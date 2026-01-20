import requests
import random
import string
import threading
import time
import os
import re
import hashlib
import urllib.parse
from colorama import init, Fore

init()

def get_browser_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }

def get_ajax_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://godlike.host',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Referer': 'https://godlike.host/clientarea/custom-register.php',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }

def load_proxies():
    try:
        with open("proxies.txt", "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
            if proxies:
                print(Fore.YELLOW + f"[*] {len(proxies)} proxies")
            return proxies
    except:
        return []

def get_proxy(proxies, index):
    if not proxies:
        return None
    return proxies[index % len(proxies)]

def setup_session_proxy(session, proxy_str):
    if proxy_str:
        try:
            session.proxies.update({
                'http': f'socks5://{proxy_str}',
                'https': f'socks5://{proxy_str}'
            })
        except:
            pass
    return session

def create_temp_inbox(session):
    try:

        services = [

            lambda: create_temp_mail_io(session),
        ]

        for service in services:
            email = service()
            if email:
                return email
            time.sleep(1)

        return None
    except:
        return None

def create_1secmail(session):
    try:
        domains = ['1secmail.com', '1secmail.org', '1secmail.net']
        domain = random.choice(domains)
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        email = f"{username}@{domain}"
        return email
    except:
        return None

def create_temp_mail_io(session):
    try:
        url = 'https://api.internal.temp-mail.io/api/v3/email/new'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        payload = {"min_name_length": 10, "max_name_length": 10}
        response = session.post(url, headers=headers, json=payload, timeout=15)

        if response.status_code == 200:
            data = response.json()
            email = data.get('email')
            return email
        return None
    except:
        return None

def get_verification_code(session, email):
    try:

        if '1secmail' in email:
            username, domain = email.split('@')
            url = f'https://www.1secmail.com/api/v1/?action=getMessages&login={username}&domain={domain}'

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }

            response = session.get(url, headers=headers, timeout=15)

            if response.status_code == 200:
                messages = response.json()
                if isinstance(messages, list):
                    for msg in messages:
                        msg_id = msg.get('id')

                        read_url = f'https://www.1secmail.com/api/v1/?action=readMessage&login={username}&domain={domain}&id={msg_id}'
                        msg_response = session.get(read_url, headers=headers, timeout=15)

                        if msg_response.status_code == 200:
                            msg_data = msg_response.json()
                            body = msg_data.get('textBody', '') or msg_data.get('htmlBody', '')

                            pattern = r'https://godlike\.host/clientarea/user/verify/[a-f0-9]{64}'
                            match = re.search(pattern, body)
                            if match:
                                return match.group(0)

        return None
    except:
        return None

def generate_username():
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(10))

def generate_password():
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(10))

def create_account(proxies, target_accounts, accounts_created, lock, running, proxy_index_counter, use_proxies):
    while running[0]:
        with lock:
            if accounts_created[0] >= target_accounts:
                break
            proxy_index = proxy_index_counter[0]
            proxy_index_counter[0] += 1

        proxy = get_proxy(proxies, proxy_index) if use_proxies else None
        session = requests.Session()
        if proxy:
            session = setup_session_proxy(session, proxy)

        try:
            time.sleep(random.uniform(3, 7))

            print(Fore.YELLOW + "[*] creating account...")

            email = create_temp_inbox(session)
            if not email:
                print(Fore.RED + "[-] email fail")
                continue

            print(Fore.CYAN + f"[+] EMAIL: {email}")

            username = generate_username()
            password = generate_password()
            email_user = email.split('@')[0]

            data = {
                'register': 'true',
                'firstname': email_user,
                'lastname': '_',
                'email': email,
                'country': 'US',
                'currency': '1',
                'password': password,
                'password2': password,
                'accepttos': 'on'
            }

            try:
                print(Fore.YELLOW + "[*] getting cookies...")
                headers = get_browser_headers()
                session.get('https://godlike.host/', headers=headers, timeout=10)
                time.sleep(2)
            except:
                pass

            print(Fore.YELLOW + "[*] sending registration...")

            url = 'https://godlike.host/clientarea/custom-register.php'
            headers = get_ajax_headers()

            response = session.post(url, headers=headers, data=data, timeout=15)

            print(Fore.MAGENTA + f"[*] status: {response.status_code}")
            print(Fore.MAGENTA + f"[*] response length: {len(response.text)}")

            if response.status_code != 200:
                print(Fore.RED + f"[-] http fail: {response.status_code}")
                continue

            print(Fore.GREEN + f"[✓] REGISTERED")

            print(Fore.YELLOW + "[*] skipping email verify for test")

            with lock:
                if accounts_created[0] < target_accounts:
                    accounts_created[0] += 1
                    with open("godlike_accs.txt", "a") as f:
                        f.write(f"{email}:{password}:{username}\n")
                    print(Fore.GREEN + f"[✓] ACCOUNT CREATED: {email}")

        except Exception as e:
            print(Fore.RED + f"[!] ERROR: {str(e)[:50]}")

        delay = random.uniform(10, 20)
        print(Fore.CYAN + f"[*] wait {delay:.1f} sec")
        time.sleep(delay)

def main():
    os.system('cls' if os.name == 'nt' else 'clear')

    print(Fore.LIGHTYELLOW_EX + "▄▀▄▀▄ GODLIKE.HOST TEST ▄▀▄▀▄")
    print(Fore.YELLOW + "[*] Testing registration only (skip email verify)")

    proxies = []
    use_proxies = False

    use_proxy_input = input(Fore.LIGHTCYAN_EX + "Use proxies? (y/n): " + Fore.WHITE).lower()
    if use_proxy_input == 'y':
        proxies = load_proxies()
        if not proxies:
            print(Fore.RED + "[!] no proxies.txt")
            return
        use_proxies = True
        print(Fore.GREEN + "[+] PROXIES")
    else:
        print(Fore.YELLOW + "[*] NO PROXIES")

    try:
        target_accounts = int(input(Fore.LIGHTCYAN_EX + "Accounts to make: " + Fore.WHITE))
        threads_count = int(input(Fore.LIGHTCYAN_EX + "Threads: " + Fore.WHITE))
    except:
        return

    accounts_created = [0]
    running = [True]
    lock = threading.Lock()
    proxy_index_counter = [0]
    threads = []

    for i in range(threads_count):
        thread = threading.Thread(target=create_account, args=(proxies, target_accounts, accounts_created, lock, running, proxy_index_counter, use_proxies), daemon=True)
        threads.append(thread)
        thread.start()
        print(Fore.YELLOW + f"[*] Thread {i+1}")

    try:
        while any(t.is_alive() for t in threads):
            time.sleep(1)
            with lock:
                current = accounts_created[0]
            print(Fore.LIGHTMAGENTA_EX + f"\r[*] PROGRESS: {current}/{target_accounts}", end="")
            if current >= target_accounts:
                running[0] = False
                break
    except KeyboardInterrupt:
        running[0] = False
        print(Fore.RED + "\n\n[!] STOP")

    print(Fore.LIGHTGREEN_EX + f"\n\n✅ DONE: {accounts_created[0]} accounts")
    print(Fore.LIGHTBLUE_EX + f"[*] saved to godlike_accs.txt")

if __name__ == "__main__":
    main()
