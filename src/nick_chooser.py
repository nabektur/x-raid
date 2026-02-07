import requests
import time
import os
import threading
from colorama import Fore, Style, init
from datetime import datetime

init(autoreset=True)

class NickChooser:

    def __init__(self, tokens_file='tokens.txt'):
        self.tokens_file = tokens_file
        self.tokens = self.load_tokens()

    def load_tokens(self):
        if not os.path.exists(self.tokens_file):
            with open(self.tokens_file, 'w') as f:
                f.write('')
            exit()
        
        with open(self.tokens_file, 'r') as f:
            tokens = [line.strip() for line in f if line.strip() and not line.startswith('#')]                
        return tokens

    @staticmethod
    def prompt(message):
        return input(f"{Fore.GREEN}{message}: {Style.RESET_ALL}")

    def run(self, function, args):
        threads = []
        for arg in args:
            thread = threading.Thread(target=function, args=arg)
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

    def mass_nick(self, token, guild, nick):
        headers = {'Authorization': token}
        url = f"https://discord.com/api/v9/guilds/{guild}/members/@me/nick"
        payload = {'nick': nick}
        response = requests.patch(url, headers=headers, json=payload)
        if response.status_code != 200:
            print(f'{Fore.RED}{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Ошибка: Не удалось сменить ник: {response.status_code}...')

    def choose_nick(self):
        nick = self.prompt(Fore.RED + "Введите ник")
        if nick == "":
            self.main_menu()

        guild = self.prompt(Fore.RED + "Введите идентификатор сервера")
        if guild == "":
            self.main_menu()
        
        args = [(token, guild, nick) for token in self.tokens]

        for arg in args:
            self.run(self.mass_nick, (arg,))

        print(f"{Fore.GREEN}[ + ] - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Успешно изменены все токены!{Style.RESET_ALL}")
        input(Fore.RED + "Нажмите Enter, чтобы продолжить...")
        self.clear_console()
        os.system('python main.py')

    @staticmethod
    def clear_console():
        os.system('cls' if os.name == 'nt' else 'clear')

    def main_menu(self):
        print(Fore.RED + "Возврат в главное меню...")
        time.sleep(1)

if __name__ == "__main__":
    chooser = NickChooser()
    chooser.choose_nick()