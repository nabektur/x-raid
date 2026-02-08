import os
import time
import requests
import threading
from colorama import Fore, Style, init
from datetime import datetime

init(autoreset=True)

class HypeSquadChooser:
    def __init__(self, tokens_file='tokens.txt'):
        self.tokens_file = tokens_file
        self.tokens = self.load_tokens()
        self.success_count = 0
        self.failed_tokens = []
        self.total_tokens = len(self.tokens)

    def load_tokens(self):
        if not os.path.exists(self.tokens_file):
            with open(self.tokens_file, 'w') as f:
                f.write('')
            exit()
        
        with open(self.tokens_file, 'r') as f:
            tokens = [line.strip() for line in f if line.strip() and not line.startswith('#')]                
        return tokens

    def choose(self, token, house_id):
        headers = {'Authorization': token}
        request_data = {'house_id': house_id}
        response = requests.post('https://discord.com/api/v9/hypesquad/online', headers=headers, json=request_data)
        if response.status_code == 401:
            print(f'{Fore.RED}{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Ошибка: {token[:6]}... При отправке сообщения, статус: {response.status_code}...')
            self.failed_tokens.append(token)
        else:
            print(f'{Fore.GREEN}{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Успешно: {token[:6]}... Статус: {response.status_code}...')
            self.success_count += 1

    def start(self, house):
        for token in self.tokens:
            self.choose(token, house)
        print(Fore.RED + "Все токены обработаны. Нажмите Enter, чтобы продолжить...")
        input()
        self.clear_console()
        self.main_menu()

    def run(self):
        self.clearprint()
        print(Fore.RED + "1. Bravery\n2. Brilliance\n3. Balance")
        choice = int(input(Fore.RED + "Выберите HypeSquad ID (1-3): "))
        if choice in [1, 2, 3]:
            self.start(choice)
        else:
            print(Fore.RED + "Неверный выбор!")

    @staticmethod
    def clear_console():
        os.system('cls' if os.name == 'nt' else 'clear')

    def clearprint(self):
        pass  

    def titles(self, title):
        print(f"\n{'=' * 40}\n{title}\n{'=' * 40}\n")

    def main_menu(self):
        os.system('python main.py')

if __name__ == "__main__":
    chooser = HypeSquadChooser()
    chooser.run()