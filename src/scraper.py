import requests
import time
import os
import threading
import json
import random
from colorama import Fore, Style, init
from datetime import datetime
import websocket
import asyncio
from deep_translator import GoogleTranslator
import ssl, certifi
ssl_context = ssl.create_default_context(cafile=certifi.where())

init(autoreset=True)
printed_logs = set()

class Utils:
    @staticmethod
    def rangeCorrector(ranges):
        if [0, 99] not in ranges:
            ranges.insert(0, [0, 99])
        return ranges

    @staticmethod
    def getRanges(index, multiplier, memberCount):
        initialNum = int(index * multiplier)
        rangesList = [[initialNum, initialNum + 99]]
        if memberCount > initialNum + 99:
            rangesList.append([initialNum + 100, initialNum + 199])
        return Utils.rangeCorrector(rangesList)

    @staticmethod
    def parseGuildMemberListUpdate(response):
        memberdata = {
            "online_count": response["d"]["online_count"],
            "member_count": response["d"]["member_count"],
            "id": response["d"]["id"],
            "guild_id": response["d"]["guild_id"],
            "hoisted_roles": response["d"]["groups"],
            "types": [],
            "locations": [],
            "updates": []
        }

        for chunk in response['d']['ops']:
            memberdata['types'].append(chunk['op'])
            if chunk['op'] in ('SYNC', 'INVALIDATE'):
                memberdata['locations'].append(chunk['range'])
                if chunk['op'] == 'SYNC':
                    memberdata['updates'].append(chunk['items'])
                else:
                    memberdata['updates'].append([])
            elif chunk['op'] in ('INSERT', 'UPDATE', 'DELETE'):
                memberdata['locations'].append(chunk['index'])
                if chunk['op'] == 'DELETE':
                    memberdata['updates'].append([])
                else:
                    memberdata['updates'].append(chunk['item'])

        return memberdata

