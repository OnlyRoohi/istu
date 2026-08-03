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
                exit(1)  # Login fatal error – यहाँ exit रहने दें
            except Exception as ex:
                LOGGER(__name__).error(f"Unexpected login error: {type(ex).__name__} - {ex}")
                exit(1)

        # ---------- SET BOT IDENTITY ----------
        self.id = self.me.id
        self.name = self.me.first_name + (" " + self.me.last_name if self.me.last_name else "")
        self.username = self.me.username
        self.mention = self.me.mention

        # ---------- NORMALIZE LOGGER_ID ----------
        logger_id_raw = getattr(config, "LOGGER_ID", None)
        if logger_id_raw is None:
            LOGGER(__name__).warning("⚠️ LOGGER_ID is not set in config. Logging to Telegram will be disabled.")
            self.logger_id = None
        else:
            # Convert to int if string
            try:
                logger_id_raw = int(logger_id_raw)
            except (ValueError, TypeError):
                LOGGER(__name__).error(f"❌ LOGGER_ID must be an integer, got {logger_id_raw}")
                self.logger_id = None
            else:
                # Try to resolve the correct chat ID
                resolved_id = await self._resolve_chat_id(logger_id_raw)
                if resolved_id is None:
                    LOGGER(__name__).warning(
                        f"⚠️ Could not resolve LOGGER_ID: {logger_id_raw}. "
                        "Logging to Telegram will be disabled."
                    )
                    self.logger_id = None
                else:
                    self.logger_id = resolved_id
                    LOGGER(__name__).info(f"✅ Log channel resolved to: {self.logger_id}")

        # ---------- SEND STARTUP MESSAGE (IF LOGGER_ID VALID) ----------
        if self.logger_id is not None:
            while True:
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
                    break
                except errors.FloodWait as e:
                    wait_time = e.value
                    LOGGER(__name__).warning(
                        f"⚠️ FloodWait while sending startup message. Waiting {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                except (errors.ChannelInvalid, errors.PeerIdInvalid) as ex:
                    LOGGER(__name__).error(
                        "❌ Bot cannot access the log group/channel. "
                        "Logging to Telegram will be disabled."
                    )
                    self.logger_id = None  # Disable logging for this session
                    break
                except Exception as ex:
                    LOGGER(__name__).error(
                        f"❌ Failed to send startup message: {type(ex).__name__} - {ex}"
                    )
                    self.logger_id = None
                    break

        # ---------- CHECK ADMIN STATUS (ONLY IF LOGGER_ID VALID) ----------
        if self.logger_id is not None:
            try:
                member = await self.get_chat_member(self.logger_id, self.id)
                if member.status != ChatMemberStatus.ADMINISTRATOR:
                    LOGGER(__name__).warning(
                        "⚠️ Bot is not an admin in the log group/channel. "
                        "Some features may not work correctly."
                    )
                else:
                    LOGGER(__name__).info("✅ Bot is admin in log channel.")
            except Exception as ex:
                LOGGER(__name__).warning(
                    f"⚠️ Failed to check admin status: {type(ex).__name__} - {ex}"
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
        # List of possible IDs to try
        variants = [chat_id]

        # If negative, try positive (for normal groups)
        if chat_id < 0:
            variants.append(-chat_id)
        else:
            variants.append(-chat_id)

        # If it's a supergroup ID (starts with -100), try without -100
        if chat_id < 0 and str(chat_id).startswith("-100"):
            # Remove '-100' prefix and make negative (like a normal group)
            stripped = int(str(chat_id)[4:])  # e.g., -1002230309222 -> 2230309222
            variants.append(-stripped)        # -> -2230309222

        # Also try adding -100 if it's positive and large
        if chat_id > 0 and chat_id > 1000000000:
            variants.append(-100 * 10**len(str(chat_id)) + chat_id)  # not precise, skip

        # Try each variant
        for variant in set(variants):  # remove duplicates
            try:
                await self.get_chat(variant)
                return variant
            except (errors.PeerIdInvalid, errors.ChannelInvalid, ValueError):
                continue
            except Exception as e:
                LOGGER(__name__).debug(f"Error checking {variant}: {type(e).__name__} - {e}")
                continue

        return None
