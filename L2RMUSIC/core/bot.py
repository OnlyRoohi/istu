import asyncio
from pyrogram import Client, errors
from pyrogram.enums import ChatMemberStatus, ParseMode

import config
from ..logging import LOGGER


class Ashish(Client):
    def __init__(self):
        LOGGER(__name__).info("Starting Bot...")
        super().__init__(
            name="L2RMUSIC",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            parse_mode=ParseMode.HTML,
            max_concurrent_transmissions=7,
        )

    async def start(self):
        LOGGER(__name__).info("Attempting to connect to Telegram...")

        # ---------- LOGIN WITH RETRY ON FLOODWAIT ----------
        while True:
            try:
                await super().start()
                break
            except errors.FloodWait as e:
                wait_time = e.value
                LOGGER(__name__).warning(
                    f"⚠️ FloodWait during login. Waiting {wait_time}s..."
                )
                await asyncio.sleep(wait_time)
            except (ValueError, errors.AuthKeyUnregistered, errors.BotMethodInvalid, errors.BadRequest) as ex:
                LOGGER(__name__).error(
                    f"❌ Fatal Login Error! Check BOT_TOKEN, API_ID, API_HASH.\n  Reason: {type(ex).__name__} - {ex}"
                )
                exit(1)  # ✅ यहाँ exit ज़रूरी है क्योंकि बिना लॉगिन के बॉट आगे नहीं चल सकता
            except Exception as ex:
                LOGGER(__name__).error(f"Unexpected login error: {type(ex).__name__} - {ex}")
                exit(1)

        # ---------- SET BOT IDENTITY ----------
        self.id = self.me.id
        self.name = self.me.first_name + (" " + self.me.last_name if self.me.last_name else "")
        self.username = self.me.username
        self.mention = self.me.mention

        # ---------- NORMALIZE AND RESOLVE LOGGER_ID ----------
        self.logger_id = None  # default: disabled
        logger_id_raw = getattr(config, "LOGGER_ID", None)

        if logger_id_raw is None:
            LOGGER(__name__).warning("⚠️ LOGGER_ID not set. Telegram logging disabled.")
        else:
            try:
                logger_id_raw = int(logger_id_raw)
            except (ValueError, TypeError):
                LOGGER(__name__).error(f"❌ LOGGER_ID must be integer, got {logger_id_raw}")
            else:
                resolved = await self._resolve_chat_id(logger_id_raw)
                if resolved is None:
                    LOGGER(__name__).warning(
                        f"⚠️ Could not resolve LOGGER_ID: {logger_id_raw}. Telegram logging disabled."
                    )
                else:
                    self.logger_id = resolved
                    LOGGER(__name__).info(f"✅ Log channel resolved to: {self.logger_id}")

        # ---------- SEND STARTUP MESSAGE (IF LOGGER_ID VALID) ----------
        if self.logger_id is not None:
            try:
                await self.send_message(
                    chat_id=self.logger_id,
                    text=(
                        f"<u><b>» {self.mention} ʙᴏᴛ sᴛᴀʀᴛᴇᴅ :</b></u>\n\n"
                        f"ɪᴅ : <code>{self.id}</code>\n"
                        f"ɴᴀᴍᴇ : {self.name}\n"
                        f"ᴜsᴇʀɴᴀᴍᴇ : @{self.username}"
                    ),
                )
                LOGGER(__name__).info("✅ Startup message sent successfully.")
            except errors.FloodWait as e:
                LOGGER(__name__).warning(f"⚠️ FloodWait: waiting {e.value}s then retrying...")
                await asyncio.sleep(e.value)
                try:
                    await self.send_message(
                        chat_id=self.logger_id,
                        text=(
                            f"<u><b>» {self.mention} ʙᴏᴛ sᴛᴀʀᴛᴇᴅ :</b></u>\n\n"
                            f"ɪᴅ : <code>{self.id}</code>\n"
                            f"ɴᴀᴍᴇ : {self.name}\n"
                            f"ᴜsᴇʀɴᴀᴍᴇ : @{self.username}"
                        ),
                    )
                    LOGGER(__name__).info("✅ Startup message sent after floodwait.")
                except Exception as ex:
                    LOGGER(__name__).error(f"❌ Retry failed: {type(ex).__name__} - {ex}")
                    self.logger_id = None  # disable logging for now
            except (errors.ChannelInvalid, errors.PeerIdInvalid, ValueError) as ex:
                LOGGER(__name__).error(
                    f"❌ Cannot access log group: {type(ex).__name__} - {ex}. "
                    "Telegram logging disabled."
                )
                self.logger_id = None
            except Exception as ex:
                LOGGER(__name__).error(
                    f"❌ Failed to send startup message: {type(ex).__name__} - {ex}. "
                    "Telegram logging disabled."
                )
                self.logger_id = None

        # ---------- CHECK ADMIN STATUS (ONLY IF LOGGER_ID VALID) ----------
        if self.logger_id is not None:
            try:
                member = await self.get_chat_member(self.logger_id, self.id)
                if member.status != ChatMemberStatus.ADMINISTRATOR:
                    LOGGER(__name__).warning(
                        "⚠️ Bot is not an admin in the log group. Some features may be limited."
                    )
                else:
                    LOGGER(__name__).info("✅ Bot is admin in log channel.")
            except Exception as ex:
                LOGGER(__name__).warning(
                    f"⚠️ Could not check admin status: {type(ex).__name__} - {ex}"
                )

        LOGGER(__name__).info(f"✅ Music Bot Started as {self.name}")

    async def stop(self):
        LOGGER(__name__).info("Stopping Bot...")
        await super().stop()

    # ---------- HELPER TO RESOLVE CHAT ID (IMPROVED) ----------
    async def _resolve_chat_id(self, chat_id: int):
        """
        Tries multiple variants of the chat ID to find a working one.
        Returns the working ID or None if all fail.
        """
        variants = set()

        # Add original and its negative
        variants.add(chat_id)
        variants.add(-chat_id)

        # If ID starts with -100, try stripping it (convert to normal group ID)
        if chat_id < 0 and str(chat_id).startswith("-100"):
            stripped = int(str(chat_id)[4:])  # remove -100 prefix
            variants.add(-stripped)           # keep negative sign
            variants.add(stripped)            # also try positive

        # If ID is positive large number, try with -100 prefix
        if chat_id > 0 and chat_id > 1000000000:
            # add -100 + original (convert to supergroup ID)
            supergroup_id = -100 * 10**len(str(chat_id)) + chat_id
            variants.add(supergroup_id)

        # Try each variant
        for variant in variants:
            try:
                await self.get_chat(variant)
                return variant
            except (errors.PeerIdInvalid, errors.ChannelInvalid, ValueError):
                continue
            except Exception:
                continue

        return None
