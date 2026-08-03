import re
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  1.  अनिवार्य वेरिएबल्स (इन्हें सेट करना ही होगा)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

API_ID = getenv("API_ID")
if not API_ID:
    raise SystemExit("[ERROR] - API_ID is not set. Get it from my.telegram.org/apps")
try:
    API_ID = int(API_ID)
except ValueError:
    raise SystemExit("[ERROR] - API_ID must be an integer.")

API_HASH = getenv("API_HASH")
if not API_HASH:
    raise SystemExit("[ERROR] - API_HASH is not set. Get it from my.telegram.org/apps")

BOT_TOKEN = getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise SystemExit("[ERROR] - BOT_TOKEN is not set. Get it from @BotFather.")

MONGO_DB_URI = getenv("MONGO_DB_URI")
if not MONGO_DB_URI:
    raise SystemExit("[ERROR] - MONGO_DB_URI is not set. Get it from MongoDB Atlas.")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  2.  LOGGER_ID – अब सुरक्षित (safe) बना दिया गया है
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_raw_logger = getenv("LOGGER_ID")
if _raw_logger and _raw_logger.strip():
    try:
        LOGGER_ID = int(_raw_logger)
    except ValueError:
        LOGGER_ID = None
        print("⚠️  WARNING: LOGGER_ID is invalid (not an integer). Logging to channel disabled.")
else:
    LOGGER_ID = None   # खाली छोड़ने पर लॉगिंग बंद

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  3.  बाकी सभी वैकल्पिक वेरिएबल्स (डिफ़ॉल्ट के साथ)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", "5400"))
SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", "5400"))

OWNER_ID = int(getenv("OWNER_ID", "5820831398"))

HEROKU_APP_NAME = getenv("HEROKU_APP_NAME", "")
HEROKU_API_KEY = getenv("HEROKU_API_KEY", "")

UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/OnlyRoohi/istu")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "master")
GIT_TOKEN = getenv("GIT_TOKEN", None)

YTPROXY_URL = getenv("YTPROXY_URL", "https://tgapi.xbitcode.com")
YT_API_KEY = getenv("YT_API_KEY", "xbit_GjLUhA7Xsu_5Dr_xBdFZLr8LzorcKIkK")

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "")

AUTO_LEAVING_ASSISTANT = getenv("AUTO_LEAVING_ASSISTANT", "False").lower() == "true"
AUTO_SUGGESTION_MODE = getenv("AUTO_SUGGESTION_MODE", "False").lower() == "true"
AUTO_SUGGESTION_TIME = int(getenv("AUTO_SUGGESTION_TIME", "5400"))

SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "bcfe26b0ebc3428882a0b5fb3e872473")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "907c6a054c214005aeae1fd752273cc4")

PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", "25"))
CLEANMODE_DELETE_MINS = int(getenv("CLEANMODE_MINS", "5"))

TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", "104857600"))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", "1073741824"))

STRING1 = getenv("STRING_SESSION", "")
STRING2 = getenv("STRING_SESSION2", "")
STRING3 = getenv("STRING_SESSION3", "")
STRING4 = getenv("STRING_SESSION4", "")
STRING5 = getenv("STRING_SESSION5", "")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  4.  इमेज URLs (डिफ़ॉल्ट)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DEFAULT_IMG = "https://telegra.ph/file/e576aa8308c49d945f433.jpg"
START_IMG_URL = getenv("START_IMG_URL", DEFAULT_IMG)
PING_IMG_URL = getenv("PING_IMG_URL", DEFAULT_IMG)
PLAYLIST_IMG_URL = DEFAULT_IMG
STATS_IMG_URL = DEFAULT_IMG
TELEGRAM_AUDIO_URL = DEFAULT_IMG
TELEGRAM_VIDEO_URL = DEFAULT_IMG
STREAM_IMG_URL = DEFAULT_IMG
SOUNCLOUD_IMG_URL = DEFAULT_IMG
YOUTUBE_IMG_URL = DEFAULT_IMG
SPOTIFY_ARTIST_IMG_URL = DEFAULT_IMG
SPOTIFY_ALBUM_IMG_URL = DEFAULT_IMG
SPOTIFY_PLAYLIST_IMG_URL = DEFAULT_IMG

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  5.  हेल्पर फंक्शन और डेरिवेटिव वेरिएबल्स
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def time_to_seconds(time: str) -> int:
    parts = time.split(":")
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(parts)))

DURATION_LIMIT = time_to_seconds(f"{DURATION_LIMIT_MIN}:00")
SONG_DOWNLOAD_DURATION_LIMIT = time_to_seconds(f"{SONG_DOWNLOAD_DURATION}:00")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  6.  URL वैलिडेशन – अब केवल तभी जब URL सेट हो
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if SUPPORT_CHANNEL:
    if not re.match(r"(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit("[ERROR] - SUPPORT_CHANNEL URL must start with https://")
if SUPPORT_CHAT:
    if not re.match(r"(?:http|https)://", SUPPORT_CHAT):
        raise SystemExit("[ERROR] - SUPPORT_CHAT URL must start with https://")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  7.  बाकी ग्लोबल वेरिएबल्स (बॉट स्टेट)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}
chatstats = {}
userstats = {}
clean = {}
