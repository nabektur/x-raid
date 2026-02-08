import string
import requests
import tls_client
import uuid
import time
import os
import random
from datetime import datetime
from colorama import Fore, init
from concurrent.futures import ThreadPoolExecutor

init(autoreset=True)

class client:
    def __init__(self):
        self.thingthong = string.ascii_letters + string.digits + '-_'
        self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.xsup = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvc3MiOiJ3aW5kb3dzIiwiYnJvd3NlciI6ImNocm9tZSIsInZlcnNpb24iOiIxMjAiLCJkZXZpY2UiOiJkZXNrdG9wIiwidGltZXpvbmUiOiJFdXJvcGUvQmVybGluIn0."
        self.cookies = self.get_cookies()

    def build(self, token=None) -> tuple:
        sess = tls_client.Session(
            client_identifier='chrome_120',
            random_tls_extension_order=True,
        )        

        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,pl;q=0.9',
            'Content-Type': 'application/json',
            'Origin': 'https://discord.com',
            'Priority': 'u=1, i',
            'Sec-Ch-Ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.ua,
            'X-Debug-Options': 'bugReporterEnabled',
            'X-Discord-Locale': 'en-US',
            'X-Discord-Timezone': 'Europe/Berlin',
            'X-Super-Properties': self.xsup
        }

        if token:
            headers['Authorization'] = token

        clean_cookies = {k: v for k, v in self.cookies.items() if v}
        
        return sess, clean_cookies, headers
    
    def get_cookies(self):    
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,pl;q=0.9',
            'User-Agent': self.ua,
        }

        try:
            r = requests.get('https://discord.com', headers=headers, timeout=10)
            cookies_ = r.cookies.get_dict()
            
            result = {}
            if cookies_.get('__dcfduid'):
                result['__dcfduid'] = cookies_['__dcfduid']
            if cookies_.get('__sdcfduid'):
                result['__sdcfduid'] = cookies_['__sdcfduid']
            if cookies_.get('_cfuvid'):
                result['_cfuvid'] = cookies_['_cfuvid']
            if cookies_.get('__cfruid'):
                result['__cfruid'] = cookies_['__cfruid']
            
            result['locale'] = 'en-US'
            
            return result
        except Exception as e:
            print(f'{Fore.RED}Ошибка получения cookies: {e}{Fore.RESET}')
            return {'locale': 'en-US'}

client_instance = client()

