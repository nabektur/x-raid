import asyncio
import json
import time
import aiohttp
import random
import requests
from datetime import datetime
from colorama import Fore, Style, init as colorama_init
import websockets
import threading
import os
import tls_client
from deep_translator import GoogleTranslator
from os.path import isfile
import uuid
import ctypes
import websocket
import string
import ssl, certifi
ssl_context = ssl.create_default_context(cafile=certifi.where())

def init():
    colorama_init() 
    pass

def read_tokens():
    if not isfile("tokens.txt"):
        open("tokens.txt", "w").close()
    with open("tokens.txt", "r") as file:
        return [token.strip() for token in file if token.strip()]

activity = {
    "name": "Spotify",
    "type": 2,
    "details": "",  
    "state": "",  
    "timestamps": {"start": int(time.time()), "end": int(time.time()) + 3600},
    "assets": {
        "large_image": "mp:stickers/1469769107686686830.gif",
        "large_text": "",  
    },
    "party": {"id": "spotify:1234567890"},
    "flags": 48,
    "sync_id": "1S0ab1Xv89UqFWU0FJjRPs",
}

def create_directory(server_id):
    directory = f"scrapes/{server_id}"
    os.makedirs(directory, exist_ok=True)
    if not isfile(f"{directory}/users.txt"):
        with open(f"{directory}/users.txt", "w") as file:
            file.write("")
    return directory

def read_users(directory):
    if not isfile(f"{directory}/users.txt"):
        open(f"{directory}/users.txt", "w").close()
    with open(f"{directory}/users.txt", "r") as file:
        return file.read().splitlines()

def save_users(user_ids, directory):
    existing_users = set(read_users(directory))
    with open(f"{directory}/users.txt", "a") as file:
        for user_id in user_ids:
            if user_id and user_id not in existing_users:
                file.write(f"{user_id}\n")

def generate_random_symbols(length=5):
    return ''.join(random.choices(string.ascii_letters, k=length))

def generate_random_emoji(length=3):
    emojis = ['😀', '😃', '😄', '😁', '😆', '😅', '😂', '🤣', '😊', '😇', '🙂', '🙃', '😉', '😌', '😍', '🥰', '😘', '😗', '😙', '😚']
    return ''.join(random.choices(emojis, k=length))

def handle_rate_limit(retry_after):
    print(f'{Fore.RED}[ ~ ] Лимит запросов превышен. Повтор через {retry_after:.2f} секунд.{Style.RESET_ALL}')
    time.sleep(retry_after)

async def send_message_with_retry_async(token, channel_id, message_text, session_id=None, use_spotify=False, retry_count=5, include_symbols="нет", include_emojis="нет", user_ids=None, num_pings=0, already_pinged=None, supported_languages=None, use_translation="нет"):
    if already_pinged is None:
        already_pinged = set()

    final_message = message_text
    if use_translation == "да" and "Windows PowerShell" not in message_text and supported_languages:
        lang = random.choice(supported_languages)
        try:
            final_message = await asyncio.to_thread(GoogleTranslator(source='auto', target=lang).translate, message_text)
        except Exception as e:
            print(f'{Fore.RED}Ошибка перевода: {e}. Использую оригинал.{Style.RESET_ALL}')
            final_message = message_text

    pings = ""
    if user_ids and num_pings > 0:
        available_users = [uid for uid in user_ids if uid not in already_pinged]
        if not available_users:
            already_pinged.clear()
            available_users = user_ids
        to_ping = random.sample(available_users, min(num_pings, len(available_users)))
        already_pinged.update(to_ping)
        pings = " ".join([f"<@{user_id}>" for user_id in to_ping])

    final_message = f"{pings} {final_message}".strip()
    if include_symbols == "да":
        symbols = f"||{generate_random_symbols()}||"
        final_message = f"{symbols} {final_message} {symbols}"
    if include_emojis == "да":
        emojis = generate_random_emoji()
        final_message = f"{final_message} {emojis}"

    async with aiohttp.ClientSession() as session:
        for attempt in range(retry_count):
            try:
                payload = {"content": final_message}
                if use_spotify and session_id:
                    payload["activity"] = {
                        "type": 3,
                        "session_id": session_id,
                        "party_id": activity["party"]["id"]  
                    }
                async with session.post(
                    f"https://discord.com/api/v9/channels/{channel_id}/messages",
                    headers={"Authorization": token, "Content-Type": "application/json"},
                    json=payload,
                    ssl=False
                ) as response:
                    if response.status == 429:
                        retry_after = float(response.headers.get("Retry-After", 1)) / 1000
                        print(f'{Fore.RED}[ + ] - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Лимит запросов, ожидание {retry_after} секунд...{Style.RESET_ALL}')
                        await asyncio.sleep(retry_after)
                        continue
                    elif response.status == 200:
                        print(f'{Fore.GREEN}[ + ] - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Отправлено: {token[:25]}... Сообщение: {final_message[:10]}...{Style.RESET_ALL}')
                        return True
                    else:
                        print(f'{Fore.RED}[ + ] - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Ошибка: {token[:25]}... Статус: {response.status}...{Style.RESET_ALL}')
                        await asyncio.sleep(0.001)
                        continue
            except aiohttp.ClientError as e:
                print(f'{Fore.RED}Ошибка сети: {e}. Повтор попытки...{Style.RESET_ALL}')
                await asyncio.sleep(0.001)
        return False

