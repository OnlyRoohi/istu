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
        
        # लॉगिन के लिए रिट्राई लूप (FloodWait हैंडलिंग)
        while True:
            try:
                await super().start()
                break
            except errors.FloodWait as e:
                wait_time = e.value
                LOGGER(__name__).warning(
                    f"⚠️ Telegram FloodWait during login. Waiting for {wait_time} seconds before retrying..."
                )
                await asyncio.sleep(wait_time)
            except (ValueError, errors.AuthKeyUnregistered, errors.BotMethodInvalid, errors.BadRequest) as ex:
                LOGGER(__name__).error(
                    f"❌ Fatal Login Error! Please check your BOT_TOKEN, API_ID, and API_HASH.\n  Reason: {type(ex).__name__} - {ex}"
                )
                exit(1)
            except Exception as ex:
                LOGGER(__name__).error(
                    f"Bot failed to start due to an unexpected error: {type(ex).__name__} - {ex}"
                )
                exit(1)
        
        # बॉट की डिटेल्स सेट करें
        self.id = self.me.id
        self.name = self.me.first_name + " " + (self.me.last_name or "")
        self.username = self.me.username
        self.mention = self.me.mention

        # ---------- लॉग चैनल सेटअप (संशोधित) ----------
        # यह मान लें कि LOGGER_ID शून्य या गलत हो सकता है
        if not config.LOGGER_ID:
            LOGGER(__name__).warning("LOGGER_ID is not set. Skipping log channel setup.")
        else:
            try:
                # 1. स्टार्टअप मैसेज भेजने की कोशिश
                await self.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"<u><b>» {self.mention} ʙᴏᴛ sᴛᴀʀᴛᴇᴅ :</b><u>\n\nɪᴅ : <code>{self.id}</code>\nɴᴀᴍᴇ : {self.name}\nᴜsᴇʀɴᴀᴍᴇ : @{self.username}",
                )
                # 2. अगर मैसेज सफलतापूर्वक भेजा, तो एडमिन चेक करें
                try:
                    a = await self.get_chat_member(config.LOGGER_ID, self.id)
                    if a.status != ChatMemberStatus.ADMINISTRATOR:
                        LOGGER(__name__).error(
                            "Please promote your bot as an admin in your log group/channel."
                        )
                        exit(1)   # एडमिन न होने पर बॉट बंद करें (यदि चाहें तो हटा सकते हैं)
                except Exception as admin_ex:
                    LOGGER(__name__).error(
                        f"Failed to check bot's admin status in the log group/channel.\n  Reason: {type(admin_ex).__name__} - {admin_ex}."
                    )
                    exit(1)   # एडमिन चेक फेल होने पर भी बंद करें (या स्किप करें)

            except (errors.ChannelInvalid, errors.PeerIdInvalid) as peer_ex:
                # ID गलत होने पर सिर्फ वार्निंग दें, बॉट को बंद न करें
                LOGGER(__name__).warning(
                    f"Log channel ID ({config.LOGGER_ID}) is invalid or inaccessible. "
                    f"Bot will continue without log channel.\n  Reason: {type(peer_ex).__name__} - {peer_ex}."
                )
                # एडमिन चेक न करें, आगे बढ़ें
            except Exception as ex:
                # कोई और अप्रत्याशित एरर – उसे भी वार्निंग मानकर आगे बढ़ें
                LOGGER(__name__).warning(
                    f"Failed to send startup message to log channel. Continuing without it.\n  Reason: {type(ex).__name__} - {ex}."
                )

        LOGGER(__name__).info(f"Music Bot Started as {self.name}")

    async def stop(self):
        LOGGER(__name__).info("Stopping Bot...")
        await super().stop()
