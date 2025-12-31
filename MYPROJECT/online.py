
import os
import sys
import time
import json
import logging
import traceback
import requests

# CONFIG

APP_LIST_FILE = "steam_applist_cache.json"
APP_LIST_TTL = 24 * 3600  # 24 години

STEAMSPY_APPLIST_URL = "https://steamspy.com/api.php?request=all"

STEAM_CURRENT_PLAYERS_URL = (
    "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
)

LOG_FILE = "online.log"

# LOGGING

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

log = logging.getLogger("steam-online")

# FUNCTIONS

def load_app_list():
    log.info("Завантаження списку ігор через SteamSpy")

    if os.path.exists(APP_LIST_FILE):
        try:
            age = time.time() - os.path.getmtime(APP_LIST_FILE)
            if age < APP_LIST_TTL:
                log.info("Використовується кеш applist")
                with open(APP_LIST_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            log.exception("Помилка читання кешу applist")

    try:
        log.info("Запит SteamSpy applist")
        r = requests.get(STEAMSPY_APPLIST_URL, timeout=30)
        r.raise_for_status()

        data = r.json()  # dict {appid: {...}}
        apps = []

        for appid, info in data.items():
            name = info.get("name")
            if name:
                apps.append({
                    "appid": int(appid),
                    "name": name
                })

        if not apps:
            raise RuntimeError("SteamSpy повернув порожній список")

        with open(APP_LIST_FILE, "w", encoding="utf-8") as f:
            json.dump(apps, f, ensure_ascii=False)

        log.info("Applist отримано: %s ігор", len(apps))
        return apps

    except Exception:
        log.exception("Помилка отримання applist зі SteamSpy")
        return []


def search_apps(apps, query, limit=20):
    q = query.lower()
    return [a for a in apps if q in a["name"].lower()][:limit]


def get_current_players(appid):
    try:
        r = requests.get(
            STEAM_CURRENT_PLAYERS_URL,
            params={"appid": appid},
            timeout=10,
        )
        r.raise_for_status()
        return r.json().get("response", {}).get("player_count")
    except Exception:
        log.exception("Помилка Steam API players (appid=%s)", appid)
        return None

# MAIN

def main():
    log.info("=== START PROGRAM ===")

    apps = load_app_list()
    if not apps:
        log.error("Список ігор порожній. Вихід.")
        return

    while True:
        query = input("\nВведіть назву гри (q — вихід): ").strip()
        if query.lower() == "q":
            break

        results = search_apps(apps, query)
        if not results:
            print("Нічого не знайдено")
            continue

        for i, a in enumerate(results, 1):
            print(f"{i}. {a['name']} (appid: {a['appid']})")

        sel = input("Оберіть номер гри: ").strip()
        if not sel.isdigit():
            print("Невірний ввід")
            continue

        idx = int(sel) - 1
        if idx < 0 or idx >= len(results):
            print("Невірний номер")
            continue

        app = results[idx]
        appid = app["appid"]

        print(f"\n=== {app['name']} ===")

        players = get_current_players(appid)
        print("Current players:", players if players is not None else "N/A")

# ENTRY POINT

if __name__ == "__main__":
    try:
        main()
    except Exception:
        log.critical("FATAL ERROR")
        traceback.print_exc()
    finally:
        input("\nНатисніть Enter для виходу...")