def send_message_with_retry(token, channel_id, message_text, session_id=None, use_spotify=False, retry_count=5, include_symbols="нет", include_emojis="нет", user_ids=None, num_pings=0, already_pinged=None, supported_languages=None, use_translation="нет"):
    if already_pinged is None:
        already_pinged = set()

    final_message = message_text
    if use_translation == "да" and "Windows PowerShell" not in message_text and supported_languages:
        lang = random.choice(supported_languages)
        try:
            final_message = GoogleTranslator(source='auto', target=lang).translate(message_text)
        except Exception as e:
            print(f'{Fore.RED}Ошибка перевода: {e}. Использую оригинал.{Style.RESET_ALL}')
            final_message = message_text

    pings = ""
    if user_ids and num_pings > 0:
        available_users = [uid for uid in user_ids if uid not in already_pinged]
        if not available_users:
            already_pinged.clear()
            available_users = user_ids
        to_ping = random.sample(available_users, min(num_pings, len(available_users)))
        already_pinged.update(to_ping)
        pings = " ".join([f"<@{user_id}>" for user_id in to_ping])

    final_message = f"{pings} {final_message}".strip()
    if include_symbols == "да":
        symbols = f"||{generate_random_symbols()}||"
        final_message = f"{symbols} {final_message} {symbols}"
    if include_emojis == "да":
        emojis = generate_random_emoji()
        final_message = f"{final_message} {emojis}"

    client = tls_client.Session(client_identifier="chrome_120")
    for attempt in range(retry_count):
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        headers = {'Authorization': token, 'Content-Type': 'application/json'}
        payload = {"content": final_message}
        if use_spotify and session_id:
            payload["activity"] = {
                "type": 3,
                "session_id": session_id,
                "party_id": activity["party"]["id"]  
            }
        try:
            response = client.post(url, headers=headers, json=payload)
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 1)) / 1000
                handle_rate_limit(retry_after)  
            elif response.status_code == 200:
                print(f'{Fore.GREEN}[ + ] - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Отправлено: {token[:6]}... Сообщение: {final_message[:10]}...{Style.RESET_ALL}')
                return True
            else:
                print(f'{Fore.RED}[ + ] - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Ошибка: {token[:6]}... Статус: {response.status_code}...{Style.RESET_ALL}')
                time.sleep(0.001)
        except Exception as e:
            print(f'{Fore.RED}Ошибка сети: {e}. Повтор попытки...{Style.RESET_ALL}')
            time.sleep(0.001)
    return False

