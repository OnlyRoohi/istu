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

        # ---------- LOGIN (यहाँ exit केवल लॉगिन फेल पर) ----------
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
                exit(1)  # ✅ बिना लॉगिन बॉट नहीं चल सकता – यह एकमात्र exit है
            except Exception as ex:
                LOGGER(__name__).error(f"Unexpected login error: {type(ex).__name__} - {ex}")
                exit(1)

        # ---------- बॉट की पहचान ----------
        self.id = self.me.id
        self.name = self.me.first_name + (" " + self.me.last_name if self.me.last_name else "")
        self.username = self.me.username
        self.mention = self.me.mention

        # ---------- LOGGER_ID को वैलिडेट करें (बिना क्रैश के) ----------
        self.logger_id = None  # डिफ़ॉल्ट: बंद
        logger_id_raw = getattr(config, "LOGGER_ID", None)

        if logger_id_raw is None:
            LOGGER(__name__).warning("⚠️ LOGGER_ID not set. Telegram logging disabled.")
        else:
            try:
                logger_id = int(logger_id_raw)
            except (ValueError, TypeError):
                LOGGER(__name__).error(f"❌ LOGGER_ID must be integer, got {logger_id_raw}")
                logger_id = None

            if logger_id is not None:
                # केवल एक बार get_chat करके देखें – अगर चल गया तो ID सही है
                try:
                    await self.get_chat(logger_id)
                    self.logger_id = logger_id
                    LOGGER(__name__).info(f"✅ Log channel resolved to: {self.logger_id}")
                except (errors.PeerIdInvalid, errors.ChannelInvalid, ValueError) as e:
                    LOGGER(__name__).warning(
                        f"⚠️ LOGGER_ID {logger_id} is invalid or bot not added. "
                        f"Telegram logging disabled. ({type(e).__name__})"
                    )
                except Exception as e:
                    LOGGER(__name__).warning(
                        f"⚠️ Failed to validate LOGGER_ID {logger_id}: {type(e).__name__} - {e}. "
                        "Telegram logging disabled."
                    )

        # ---------- स्टार्टअप मैसेज भेजें (अगर logger_id मान्य है) ----------
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
                    self.logger_id = None  # लॉगिंग बंद करें
            except (errors.ChannelInvalid, errors.PeerIdInvalid, ValueError) as ex:
                LOGGER(__name__).error(
                    f"❌ Cannot access log group: {type(ex).__name__} - {ex}. Disabling logging."
                )
                self.logger_id = None
            except Exception as ex:
                LOGGER(__name__).error(
                    f"❌ Failed to send startup message: {type(ex).__name__} - {ex}. Disabling logging."
                )
                self.logger_id = None

        # ---------- एडमिन स्टेटस चेक (अगर logger_id मान्य है) ----------
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
