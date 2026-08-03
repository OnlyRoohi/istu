import sys
import asyncio
from pyrogram import Client
from pyrogram.errors import PeerIdInvalid, FloodWait
import config
from ..logging import LOGGER

assistants = []
assistantids = []

class Userbot(Client):
    def __init__(self):
        self.one = Client(
            name="L2RMUSICAss1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
            no_updates=True,
        )
        self.two = Client(
            name="L2RMUSICAss2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
            no_updates=True,
        )
        self.three = Client(
            name="L2RMUSICAss3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
            no_updates=True,
        )
        self.four = Client(
            name="L2RMUSICAss4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
            no_updates=True,
        )
        self.five = Client(
            name="L2RMUSICAss5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
            no_updates=True,
        )

    async def start(self):
        LOGGER(__name__).info("Getting Assistants Info...")

        # 🚨 MAIN FIX: Naming strictly set to Integers (1, 2, 3). 
        # Plugins rely on these integers to play music!
        assistants_config = [
            (self.one, config.STRING1, 1),
            (self.two, config.STRING2, 2),
            (self.three, config.STRING3, 3),
            (self.four, config.STRING4, 4),
            (self.five, config.STRING5, 5),
        ]

        for client, session_string, name in assistants_config:
            if not session_string:
                continue

            try:
                await client.start()

                # Force join channels
                try:
                    await client.join_chat("BWF_MUSIC1")
                    await client.join_chat("MUSICBOT_OWNER")
                except Exception:
                    pass 

                get_me = await client.get_me()
                client.username = get_me.username
                client.id = get_me.id
                client.name = get_me.first_name + (" " + get_me.last_name if get_me.last_name else "")

                # Storing properly for music plugins
                assistants.append(name)
                assistantids.append(get_me.id)

                LOGGER(__name__).info(f"Assistant {name} Started as {client.name}")

                if config.LOGGER_ID: 
                    try:
                        await client.send_message(
                            config.LOGGER_ID,
                            f"**» ᴀssɪsᴛᴀɴᴛ {name} sᴛᴀʀᴛᴇᴅ :**\n\n"
                            f"✨ ɪᴅ : `{client.id}`\n"
                            f"❄ ɴᴀᴍᴇ : {client.name}\n"
                            f"💫 ᴜsᴇʀɴᴀᴍᴇ : @{client.username}"
                        )
                    except PeerIdInvalid:
                        # Crash bypass lag gaya hai!
                        LOGGER(__name__).warning(
                            f"Assistant {name} log message skipped due to Cache (Peer id invalid). Bypass activated - Bot will not crash!"
                        )
                    except FloodWait as e:
                        LOGGER(__name__).warning(f"FloodWait! Assistant {name} sleeping for {e.value} seconds.")
                        await asyncio.sleep(e.value)
                    except Exception as e:
                        LOGGER(__name__).warning(f"Assistant {name} log message skipped. Reason: {e}")
                else:
                    LOGGER(__name__).info(f"LOGGER_ID not set, skipping log message for Assistant {name}")

            except Exception as e:
                LOGGER(__name__).error(f"Assistant {name} failed to start. Reason: {e}")

        if not assistants:
            LOGGER(__name__).critical("No assistant accounts started. Bot cannot function without assistant.")
            sys.exit(1)
        else:
            LOGGER(__name__).info(f"Total {len(assistants)} assistants started successfully.")
            
