import sys
from pyrogram import Client
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
        LOGGER(__name__).info("Gettings Assistants Info...")

        # 🚨 FIX 1: Names are set to Integers (1, 2, 3) so that the /play command works properly
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

                try:
                    await client.join_chat("BWF_MUSIC1")
                    await client.join_chat("MUSICBOT_OWNER")
                except Exception:
                    pass

                get_me = await client.get_me()
                client.username = get_me.username
                client.id = get_me.id
                client.name = get_me.first_name + (" " + get_me.last_name if get_me.last_name else "")

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
                    except Exception as e:
                        # 🚨 FIX 2: Removed 'sys.exit()'. Now if Telegram throws PeerIdInvalid, the bot will bypass it and start anyway!
                        LOGGER(__name__).error(
                            f"Assistant Account {name} failed to access log Group. Error: {e}. Bypassing crash..."
                        )
                        pass 
                else:
                    LOGGER(__name__).info(f"LOGGER_ID not set, skipping log message for Assistant {name}")

            except Exception as e:
                LOGGER(__name__).error(f"Assistant {name} failed to start. Reason: {e}")

        if not assistants:
            LOGGER(__name__).critical("No assistant accounts started. Bot cannot function without assistant.")
            sys.exit(1)
        else:
            LOGGER(__name__).info(f"Total {len(assistants)} assistants started successfully.")
