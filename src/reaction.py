import requests
import time
import os
import datetime
from colorama import Fore

class Client:
    def __init__(self, token):
        self.sess = requests.Session()
        self.headers = {'Authorization': token}
        self.cookies = {}

class Reaction:
    def __init__(self, tokens_file='tokens.txt'):
        self.serverid = None
        self.channelid = None
        self.messageid = None
        self.reaction = None
        self.delay = 0
        self.url = None
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

    def bypass(self, token):
        cl = Client(token)
        cl.headers['Authorization'] = token

        r = cl.sess.put(
            self.url,
            headers=cl.headers,
            cookies=cl.cookies
        )

        if r.status_code == 204:
            print(f'{Fore.GREEN}[ + ] - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Токен: {token[:6]}... Успешно')
        elif 'retry_after' in r.text:
            limit = r.json().get('retry_after', 1.5)
            print(Fore.YELLOW + f'[ ~ ] - {token[:6]}... >> Лимит на {limit} сек.')
            time.sleep(float(limit))
            self.bypass(token)
        elif 'Cloudflare' in r.text:
            print(Fore.YELLOW + f'[ ~ ] - {token[:6]}... >> Cloudflare блокировка >> Ожидание 5 сек. и повторная попытка')
            time.sleep(5)
            self.bypass(token)
        elif 'captcha_key' in r.text:
            print(Fore.YELLOW + f'[ ~ ] - {token[:6]}... >> HCaptcha')
        elif 'You need to verify' in r.text:
            print(f'{Fore.RED}[ - ] - {token[:6]}... >> Заблокировано')
        else:
            print(f'{Fore.RED}[ - ] - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Ошибка: {token[:6]}... При реакции для токена, статус: {r.status_code}')

    def debypass(self, token):
        cl = Client(token)
        cl.headers['Authorization'] = token

        r = cl.sess.delete(
            self.url,
            headers=cl.headers,
            cookies=cl.cookies
        )

        if r.status_code == 204:
            print(f'{Fore.GREEN}[ + ] - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Токен: {token[:6]}... Успешно')
        elif 'retry_after' in r.text:
            limit = r.json().get('retry_after', 1.5)
            print(Fore.YELLOW + f'[ ~ ] - {token[:6]}... >> Лимит на {limit} сек.')
            time.sleep(float(limit))
            self.debypass(token)
        elif 'Cloudflare' in r.text:
            print(Fore.YELLOW + f'[ ~ ] - {token[:6]}... >> Cloudflare блокировка >> Ожидание 5 сек. и повторная попытка')
            time.sleep(5)
            self.debypass(token)
        elif 'captcha_key' in r.text:
            print(Fore.YELLOW + f'[ ~ ] - {token[:6]}... >> HCaptcha')
        elif 'You need to verify' in r.text:
            print(f'{Fore.RED}[ - ] - {Fore.RED}{token[:6]}... >> Заблокировано')
        else:
            print(f'{Fore.RED}[ - ] - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Ошибка: {token[:6]}... При заходе для токена, статус: {r.status_code} - {r.text}')

    @staticmethod
    def clear_console():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def input_wait():
        input(Fore.RED + "Нажмите Enter, чтобы продолжить...")
        Reaction.clear_console()
        os.system('python main.py')

    def main_menu(self):
        print(Fore.RED + "Возврат в главное меню...")
        time.sleep(1)
        self.clear_console()
        os.system('python main.py')

    def main(self):
        self.serverid = input(Fore.RED + 'Введите ID сервера: ')
        self.channelid = input(Fore.RED + 'Введите ID канала: ')
        self.messageid = input(Fore.RED + 'Введите ID сообщения: ')
        dodebypass_input = input(Fore.RED + 'Выполнить деобход? (если токены уже отреагировали, сначала удалите реакцию) (да/нет): ').lower()
        self.dodebypass = dodebypass_input == 'да'
        try:
            self.delay = float(input(Fore.RED + 'Введите задержку (0 для отсутствия задержки): '))
        except:
            print(Fore.RED + 'Задержка установлена в 0 (ошибка при преобразовании в число)')
            self.delay = 0

        self.reaction = input(Fore.RED + 'Введите реакцию (например, 👍): ')
        self.url = f'https://discord.com/api/v9/channels/{self.channelid}/messages/{self.messageid}/reactions/{self.reaction}/@me'

        for token in self.tokens:
            if self.dodebypass:
                self.debypass(token)
            else:
                self.bypass(token)
        self.input_wait()

if __name__ == "__main__":
    Reaction().main()