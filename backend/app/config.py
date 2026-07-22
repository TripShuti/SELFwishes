import os

DATA_DIR = os.environ.get("DATA_DIR") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)
DATABASE_URL = f"sqlite+aiosqlite:///{DATA_DIR}/wishes.db"

HOYO_BASE_URL = "https://hk4e-api-os.hoyoverse.com/event/gacha_info/api/getGachaLog"
HOYO_PAGE_SIZE = 20
HOYO_REQUEST_DELAY = 0.5

GACHA_TYPES = {
    "100": "Beginners' Wish",
    "200": "Standard Wish",
    "301": "Character Event Wish",
    "302": "Weapon Event Wish",
    "400": "Character Event Wish-2",
    "500": "Chronicled Wish",
}

UIGF_MERGE = {
    "100": "100",
    "200": "200",
    "301": "301",
    "302": "302",
    "400": "301",
    "500": "500",
}

GACHA_TYPE_ORDER = ["301", "302", "200", "100", "500"]

STANDARD_5_CHARS = {
    "Diluc", "Jean", "Mona", "Qiqi", "Keqing",
    "Tighnari", "Dehya", "Yumemizuki Mizuki",
}

PITY_HARD_5 = {"100": 90, "200": 90, "301": 90, "302": 80, "400": 90, "500": 90}
PITY_HARD_4 = {"100": 10, "200": 10, "301": 10, "302": 10, "400": 10, "500": 10}
