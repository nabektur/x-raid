import requests
import time
import os
import threading
from colorama import Fore, Style, init
from datetime import datetime

init(autoreset=True)

class Raider:
    def __init__(self):
        self.base_url = "https://discord.com/api/v9/channels/{}/typing"
        self.tokens_file = "tokens.txt"
        self.tokens = self.load_or_create_tokens()

    def load_or_create_tokens(self):
        if not os.path.exists(self.tokens_file):
            with open(self.tokens_file, 'w') as file:
                file.write("")
            exit()
        
        with open(self.tokens_file, 'r') as file:
            tokens = [line.strip() for line in file if line.strip()]
        return tokens
    
    def typier(self, token, channel_id):
        url = self.base_url.format(channel_id)
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        while True:
            response = requests.post(url, headers=headers)
            if response.status_code == 204:
                print(f'{Fore.GREEN}[ + ] - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Печатает: {token[:6]}... В канале {channel_id}...')
            else:
                print(f'{Fore.RED}{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Ошибка: {token[:20]}... При отправке сообщения, статус: {response.status_code}... в канале {channel_id}...')
            time.sleep(10) 

    def execute_typing(self):
        channel_id = input(Fore.RED + "Введите идентификатор канала: ")
        if not channel_id:
            print(Fore.RED + "Неверный идентификатор канала.")
            return

        threads = []
        for token in self.tokens:
            thread = threading.Thread(target=self.typier, args=(token, channel_id))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
class Main:
    def __init__(self):
        self.raider = Raider()
    
    def start(self):
        self.raider.execute_typing()

if __name__ == "__main__":
    main = Main()
    main.start()