class button_presser:
    def __init__(self, tokens_file='tokens.txt'):
        self.tokens_file = tokens_file
        self.tokens = self.load_tokens()

    def load_tokens(self):
        if not os.path.exists(self.tokens_file):
            with open(self.tokens_file, 'w', encoding='utf-8') as f:
                f.write('')
            print(Fore.RED + f"Файл tokens.txt не найден. Он был создан автоматически. Добавьте токены и перезапустите скрипт.")
            exit()

        with open(self.tokens_file, 'r', encoding='utf-8') as f:
            tokens = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return tokens

    @staticmethod
    def clear_console():
        os.system('cls' if os.name == 'nt' else 'clear')

    def input_wait(self):
        input(Fore.RED + "Нажмите Enter, чтобы продолжить...")
        self.clear_console()
        os.system('python main.py')

    def titles(self, title):
        print(Fore.CYAN + f"\n{'=' * 40}\n{title}\n{'=' * 40}\n")

    def main_menu(self):
        print(Fore.RED + "Возврат в главное меню...")
        time.sleep(1)
        self.clear_console()
        os.system('python main.py')

    def check_token_access(self, token: str, channelid: str):
        sess, cookies, headers = client_instance.build(token)
        r = sess.get(f"https://discord.com/api/v9/channels/{channelid}", headers=headers, cookies=cookies)
        if r.status_code != 200:
            return False, f"Нет доступа к каналу: {r.text}"
        return True, "Доступ есть"

    def press_button(self, token: str, channelid: str, messageid: str, serverid: str, customid: str, application_id: str, component_type: int, selected_value: str = None, csess=None):
        has_access, reason = self.check_token_access(token, channelid)
        if not has_access:
            print(f'{Fore.RED}{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Ошибка: {token[:6]}... пропускаю статус!')
            return False

        sess, cookies, headers = client_instance.build(token)
        if csess:
            sess = csess

        payload = {
            'application_id': application_id,
            'channel_id': channelid,
            'guild_id': serverid,
            'message_id': messageid,
            'message_flags': 0,
            'type': 3,
            'data': {
                'component_type': component_type,
                'custom_id': customid,
            },
            'nonce': utils.getnonce(),
            'session_id': uuid.uuid4().hex,
        }

        if component_type == 3 and selected_value:
            payload['data']['values'] = [selected_value]

        r = sess.post(
            'https://discord.com/api/v9/interactions',
            headers=headers,
            cookies=cookies,
            json=payload
        )

        try:
            resp = r.json()
        except:
            resp = r.text

        if r.status_code == 204:
            print(f'{Fore.GREEN}[ + ] - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Успешно: {token[:6]}... нажал кнопку!...')
            return True
        else:
            print(f'{Fore.RED}{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Ошибка: {token[:6]}... пропускаю статус!')  
            return False

    def validate_button_and_list(self, channelid: str, messageid: str, token: str):
        message = Discord.get_message(channelid, messageid, token)
        if not message:
            return False, "Не удалось получить сообщение!", []

        if 'components' not in message:
            return False, "В сообщении нет компонентов!", []

        available_components = []
        for component_group in message.get('components', []):
            if 'components' in component_group:
                for component in component_group['components']:
                    component_type = component.get('type')
                    if component_type == 2: 
                        label = component.get('label', 'Без названия')
                        custom_id = component.get('custom_id')
                        emoji = component.get('emoji', {}).get('name', '') if component.get('emoji') else ''
                        if custom_id:
                            available_components.append({
                                'type': component_type,
                                'custom_id': custom_id,
                                'label': label,
                                'emoji': emoji
                            })
                    elif component_type == 3:  
                        placeholder = component.get('placeholder', 'Без названия')
                        custom_id = component.get('custom_id')
                        if custom_id:
                            available_components.append({
                                'type': component_type,
                                'custom_id': custom_id,
                                'label': placeholder,
                                'emoji': ''  
                            })

        return bool(available_components), "Компоненты найдены!" if available_components else "Компоненты не найдены!", available_components

    def menu(self):        
        serverid = input(Fore.RED + "Введите ID сервера (guild_id): ")
        channelid = input(Fore.RED + "Введите ID канала (channel_id): ")
        messageid = input(Fore.RED + "Введите ID сообщения (message_id): ")

        if not serverid or not channelid or not messageid:
            self.input_wait()
            return

        if not self.tokens:
            print(Fore.RED + "Токены не найдены! Добавьте их в tokens.txt")
            self.input_wait()
            return

        application_id = None
        valid_token_for_validation = None
        available_components = []

        for token in self.tokens:
            has_access, access_reason = self.check_token_access(token, channelid)
            if not has_access:
                print(f'{Fore.RED}{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Ошибка: {token[:6]}... не может проверить компоненты, пробую следующий токен...')
                continue

            components_valid, components_reason, available_components = self.validate_button_and_list(channelid, messageid, token)
            if not components_valid:
                print(Fore.RED + f"Ошибка: {components_reason}")
                self.input_wait()
                return

            application_id = Discord.get_application_id(channelid, messageid, token)
            if application_id:
                valid_token_for_validation = token
                break
            else:
                print(f'{Fore.RED}{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Ошибка: {token[:6]}... не смог получить application_id, пробую следующий токен...')

        if not application_id:
            print(Fore.RED + "Ни один токен не смог получить application_id автоматически!")
            application_id = input(Fore.RED + "Введите application_id вручную (ID бота, который создал компонент): ")
            if not application_id:
                print(Fore.RED + "application_id обязателен! Завершение работы.")
                self.input_wait()
                return

        if available_components:
            print(Fore.RED + "\nДоступные компоненты:")
            for i, component in enumerate(available_components, 1):
                label = component['label']
                emoji = component['emoji']
                component_type = component['type']
                display_name = ''
                if component_type == 2:  
                    if emoji and label == 'Без названия':
                        display_name = emoji
                    elif emoji:
                        display_name = f"{emoji} {label}"
                    else:
                        display_name = label
                    display_name = f"Кнопка: {display_name}"
                elif component_type == 3: 
                    display_name = f"Меню: {label}"
                print(Fore.RED + f"{i}. {display_name}")
            
            while True:
                try:
                    choice = int(input(Fore.RED + "Выберите номер компонента: "))
                    if 1 <= choice <= len(available_components):
                        selected_component = available_components[choice - 1]
                        custom_id = selected_component['custom_id']
                        component_type = selected_component['type']
                        break
                    else:
                        print(Fore.RED + f"Введите число от 1 до {len(available_components)}!")
                except ValueError:
                    print(Fore.RED + "Введите корректное число!")
        else:
            print(Fore.RED + "Компоненты не найдены!")
            self.input_wait()
            return

        selected_value = None
        if component_type == 3:
            message = Discord.get_message(channelid, messageid, valid_token_for_validation)
            if message and 'components' in message:
                for component_group in message.get('components', []):
                    if 'components' in component_group:
                        for component in component_group['components']:
                            if component.get('custom_id') == custom_id and component.get('type') == 3:
                                options = component.get('options', [])
                                if options:
                                    print(Fore.RED + "\nДоступные опции:")
                                    for i, option in enumerate(options, 1):
                                        option_label = option.get('label', 'Без названия')
                                        option_value = option.get('value')
                                        print(Fore.RED + f"{i}. {option_label}")
                                    while True:
                                        try:
                                            option_choice = int(input(Fore.RED + "Выберите номер опции: "))
                                            if 1 <= option_choice <= len(options):
                                                selected_value = options[option_choice - 1]['value']
                                                break
                                            else:
                                                print(Fore.RED + f"Введите число от 1 до {len(options)}!")
                                        except ValueError:
                                            print(Fore.RED + "Введите корректное число!")
                                break
                if not selected_value:
                    print(Fore.RED + "Не удалось найти опции для выбора!")
                    self.input_wait()
                    return

        thread(
            len(self.tokens),  
            self.press_button,
            self.tokens,
            [channelid, messageid, serverid, custom_id, application_id, component_type, selected_value]
        ).work()
        
        self.input_wait()

