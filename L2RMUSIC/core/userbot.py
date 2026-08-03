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

        # सभी असिस्टेंट्स को एक लिस्ट में डालें
        assistants_config = [
            (self.one, config.STRING1, "One"),
            (self.two, config.STRING2, "Two"),
            (self.three, config.STRING3, "Three"),
            (self.four, config.STRING4, "Four"),
            (self.five, config.STRING5, "Five"),
        ]

        for client, session_string, name in assistants_config:
            # अगर सेशन स्ट्रिंग खाली है, तो इस असिस्टेंट को स्किप करें
            if not session_string:
                continue

            try:
                # 1. असिस्टेंट स्टार्ट करें
                await client.start()

                # 2. चैनल ज्वाइन करने की कोशिश करें (अगर फेल हो तो कोई बात नहीं)
                try:
                    await client.join_chat("BWF_MUSIC1")
                    await client.join_chat("MUSICBOT_OWNER")
                except Exception:
                    pass  # ज्वाइन न हो तो आगे बढ़ें

                # 3. असिस्टेंट की डिटेल्स लें
                get_me = await client.get_me()
                client.username = get_me.username
                client.id = get_me.id
                client.name = get_me.first_name + (" " + get_me.last_name if get_me.last_name else "")

                # 4. ग्लोबल लिस्ट में सेव करें
                assistants.append(name)
                assistantids.append(get_me.id)

                LOGGER(__name__).info(f"Assistant {name} Started as {client.name}")

                # 5. लॉग ग्रुप में स्टार्टअप मैसेज भेजें (अब बिना किसी डर के)
                if config.LOGGER_ID:  # अगर LOGGER_ID सेट है
                    try:
                        await client.send_message(
                            config.LOGGER_ID,
                            f"**» ᴀssɪsᴛᴀɴᴛ {name.lower()} sᴛᴀʀᴛᴇᴅ :**\n\n"
                            f"✨ ɪᴅ : `{client.id}`\n"
                            f"❄ ɴᴀᴍᴇ : {client.name}\n"
                            f"💫 ᴜsᴇʀɴᴀᴍᴇ : @{client.username}"
                        )
                    except Exception as e:
                        # 🚨 यहाँ sys.exit() नहीं होगा, सिर्फ वार्निंग लॉग होगी!
                        LOGGER(__name__).warning(
                            f"Assistant {name} could not send startup message to log channel. "
                            f"Reason: {type(e).__name__} - {e}"
                        )
                else:
                    LOGGER(__name__).info(f"LOGGER_ID not set, skipping log message for Assistant {name}")

            except Exception as e:
                # अगर असिस्टेंट स्टार्ट ही नहीं हो पाया (जैसे गलत सेशन)
                LOGGER(__name__).error(f"Assistant {name} failed to start. Reason: {e}")

        # 6. चेक करें कि कम से कम एक असिस्टेंट तो चालू हुआ है
        if not assistants:
            LOGGER(__name__).critical("No assistant accounts started. Bot cannot function without assistant.")
            sys.exit(1)  # यहाँ exit होना सही है, क्योंकि बिना असिस्टेंट के बॉट काम नहीं करेगा
        else:
            LOGGER(__name__).info(f"Total {len(assistants)} assistants started successfully.")
