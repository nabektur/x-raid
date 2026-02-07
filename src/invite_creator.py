import aiohttp
import asyncio
import os
import random
from colorama import Fore, init
from datetime import datetime

init(autoreset=True)

class AccountInviteCreator:
    def __init__(self, tokens_file='tokens.txt'):
        self.tokens_file = tokens_file
        self.tokens = self.load_tokens()

    def load_tokens(self):
        if not os.path.exists(self.tokens_file):
            with open(self.tokens_file, 'w') as f:
                f.write('')
        
        with open(self.tokens_file, 'r') as f:
            tokens = [line.strip() for line in f if line.strip() and not line.startswith('#')]                
        return tokens

    def headers(self, token):
        return {
            "Authorization": token,
            "Content-Type": "application/json"
        }

    async def get_random_channel(self, guild_id, token, session):
        async with session.get(
            f"https://discord.com/api/v9/guilds/{guild_id}/channels",
            headers=self.headers(token),
            ssl=False
        ) as response:
            if response.status == 200:
                channels = await response.json()
                return random.choice(channels).get("id")
            else:
                print(f'{Fore.RED}{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Ошибка: {token[:6]}... При получении канала, статус: {response.status}')  
                return None

    async def create_invite(self, token, guild_id, session):
        try:
            channel_id = await self.get_random_channel(guild_id, token, session)
            if channel_id:
                url = f"https://discord.com/api/v9/channels/{channel_id}/invites"
                data = {"max_age": 0, "max_uses": 0}
                async with session.post(url, headers=self.headers(token), json=data, ssl=False) as response:
                    if response.status == 200:
                        result = await response.json()
                        code = result.get("code")
                        print(f'{Fore.GREEN}[ + ] - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Создал: {token[:6]}... инвайт: https://discord.gg/{code}...')
                    elif response.status == 429:
                        result = await response.json()
                        retry_after = result.get("retry_after")
                        print(Fore.RED + f'[ ~ ] Лимит запросов превышен. Повтор через {retry_after:.2f} секунд.')
                        await asyncio.sleep(retry_after + 1)
                    else:
                        print(f'{Fore.RED}{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Ошибка: {token[:6]}... При создании инвайта, статус: {response.status}')  
        except Exception as e:
            print(f"FAILED: {e}")

    async def create_invites(self, guild_id):
        async with aiohttp.ClientSession() as session:
            while True:
                tasks = []
                for token in self.tokens:
                    task = asyncio.create_task(self.create_invite(token, guild_id, session))
                    tasks.append(task)
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                self.tokens = [token for token, result in zip(self.tokens, results) if result is None]

if __name__ == "__main__":
    invite_creator = AccountInviteCreator()
    guild_id = input(Fore.RED + "Введите идентификатор сервера: ") 
    
    asyncio.run(invite_creator.create_invites(guild_id))