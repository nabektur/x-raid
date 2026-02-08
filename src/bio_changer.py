import concurrent.futures
import requests
import os
from colorama import Fore, init
from datetime import datetime
import time

init(autoreset=True)

class BioChanger:
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

    def change_bio(self, bio):
        global success, failure
        success = 0
        failure = 0

        if bio == "" or bio is None:
            bio = "discord.gg/pon"

        def bio_changer(token):
            global success, failure
            payload = {
                "bio": bio
            }

            response = requests.patch("https://discord.com/api/v9/users/@me/profile", headers={'Authorization': token}, json=payload)
            if response.status_code in [200, 202]:
                success += 1
                print(f'{Fore.GREEN}[ + ] - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} -  Успешно: {token[:6]}... Изменено БИО...')
            else:
                failure += 1
                print(f'{Fore.RED}{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Ошибка: {token[:6]}... При изменении БИО, статус: {response.status_code}...')  

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(bio_changer, self.tokens)
        
        print(f"{Fore.GREEN}Успешно: {success}, Неуспешно: {failure}")

        input(Fore.RED + "Нажмите Enter, чтобы продолжить...")
        self.clear_console()
        os.system('python main.py')

    @staticmethod
    def clear_console():
        os.system('cls' if os.name == 'nt' else 'clear')

    def main_menu(self):
        print(Fore.RED + "Возврат в главное меню...")
        time.sleep(1)

if __name__ == '__main__':
    bio_changer = BioChanger()
    bio = input(Fore.RED + "Введите БИО: ")
    bio_changer.change_bio(bio)