async def spotify_client(token, channel_ids, message_text, use_spotify, include_symbols="нет", include_emojis="нет", user_ids=None, num_pings=0, failed_tokens=None, already_pinged=None, supported_languages=None, use_translation="нет"):
    if already_pinged is None:
        already_pinged = set()

    if not use_spotify:
        while True:
            for channel_id in channel_ids:
                await send_message_with_retry_async(
                    token, channel_id, message_text, None, False,
                    include_symbols=include_symbols, include_emojis=include_emojis,
                    user_ids=user_ids, num_pings=num_pings, already_pinged=already_pinged,
                    supported_languages=supported_languages, use_translation=use_translation
                )
            await asyncio.sleep(0.1)

    session_id = None
    resume_gateway_url = None
    seq = None

    while True:
        try:
            async with websockets.connect(
                resume_gateway_url or 'wss://gateway.discord.gg/?v=10&encoding=json',
                max_size=None,
                ssl=ssl_context
            ) as ws:
                heartbeat_task = None
                while True:
                    try:
                        data = await asyncio.wait_for(ws.recv(), timeout=60)
                        json_data = json.loads(data)
                        if json_data.get("op") == 10:
                            heartbeat_interval = json_data["d"]["heartbeat_interval"] / 1000 * 0.75
                            if heartbeat_task:
                                heartbeat_task.cancel()
                            heartbeat_task = asyncio.create_task(heartbeat(heartbeat_interval, ws, token, failed_tokens))
                            identify = {
                                "op": 2,
                                "d": {
                                    "token": token,
                                    "properties": {
                                        "$os": "Linux",
                                        "$browser": "Chrome",
                                        "$device": ""
                                    },
                                    "compress": False
                                }
                            }
                            if session_id and seq is not None:
                                identify["op"] = 6
                                identify["d"]["session_id"] = session_id
                                identify["d"]["seq"] = seq
                            await ws.send(json.dumps(identify))
                        elif json_data.get("t") == "READY" or json_data.get("t") == "RESUMED":
                            if json_data.get("t") == "READY":
                                session_id = json_data["d"]["session_id"]
                                resume_gateway_url = json_data["d"].get("resume_gateway_url", "wss://gateway.discord.gg")
                            seq = json_data.get("s", seq)
                            await ws.send(json.dumps({
                                "op": 3,
                                "d": {
                                    "since": 0,
                                    "activities": [activity],  
                                    "status": "online",
                                    "afk": False
                                }
                            }))
                            while True:
                                for channel_id in channel_ids:
                                    translated_message = message_text
                                    if use_translation == "да" and "Windows PowerShell" not in message_text and supported_languages:
                                        lang = random.choice(supported_languages)
                                        try:
                                            translated_message = await asyncio.to_thread(GoogleTranslator(source='auto', target=lang).translate, message_text)
                                        except Exception as e:
                                            print(f'{Fore.RED}Ошибка перевода: {e}. Использую оригинал.{Style.RESET_ALL}')
                                            translated_message = message_text

                                    success = await send_message_with_retry_async(
                                        token, channel_id, translated_message, session_id, True,
                                        retry_count=20,
                                        include_symbols=include_symbols, include_emojis=include_emojis,
                                        user_ids=user_ids, num_pings=num_pings, already_pinged=already_pinged,
                                        supported_languages=supported_languages, use_translation="нет"  
                                    )
                                    if success:
                                        await asyncio.sleep(0.3)
                                    else:
                                        await asyncio.sleep(2)
                        elif json_data.get("op") == 7:
                            print(f'{Fore.RED}Переподключение для {token[:25]}...{Style.RESET_ALL}')
                            break
                        elif json_data.get("op") == 9:
                            if json_data["d"]:
                                print(f'{Fore.RED}Сессия невалидна, но восстанавливаем. Жду 5 сек...{Style.RESET_ALL}')
                                await asyncio.sleep(5)
                                break
                            else:
                                print(f'{Fore.RED}Сессия невалидна полностью для {token[:25]}. Сбрасываем сессию...{Style.RESET_ALL}')
                                session_id = None
                                seq = None
                                resume_gateway_url = None
                                await asyncio.sleep(10)
                                break
                        elif json_data.get("op") == 11:
                            continue
                        seq = json_data.get("s", seq)
                    except asyncio.TimeoutError:
                        print(f'{Fore.RED}Таймаут приема данных для {token[:25]}. Переподключение...{Style.RESET_ALL}')
                        break
                    except websockets.exceptions.ConnectionClosedError as e:
                        print(f'{Fore.RED}Соединение закрыто: {e}. Переподключение через 3 сек...{Style.RESET_ALL}')
                        await asyncio.sleep(3)
                        break
                    except Exception as e:
                        print(f'{Fore.RED}Ошибка в обработке данных: {e}. Переподключение через 3 сек...{Style.RESET_ALL}')
                        await asyncio.sleep(3)
                        break
                if heartbeat_task:
                    heartbeat_task.cancel()
        except Exception as e:
            print(f'{Fore.RED}Ошибка подключения: {e}. Пробую снова через 3 сек...{Style.RESET_ALL}')
            await asyncio.sleep(3)