class DiscordSocket(websocket.WebSocketApp):
    def __init__(self, token, guild_id, channel_id, all_tokens, existing_members=None):
        self.token = token
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.all_tokens = all_tokens
        self.current_token_index = 0
        self.existing_members = existing_members or {}

        self.socket_headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15"
        }

        super().__init__("wss://gateway.discord.gg/?encoding=json&v=9",
                            header=self.socket_headers,
                            on_open=self.sock_open,
                            on_message=self.sock_message,
                            on_close=self.sock_close,
                            on_error=self.sock_error)

        self.endScraping = False
        self.guilds = {}
        self.members = dict(existing_members)
        self.ranges = [[0, 0]]
        self.lastRange = 0
        self.packets_recv = 0
        self.connected = False
        self.ready = False
        self.last_update_time = time.time()
        self.scraping_complete = False
        self.no_data_count = 0
        self.should_try_next_token = False
        self.bot_count = 0
        self.total_seen = 0

    def run(self):
        self.run_forever(sslopt={"context": ssl_context})
        return self.members

    def get_next_token(self):
        if self.current_token_index >= len(self.all_tokens):
            return None
        token = self.all_tokens[self.current_token_index]
        self.current_token_index += 1
        return token

    def scrapeUsers(self):
        if not self.endScraping and self.ready:
            payload = {
                "op": 14,
                "d": {
                    "guild_id": self.guild_id,
                    "typing": True,
                    "activities": True,
                    "threads": True,
                    "channels": {
                        self.channel_id: self.ranges
                    }
                }
            }
            self.send(json.dumps(payload))

    def sock_open(self, ws):
        print(f'{Fore.GREEN}[✓] WebSocket соединение установлено')
        self.connected = True
        current_token = self.all_tokens[0] if self.all_tokens else self.token
        
        auth_payload = {
            "op": 2,
            "d": {
                "token": current_token,
                "capabilities": 125,
                "properties": {
                    "os": "Windows",
                    "browser": "Firefox",
                    "device": "",
                    "system_locale": "ru-RU",
                    "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0",
                    "browser_version": "94.0",
                    "os_version": "10",
                    "referrer": "",
                    "referring_domain": "",
                    "referrer_current": "",
                    "referring_domain_current": "",
                    "release_channel": "stable",
                    "client_build_number": 103981,
                    "client_event_source": None
                },
                "presence": {
                    "status": "online",
                    "since": 0,
                    "activities": [],
                    "afk": False
                },
                "compress": False,
                "client_state": {
                    "guild_hashes": {},
                    "highest_last_message_id": "0",
                    "read_state_version": 0,
                    "user_guild_settings_version": -1,
                    "user_settings_version": -1
                }
            }
        }
        self.send(json.dumps(auth_payload))

    def heartbeatThread(self, interval):
        try:
            while self.connected and not self.endScraping:
                self.send(json.dumps({"op": 1, "d": self.packets_recv}))
                
                if self.ready and time.time() - self.last_update_time > 30:
                    if len(self.members) > 0:
                        print(f'{Fore.RED}[!] Таймаут: нет новых данных 30 секунд')
                        print(f'{Fore.GREEN}[✓] Скрапинг завершён. Всего: {len(self.members)} пользователей')
                        self.endScraping = True
                        self.close()
                        break
                
                time.sleep(interval)
        except Exception as e:
            print(f'{Fore.RED}[!] Ошибка heartbeat: {e}')
            return

    def sock_message(self, ws, message):
        try:
            decoded = json.loads(message)
        except:
            return

        if decoded is None:
            return

        if decoded["op"] != 11:
            self.packets_recv += 1

        if decoded["op"] == 10:
            threading.Thread(
                target=self.heartbeatThread,
                args=(decoded["d"]["heartbeat_interval"] / 1000,),
                daemon=True
            ).start()

        if decoded["t"] == "READY":
            self.ready = True
            print(f'{Fore.GREEN}[✓] Авторизация успешна')
            for guild in decoded["d"]["guilds"]:
                self.guilds[guild["id"]] = {
                    "member_count": guild["member_count"],
                    "approximate_member_count": guild.get("approximate_member_count", guild["member_count"])
                }
            print(f'{Fore.CYAN}[i] Найдено серверов: {len(self.guilds)}')
            
            if self.guild_id not in self.guilds:
                print(f'{Fore.RED}[!] Токен не состоит в целевом сервере, пробуем следующий...')
                self.endScraping = True
                self.connected = False
                self.close()

        if decoded["t"] == "READY_SUPPLEMENTAL":
            if self.guild_id in self.guilds:
                member_count = self.guilds[self.guild_id]["member_count"]
                print(f'{Fore.CYAN}[i] Всего участников на сервере: {member_count}')
                print(f'{Fore.RED}[i] Боты будут пропущены, реальное число может быть меньше')
                self.ranges = Utils.getRanges(0, 100, member_count)
                self.scrapeUsers()
            else:
                print(f'{Fore.RED}[!] Токен не состоит в целевом сервере')
                self.endScraping = True
                self.close()

        elif decoded["t"] == "GUILD_MEMBER_LIST_UPDATE":
            parsed = Utils.parseGuildMemberListUpdate(decoded)

            if parsed['guild_id'] == self.guild_id and ('SYNC' in parsed['types'] or 'UPDATE' in parsed['types']):
                self.last_update_time = time.time()
                
                for elem, index in enumerate(parsed["types"]):
                    if index == "SYNC":
                        update_size = len(parsed['updates'][elem]) if elem < len(parsed['updates']) else 0
                        
                        if update_size == 0:
                            self.no_data_count += 1
                            if self.no_data_count >= 3 and len(self.members) > 0:
                                member_count = self.guilds.get(self.guild_id, {}).get("member_count", 0)
                                percentage = (len(self.members) / member_count * 100) if member_count > 0 else 0
                                
                                print(f'{Fore.RED}[!] Получено {self.no_data_count} пустых ответов')
                                print(f'{Fore.GREEN}[✓] Скрапинг завершён. Всего: {len(self.members)}/{member_count} ({percentage:.1f}%) пользователей')
                                self.endScraping = True
                                break
                            else:
                                continue
                        else:
                            self.no_data_count = 0

                        for item in parsed["updates"][elem]:
                            if not isinstance(item, dict):
                                continue
                            
                            self.total_seen += 1
                                
                            if "member" in item and "user" in item["member"]:
                                mem = item["member"]
                                
                                if not isinstance(mem, dict) or not isinstance(mem.get("user"), dict):
                                    continue
                                
                                if mem["user"].get("bot", False):
                                    self.bot_count += 1
                                    continue
                                if "embed" in mem:
                                    continue
                                try:
                                    discriminator = mem["user"].get("discriminator", "0")
                                    username = mem["user"]["username"]
                                    user_id = mem["user"]["id"]
                                    
                                    obj = {
                                        "tag": f"{username}#{discriminator}",
                                        "id": user_id
                                    }
                                    self.members[user_id] = obj
                                    current_dir = create_directory(self.guild_id)
                                    save_users([user_id], current_dir)
                                except (KeyError, TypeError) as e:
                                    continue

                    elif index == "UPDATE":
                        for item in parsed["updates"][elem]:
                            if not isinstance(item, dict):
                                continue
                            
                            self.total_seen += 1
                                
                            if "member" in item and "user" in item["member"]:
                                mem = item["member"]
                                
                                if not isinstance(mem, dict) or not isinstance(mem.get("user"), dict):
                                    continue
                                
                                if mem["user"].get("bot", False):
                                    self.bot_count += 1
                                    continue
                                if "embed" in mem:
                                    continue
                                try:
                                    discriminator = mem["user"].get("discriminator", "0")
                                    username = mem["user"]["username"]
                                    user_id = mem["user"]["id"]
                                    
                                    obj = {
                                        "tag": f"{username}#{discriminator}",
                                        "id": user_id
                                    }
                                    self.members[user_id] = obj
                                    current_dir = create_directory(self.guild_id)
                                    save_users([user_id], current_dir)
                                except (KeyError, TypeError):
                                    continue

                if not self.endScraping:
                    self.lastRange += 1
                    if self.guild_id in self.guilds:
                        member_count = self.guilds[self.guild_id]["member_count"]
                        self.ranges = Utils.getRanges(
                            self.lastRange, 100, member_count
                        )

                        estimated_humans = member_count - self.bot_count
                        if estimated_humans > 0:
                            percentage = (len(self.members) / estimated_humans * 100)
                        else:
                            percentage = (len(self.members) / member_count * 100)
                        
                        log_message = f'{Fore.RED}[+] {datetime.now().strftime("%H:%M:%S")} - Люди: {len(self.members)} | Боты: {self.bot_count} | Прогресс: {percentage:.1f}%'
                        if log_message not in printed_logs:
                            print(log_message)
                            printed_logs.add(log_message)

                        max_range = (member_count // 100 + 1) * 100
                        if self.lastRange * 100 >= max_range:
                            print(f'{Fore.RED}[!] Достигнут максимальный диапазон')
                            time.sleep(3)
                            if not self.scraping_complete:
                                estimated_humans = member_count - self.bot_count
                                if estimated_humans > 0:
                                    percentage = (len(self.members) / estimated_humans * 100)
                                else:
                                    percentage = (len(self.members) / member_count * 100)
                                
                                print(f'{Fore.CYAN}[i] Статистика токена:')
                                print(f'{Fore.CYAN}    └─ Собрано людей: {len(self.members)}')
                                print(f'{Fore.CYAN}    └─ Пропущено ботов: {self.bot_count}')
                                print(f'{Fore.CYAN}    └─ Всего на сервере: {member_count}')
                                print(f'{Fore.CYAN}    └─ Оценка людей: ~{estimated_humans}')
                                print(f'{Fore.CYAN}    └─ Прогресс: {percentage:.1f}%')
                                
                                if percentage < 95:
                                    print(f'{Fore.RED}[!] Не все пользователи собраны, попробуем следующий токен...')
                                    self.should_try_next_token = True
                                
                                self.scraping_complete = True
                                self.endScraping = True
                        else:
                            self.scrapeUsers()

            if self.endScraping:
                self.close()

    def sock_error(self, ws, error):
        print(f'{Fore.RED}[!] WebSocket ошибка: {error}')

    def sock_close(self, ws, close_code, close_msg):
        self.connected = False
        print(f'{Fore.RED}[!] WebSocket соединение закрыто')
        if close_code:
            print(f'{Fore.RED}[!] Код: {close_code}, Сообщение: {close_msg}')

def read_users(directory):
    if not os.path.exists(f"{directory}/users.txt"):
        open(f"{directory}/users.txt", "w").close()
    with open(f"{directory}/users.txt", "r") as file:
        return file.read().splitlines()

def save_users(user_ids, directory):
    existing_users = set(read_users(directory))
    with open(f"{directory}/users.txt", "a") as file:
        for user_id in user_ids:
            if user_id not in existing_users:
                file.write(f"{user_id}\n")

def create_directory(server_id):
    directory = f"scrapes/{server_id}"
    os.makedirs(directory, exist_ok=True)
    if not os.path.exists(f"{directory}/users.txt"):
        with open(f"{directory}/users.txt", "w") as file:
            file.write("")
    return directory

def read_tokens():
    if not os.path.exists("tokens.txt"):
        open("tokens.txt", "w").close()
        return []
    with open("tokens.txt", "r") as file:
        tokens = [line.strip() for line in file.readlines() if line.strip()]
        return tokens

def test_token_in_guild(token, server_id):
    """Проверяет, состоит ли токен в гильдии (более точная проверка)"""
    try:
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }

        response = requests.get(
            f"https://discord.com/api/v9/users/@me/guilds",
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            guilds = response.json()
            for guild in guilds:
                if guild.get("id") == server_id:
                    return True
        return False
    except Exception as e:
        return False

async def run_scrape(tokens, server_id, channel_id):
    if not tokens:
        print(f'{Fore.RED}[!] Нет доступных токенов в tokens.txt')
        return {}

    print(f'{Fore.CYAN}[i] Проверка токенов на членство в сервере...')
    valid_tokens = []
    
    for i, token in enumerate(tokens):
        print(f'{Fore.RED}[...] Проверка токена {i+1}/{len(tokens)}')
        if test_token_in_guild(token, server_id):
            valid_tokens.append(token)
            print(f'{Fore.GREEN}[✓] Токен {i+1} состоит в сервере')
        else:
            print(f'{Fore.RED}[✗] Токен {i+1} не состоит в сервере')

    if not valid_tokens:
        print(f'{Fore.RED}[!] Ни один токен не состоит в этом сервере')
        print(f'{Fore.RED}[i] Убедитесь что токены действительно добавлены на сервер')
        return {}

    print(f'{Fore.GREEN}[✓] Найдено валидных токенов: {len(valid_tokens)}')
    
    all_members = {}
    for i, token in enumerate(valid_tokens):
        members_before = len(all_members)
        print(f'\n{Fore.CYAN}{"="*60}')
        print(f'{Fore.CYAN}[i] Попытка {i+1}/{len(valid_tokens)} - Токен #{i+1}')
        print(f'{Fore.CYAN}{"="*60}')
        
        try:
            sb = DiscordSocket(token, server_id, channel_id, valid_tokens, all_members)
            members = sb.run()
            
            new_members = 0
            for user_id, user_data in members.items():
                if user_id not in all_members:
                    all_members[user_id] = user_data
                    new_members += 1
            
            members_after = len(all_members)
            print(f'{Fore.GREEN}[✓] Токен #{i+1} добавил {new_members} новых пользователей')
            print(f'{Fore.CYAN}[i] Всего уникальных: {members_after}')
            
            if hasattr(sb, 'should_try_next_token') and sb.should_try_next_token:
                if i < len(valid_tokens) - 1:
                    print(f'{Fore.RED}[i] Продолжаем со следующим токеном...')
                    time.sleep(2)
                    continue
            
            if hasattr(sb, 'guilds') and server_id in sb.guilds:
                total_members = sb.guilds[server_id].get('member_count', 0)
                bot_count = getattr(sb, 'bot_count', 0)
                estimated_humans = total_members - bot_count
                
                if estimated_humans > 0:
                    percentage = (members_after / estimated_humans * 100)
                    print(f'{Fore.CYAN}[i] Оценка: {estimated_humans} человек на сервере (без {bot_count} ботов)')
                    if percentage >= 95:
                        print(f'{Fore.GREEN}[✓] Собрано {percentage:.1f}% участников - достаточно!')
                        break
                
        except Exception as e:
            print(f'{Fore.RED}[!] Ошибка с токеном {i+1}: {e}')
            if i < len(valid_tokens) - 1:
                print(f'{Fore.RED}[i] Пробуем следующий токен...')
                time.sleep(2)
            continue
    
    if not all_members:
        print(f'\n{Fore.RED}[!] Все попытки исчерпаны')
        return {}
    
    print(f'\n{Fore.GREEN}{"="*60}')
    print(f'{Fore.GREEN}[✓] СКРАПИНГ ЗАВЕРШЁН')
    print(f'{Fore.GREEN}{"="*60}')
    return all_members

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

async def main():
    clear_console()
    
    tokens = read_tokens()
    
    if not tokens:
        print(f'{Fore.RED}[!] Файл tokens.txt пуст или не существует')
        print(f'{Fore.RED}[i] Добавьте токены в файл tokens.txt (по одному на строку)')
        input(f'\n{Fore.RED}Нажмите Enter для выхода...')
        return
    
    print(f'{Fore.GREEN}[✓] Загружено токенов: {len(tokens)}\n')
    
    server_id = input(f"{Fore.RED}Введите ID сервера: ").strip()
    channel_id = input(f"{Fore.RED}Введите ID канала: ").strip()
    
    if not server_id or not channel_id:
        print(f'{Fore.RED}[!] ID сервера и канала обязательны')
        return
    
    directory = create_directory(server_id)
    
    scrap_users = input(f"{Fore.RED}Скрапить пользователей? (да/нет): ").strip().lower()
    
    if scrap_users == "да" or scrap_users == "yes" or scrap_users == "y":
        print(f'\n{Fore.CYAN}[i] Запуск скрапинга...\n')
        user_ids = await run_scrape(tokens, server_id, channel_id)
        
        if user_ids:
            print(f'\n{Fore.GREEN}[✓] Скрапинг завершён успешно!')
            print(f'{Fore.GREEN}[✓] Всего пользователей: {len(user_ids)}')
            print(f'{Fore.GREEN}[✓] Сохранено в: {directory}/users.txt')
        else:
            print(f'\n{Fore.RED}[!] Не удалось скрапить пользователей')
    else:
        user_ids = read_users(directory)
        print(f'{Fore.CYAN}[i] Загружено {len(user_ids)} пользователей из файла')

    input(f'\n{Fore.RED}Нажмите Enter, чтобы продолжить...')
    clear_console()
    
    os.system('python main.py')

if __name__ == "__main__":
    asyncio.run(main())