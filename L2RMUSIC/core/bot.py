
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
            in_memory=False,
            workdir=".",
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
                exit(1)
            except Exception as ex:
                LOGGER(__name__).error(f"Unexpected login error: {type(ex).__name__} - {ex}")
                exit(1)

        # ---------- SET BOT IDENTITY ----------
        self.id = self.me.id
        self.name = self.me.first_name + (" " + self.me.last_name if self.me.last_name else "")
        self.username = self.me.username
        self.mention = self.me.mention

        # ---------- WARM UP PEER CACHE ----------
        try:
            LOGGER(__name__).info("🔄 Warming up peer cache via get_dialogs()...")
            async for _ in self.get_dialogs():
                pass
            LOGGER(__name__).info("✅ Peer cache warmed up.")
        except Exception as ex:
            LOGGER(__name__).warning(f"⚠️ get_dialogs() warmup failed: {type(ex).__name__} - {ex}")

        # ---------- NORMALIZE LOGGER_ID SAFELY ----------
        logger_id_raw = getattr(config, "LOGGER_ID", None)
        self.logger_id = None

        if logger_id_raw is not None:
            try:
                logger_id_raw = int(logger_id_raw)
                resolved_id = await self._resolve_chat_id(logger_id_raw)
                if resolved_id is not None:
                    self.logger_id = resolved_id
                    LOGGER(__name__).info(f"✅ Log channel resolved to: {self.logger_id}")
                else:
                    LOGGER(__name__).warning(f"⚠️ Could not resolve LOGGER_ID: {logger_id_raw}. Skipping log messages.")
            except Exception as ex:
                LOGGER(__name__).warning(f"⚠️ Error processing LOGGER_ID: {ex}. Skipping log messages.")
        else:
            LOGGER(__name__).warning("⚠️ LOGGER_ID is not set in config. Skipping log messages.")

        # ---------- SEND STARTUP MESSAGE SAFELY (WITHOUT CRASHING) ----------
        if self.logger_id:
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
                except Exception as ex:
                    LOGGER(__name__).warning(
                        f"⚠️ Bot has failed to send startup message to the log group: {ex}. Continuing startup..."
                    )
                    break

        # ---------- CHECK ADMIN STATUS SAFELY ----------
        if self.logger_id:
            try:
                member = await self.get_chat_member(self.logger_id, self.id)
                if member.status != ChatMemberStatus.ADMINISTRATOR:
                    LOGGER(__name__).warning("⚠️ Bot is not an admin in the log group/channel.")
                else:
                    LOGGER(__name__).info("✅ Bot is admin in log channel.")
            except Exception as ex:
                LOGGER(__name__).warning(f"⚠️ Failed to check admin status in log channel: {ex}")

        LOGGER(__name__).info(f"✅ Music Bot Started as {self.name}")

    async def stop(self):
        LOGGER(__name__).info("Stopping Bot...")
        await super().stop()

    # ---------- HELPER TO RESOLVE CHAT ID ----------
    async def _resolve_chat_id(self, chat_id: int):
        try:
            await self.get_chat(chat_id)
            return chat_id
        except ValueError:
            if chat_id > 0:
                negative_id = -chat_id
                LOGGER(__name__).info(
                    f"🔁 Positive ID {chat_id} failed. Trying negative: {negative_id}"
                )
                try:
                    await self.get_chat(negative_id)
                    return negative_id
                except Exception:
                    pass
            return None
        except Exception:
            return None