async def run_all_spam_tasks(tokens, channel_ids, message_text, user_ids, num_pings, include_symbols, include_emojis, supported_languages, use_translation, use_spotify):
    already_pinged = set()
    failed_tokens = set()
    if isinstance(user_ids, dict):
        user_ids = list(user_ids.keys())
    elif isinstance(user_ids, set):
        user_ids = list(user_ids)

    while True:
        tasks = []
        for token in tokens:
            if token in failed_tokens:
                continue

            if use_spotify:
                tasks.append(spotify_client(
                    token, channel_ids, message_text, use_spotify,
                    include_symbols=include_symbols, include_emojis=include_emojis,
                    user_ids=user_ids, num_pings=num_pings, failed_tokens=failed_tokens, already_pinged=already_pinged,
                    supported_languages=supported_languages, use_translation=use_translation
                ))
            else:
                tasks.extend([
                    send_message_with_retry_async(
                        token, channel_id, message_text, include_symbols=include_symbols,
                        include_emojis=include_emojis, user_ids=user_ids, num_pings=num_pings, already_pinged=already_pinged,
                        supported_languages=supported_languages, use_translation=use_translation
                    ) for channel_id in channel_ids
                ])
        await asyncio.gather(*tasks, return_exceptions=True)
        if len(already_pinged) >= len(user_ids) and user_ids:
            already_pinged.clear()
        await asyncio.sleep(0.1)

class DiscordSocket:
    def __init__(self, token, server_id, channel_id):
        self.token = token
        self.server_id = server_id
        self.channel_id = channel_id
        self.base_url = "https://discord.com/api/v9"

    def fetch_users(self):
        return []

    def run(self):
        return self.fetch_users()

def run_scrape(token, server_id, channel_id):
    sb = DiscordSocket(token, server_id, channel_id)
    return sb.run()