class thread:
    def __init__(self, thread_amt: int, func, tokens: list = [], args: list = []):
        self.maxworkers = thread_amt
        self.func = func
        self.tokens = tokens
        self.args = args

    def work(self):
        if self.tokens:
            with ThreadPoolExecutor(max_workers=self.maxworkers) as exe:
                for token in self.tokens:
                    self.args.insert(0, token)
                    try:
                        exe.submit(self.func, *self.args)
                    except Exception as e:
                        print(f'{Fore.RED}{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Ошибка: {token[:6]}... не смог выполнить действие...')
                    self.args.remove(token)
        else:
            print(Fore.RED + "Нет токенов! Добавьте их в tokens.txt")

class utils:
    def random_string(length: int) -> str:
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    def getnonce():
        return str((int(time.mktime(datetime.now().timetuple())) * 1000 - 1420070400000) * 4194304)
    
    def gettimestamp():
        timestamp = "{:.0f}".format(time.time() * 1000)
        return timestamp

class Discord:
    @staticmethod
    def get_message(channelid, messageid, token):
        if not token:
            return None

        sess, cookies, headers = client_instance.build(token)
        r = sess.get(f"https://discord.com/api/v9/channels/{channelid}/messages?limit=1&around={messageid}", headers=headers, cookies=cookies)
        
        if r.status_code != 200:
            print(Fore.RED + f"Ошибка получения сообщения: {r.text}")
            return None

        messages = r.json()
        if not messages:
            print(Fore.RED + "Сообщение не найдено!")
            return None

        return messages[0]

    @staticmethod
    def get_application_id(channelid, messageid, token):
        message = Discord.get_message(channelid, messageid, token)
        if not message:
            return None

        if 'application_id' in message:
            return message['application_id']
        elif 'author' in message and 'id' in message['author']:
            return message['author']['id']  
        else:
            print(Fore.RED + "Не удалось найти application_id в сообщении!")
            return None

if __name__ == "__main__":
    button_presser().menu()