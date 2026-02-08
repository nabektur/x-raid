import os
import time
import uuid
import requests
import random
from colorama import Fore
import tls_client
import datetime
from concurrent.futures import ThreadPoolExecutor

class prep:
    def __init__(self):
        self.identifier = 'chrome_131'
        self.sess = tls_client.Session(
            client_identifier=self.identifier,
            random_tls_extension_order=True,
        )
        self.headers = {}
        self.initialize_client()

    def initialize_client(self):
        try:
            r = requests.get('https://raw.githubusercontent.com/sadasdas2131/discord-api-main/refs/heads/main/latest.json', timeout=10).json()
            self.xsup = r['chrome133-duckduckgo']['X-Super-Properties']
            self.ua = r['chrome133-duckduckgo']['User-Agent']
        except Exception as e:
            print(f'{Fore.RED}Не удалось загрузить конфигурацию, использую стандартную: {e}{Fore.RESET}')
            self.xsup = 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEzMS4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTMxLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjk5OTksImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9'
            self.ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        
        self.reffrer = 'https://discord.com/channels/@me'
        self.xtimezone = 'Europe/Warsaw'
        self.cookies_renew()
        self.headers_form()

    def cookies_renew(self):
        try:
            r = self.sess.get('https://discord.com', headers=self.headers)
            cookies_ = r.cookies.get_dict()
            self.cookies = {
                '__dcfduid': cookies_.get('__dcfduid', ''),
                '__sdcfduid': cookies_.get('__sdcfduid', ''),
                '_cfuvid': cookies_.get('_cfuvid', ''),
                'locale': 'en-US',
                '__cfruid': cookies_.get('__cfruid', '')
            }
            self.cookies = {k: v for k, v in self.cookies.items() if v}
        except Exception as e:
            print(f'{Fore.RED}Ошибка получения cookies: {e}{Fore.RESET}')
            self.cookies = {'locale': 'en-US'}

    def headers_form(self):
        self.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-GB,pl;q=0.9',
            'Content-Type': 'application/json',
            'Origin': 'https://discord.com',
            'Referer': self.reffrer,
            'Priority': 'u=1, i',
            'Sec-Ch-Ua': '"Not;A=Brand";v="24", "Chromium";v="131"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.ua,
            'X-Debug-Options': 'bugReporterEnabled',
            'X-Discord-Locale': 'en-US',
            'X-Discord-Timezone': self.xtimezone,
            'X-Super-Properties': self.xsup
        }

class client:
    def __init__(self, token=None):
        self.token = token
        self.sess = tls_client.Session(
            client_identifier=prep().identifier,
            random_tls_extension_order=True,
        )
        prep_instance = prep()
        self.headers = prep_instance.headers.copy()
        self.cookies = prep_instance.cookies.copy()
        self.xsup = prep_instance.xsup
        self.ua = prep_instance.ua

class joiner:
    def __init__(self, tokens_file='tokens.txt'):
        self.invite = None
        self.delay = 0
        self.tokens_file = tokens_file
        self.tokens = self.load_tokens()

    def load_tokens(self):
        if not os.path.exists(self.tokens_file):
            with open(self.tokens_file, 'w') as f:
                f.write('')
            print(Fore.RED + f"Файл {self.tokens_file} не найден. Он был создан автоматически. Добавьте токены и перезапустите скрипт.")
            exit()

        with open(self.tokens_file, 'r') as f:
            tokens = [line.strip() for line in f if line.strip() and not line.startswith('#')]                
        return tokens

    @staticmethod
    def clear_console():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def input_wait():
        input(Fore.RED + "Нажмите Enter, чтобы продолжить...")
        joiner.clear_console()
        os.system('python main.py')

    def main_menu(self):
        print(Fore.RED + "Возврат в главное меню...")
        time.sleep(1)
        self.clear_console()
        os.system('python main.py')

    def join(self, token):
        cl = client(token)
        cl.headers['Authorization'] = token
        self.sessionid = uuid.uuid4().hex

        payload = {
            'session_id': self.sessionid
        }

        try:
            clean_cookies = {k: v for k, v in cl.cookies.items() if v is not None and v != ''}
            
            r = cl.sess.post(
                f'https://discord.com/api/v9/invites/{self.invite}',
                headers=cl.headers,
                cookies=clean_cookies if clean_cookies else None,
                json=payload
            )

            if r.status_code == 200:
                print(f'{Fore.GREEN}[ + ] - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Токен: {token[:6]}... Успешно зашёл на сервер: https://discord.gg/{self.invite}')
            elif r.status_code == 403 and 'already_joined' in r.text:
                print(f'{Fore.RED}[ * ] - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Токен: {token[:6]}... Уже находится на сервере: https://discord.gg/{self.invite}')
            elif 'retry_after' in r.text:
                try:
                    limit = r.json().get('retry_after', 1.5)
                    print(f'{Fore.RED}[ ! ] - Рейтлимит, ожидание {limit} сек...')
                    time.sleep(float(limit))
                    self.join(token)
                except:
                    time.sleep(2)
            elif 'Cloudflare' in r.text:
                print(f'{Fore.RED}[ ! ] - Cloudflare защита, повтор через 5 сек...')
                time.sleep(5)
                self.join(token)
            elif 'captcha_key' in r.text:
                print(f'{Fore.RED}[ ! ] - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Требуется CAPTCHA для токена: {token[:6]}...')
            elif 'You need to verify' in r.text:
                print(f'{Fore.RED}[ - ] - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Токен заблокирован: {token[:6]}...')
            else:
                print(f'{Fore.RED}[ - ] - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Ошибка: {token[:6]}... статус: {r.status_code}')
        
        except Exception as e:
            print(f'{Fore.RED}[ - ] - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Ошибка подключения для {token[:6]}...: {str(e)}')

    def main(self):
        self.invite = input(Fore.RED + 'Приглашение: ')
        self.invite = self.invite.replace('https://discord.gg/', '').strip()
        try:
            self.delay = float(input(Fore.RED + 'Задержка (0 для без задержки): '))
        except ValueError:
            print(Fore.RED + 'Задержка установлена на 0 (не удалось преобразовать в число, недопустимый ввод?)')
            self.delay = 0

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.join, token) for token in self.tokens]
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    print(f'{Fore.RED}Ошибка в потоке: {e}')
                if self.delay > 0:
                    time.sleep(self.delay)

        self.input_wait()

if __name__ == "__main__":
    joiner_instance = joiner()
    joiner_instance.main()