def main():
    init()  
    tokens = read_tokens()
    if not tokens:
        print(f'{Fore.RED}Ошибка: tokens.txt пуст или не существует.{Style.RESET_ALL}')
        return

    while True: 
        server_id = input(Fore.RED + "Введите идентификатор сервера: " + Style.RESET_ALL).strip()
        channel_ids = [cid.strip() for cid in input(Fore.RED + "Введите идентификатор канала: " + Style.RESET_ALL).split(',') if cid.strip()]
        if not channel_ids:
            print(Fore.RED + "Ошибка: не указан идентификатор канала." + Style.RESET_ALL)
            continue
        else:
            break

    directory = create_directory(server_id)
    
    scrap_users = input(Fore.RED + "Пинговать ли пользователей для массового пинга? (да/нет): " + Style.RESET_ALL).strip().lower()
    include_symbols = input(Fore.RED + "Включать случайные символы вокруг сообщения? (да/нет): " + Style.RESET_ALL).strip().lower()
    include_emojis = input(Fore.RED + "Включать разные эмодзи в конце текста? (да/нет): " + Style.RESET_ALL).strip().lower()
    use_translation = input(Fore.RED + "Переводить сообщения на разные языки? (да/нет): " + Style.RESET_ALL).strip().lower()
    use_spotify = input(Fore.RED + "Включить спам с активностью Spotify? (да/нет): " + Style.RESET_ALL).strip().lower() == "да"
    
    if use_spotify:
        activity["details"] = input(Fore.RED + "Введите текст для Spotify (например, URL или описание): " + Style.RESET_ALL).strip() or "https://discord.gg/jNDea8rtPq"
        activity["state"] = input(Fore.RED + "Введите текст для Spotify (например, статус): " + Style.RESET_ALL).strip() or "✠ ВАС ВЫЕБ@ЛИ R-ZONE CLXN ✠"
        activity["assets"]["large_text"] = input(Fore.RED + "Введите текст для Spotify (например, подпись): " + Style.RESET_ALL).strip() or "✠ ВАС ВЫЕБ@ЛИ R-ZONE CLXN ✠"

    existing_user_ids = read_users(directory)
    if existing_user_ids:
        print(Fore.GREEN + f"Успешно будут пингануты {len(existing_user_ids)} пользователей." + Style.RESET_ALL)
    else:
        print(Fore.RED + "Нету скрапнутых идентификаторов этого сервере. Попробуйте скрапнуть." + Style.RESET_ALL)

    user_ids = run_scrape(tokens[0], server_id, channel_ids[0]) if scrap_users == "да" else read_users(directory)
    if scrap_users == "да" and user_ids:
        save_users(user_ids, directory)

    if isfile(f"{directory}/users.txt") and len(read_users(directory)) > 0:
        user_ids = read_users(directory)

    message_text = input(f'{Fore.RED}Введите текст для отправки: {Style.RESET_ALL}').strip()
    if not message_text:
        print(f'{Fore.RED}Ошибка: текст не может быть пустым.{Style.RESET_ALL}')
        time.sleep(2)
        return

    if scrap_users == "да":
        while True:
            try:
                num_pings = int(input(f'{Fore.RED}Сколько пинговать пользователей (0–20, 0 — без пингов): {Style.RESET_ALL}'))
                if 0 <= num_pings <= 20:
                    break
                print(f'{Fore.RED}Ошибка: введите число от 0 до 20.{Style.RESET_ALL}')
            except ValueError:
                print(f'{Fore.RED}Ошибка: введите целое число.{Style.RESET_ALL}')
    else:
        num_pings = 0

    supported_languages = ['af', 'sq', 'am', 'ar', 'hy', 'as', 'ay', 'az', 'bm', 'eu', 'be', 'bn', 'bho', 'bs', 'bg', 'ca', 'ceb', 'ny', 'zh-CN', 'zh-TW', 'co', 'hr', 'cs', 'da', 'dv', 'doi', 'nl', 'en', 'eo', 'et', 'ee', 'tl', 'fi', 'fr', 'fy', 'gl', 'ka', 'de', 'el', 'gn', 'gu', 'ht', 'ha', 'haw', 'iw', 'hi', 'hmn', 'hu', 'is', 'ig', 'ilo', 'id', 'ga', 'it', 'ja', 'jw', 'kn', 'kk', 'km', 'rw', 'gom', 'ko', 'kri', 'ku', 'ckb', 'ky', 'lo', 'la', 'lv', 'ln', 'lt', 'lg', 'lb', 'mk', 'mai', 'mg', 'ms', 'ml', 'mt', 'mi', 'mr', 'mni-Mtei', 'lus', 'mn', 'my', 'ne', 'no', 'or', 'om', 'ps', 'fa', 'pl', 'pt', 'pa', 'qu', 'ro', 'ru', 'sm', 'sa', 'gd', 'nso', 'sr', 'st', 'sn', 'sd', 'si', 'sk', 'sl', 'so', 'es', 'su', 'sw', 'sv', 'tg', 'ta', 'tt', 'te', 'th', 'ti', 'ts', 'tr', 'tk', 'ak', 'uk', 'ur', 'ug', 'uz', 'vi', 'cy', 'xh', 'yi', 'yo', 'zu']

    try:
        asyncio.run(run_all_spam_tasks(
            tokens, channel_ids, message_text, user_ids, num_pings,
            include_symbols, include_emojis, supported_languages, use_translation, use_spotify
        ))
    except KeyboardInterrupt:
        print(f'{Fore.RED}Программа остановлена.{Style.RESET_ALL}')

async def heartbeat(interval, ws, token, failed_tokens):
    try:
        while True:
            await asyncio.sleep(interval)
            heartbeat_payload = {"op": 1, "d": None}
            await ws.send(json.dumps(heartbeat_payload))
    except websockets.exceptions.ConnectionClosedError as e:
        if failed_tokens is not None and token not in failed_tokens and "4004" in str(e):
            print(f'{Fore.RED}Ошибка: Неверный токен {token[:25]} (Authentication failed) в heartbeat. Пропускаем... {Style.RESET_ALL}')
            failed_tokens.add(token)
    except Exception as e:
        if failed_tokens is not None and token not in failed_tokens:
            print(f'{Fore.RED}Ошибка в heartbeat: {e}. {Style.RESET_ALL}')
            failed_tokens.add(token)

if __name__ == "__main__":
    main()