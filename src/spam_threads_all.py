import aiohttp
import os
import asyncio
import time
from datetime import datetime
from colorama import Fore, init

init(autoreset=True)

class DiscordThreadCreator:
    def __init__(self):
        self.tokens = []
        self.load_tokens()

    def load_tokens(self):
        if not os.path.isfile('tokens.txt'):
            with open('tokens.txt', 'w') as f:
                f.write('')  
        else:
            with open('tokens.txt', 'r') as f:
                self.tokens = [t.strip() for t in f.read().splitlines() if t.strip()]
            if not self.tokens:
                print("Файл tokens.txt пуст.")

    async def create_single_thread(self, session, token, channel_id, name):
        """Создаёт одну ветку с повторными попытками при рейтлимите"""
        headers = {'authorization': token, 'Content-Type': 'application/json'}
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                async with session.post(
                    f'https://discord.com/api/v9/channels/{channel_id}/threads',
                    headers=headers,
                    json={'name': name, 'auto_archive_duration': 1440, 'type': 11},
                    ssl=False
                ) as response:
                    status = response.status
                    
                    if status in [200, 201]:
                        return True, None
                    
                    elif status == 403:
                        error_msg = f'Доступ запрещен для токена: {token[:6]}...'
                        return False, error_msg
                    
                    elif status == 429:
                        try:
                            data = await response.json()
                            retry_after = data.get('retry_after', 5)
                            print(f'{Fore.RED}Рейтлимит для {token[:6]}..., ожидание {retry_after:.1f} сек... (попытка {attempt + 1}/{max_retries})')
                            await asyncio.sleep(retry_after)
                            continue
                        except Exception as e:
                            print(f'{Fore.RED}Ошибка обработки рейтлимита: {e}')
                            await asyncio.sleep(5)
                            continue
                    
                    else:
                        error_msg = f'Ошибка статус {status} для токена {token[:6]}...'
                        return False, error_msg
            
            except aiohttp.ClientError as e:
                print(f'{Fore.RED}Ошибка сети (попытка {attempt + 1}/{max_retries}): {e}')
                await asyncio.sleep(2)
                continue
            except Exception as e:
                error_msg = f'Неожиданная ошибка: {e}'
                return False, error_msg
        
        return False, f'Превышено количество попыток для {token[:6]}...'

    async def create_threads(self, channel_id, name, total_threads_required):
        if not self.tokens:
            print("Нет доступных токенов для использования.")
            return
        
        import aiohttp
        
        total_created_threads = 0
        failed_tokens = set()
        
        async with aiohttp.ClientSession() as session:
            token_index = 0
            consecutive_failures = 0
            
            while total_created_threads < total_threads_required:
                available_tokens = [t for t in self.tokens if t not in failed_tokens]
                
                if not available_tokens:
                    print(f'{Fore.RED}Все токены исчерпаны или заблокированы.')
                    break
                
                token = available_tokens[token_index % len(available_tokens)]
                
                success, error = await self.create_single_thread(session, token, channel_id, name)
                
                if success:
                    total_created_threads += 1
                    consecutive_failures = 0
                    print(f'{Fore.GREEN}[{total_created_threads}/{total_threads_required}] Успешно создана ветка: {token[:6]}...')
                    await asyncio.sleep(0.5)
                else:
                    if error:
                        print(f'{Fore.RED}{error}')
                    
                    if 'Доступ запрещен' in error or 'Превышено количество попыток' in error:
                        failed_tokens.add(token)
                        print(f'{Fore.RED}Токен {token[:6]}... исключён из дальнейшей работы')
                    
                    consecutive_failures += 1
                    
                    if consecutive_failures >= len(available_tokens) * 2:
                        print(f'{Fore.RED}Слишком много неудачных попыток подряд. Завершение...')
                        break
                
                token_index += 1
                
                if token_index > total_threads_required * 10:
                    print(f'{Fore.RED}Превышен лимит итераций. Возможно, проблема с доступом.')
                    break
        
        print(f'\n{Fore.GREEN}{"="*50}')
        print(f'{Fore.GREEN}[ + ] - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print(f'{Fore.GREEN}Завершено! Создано {total_created_threads}/{total_threads_required} веток')
        print(f'{Fore.GREEN}{"="*50}\n')
        
        input(Fore.RED + "Нажмите Enter, чтобы продолжить...")
        self.clear_console()
        os.system('python main.py')

    @staticmethod
    def clear_console():
        os.system('cls' if os.name == 'nt' else 'clear')

    def main_menu(self):
        print(Fore.RED + "Возврат в главное меню...")
        time.sleep(1)

    def run(self):
        try:
            channel_id = input(Fore.RED + "Укажите ID канала: ").strip()
            name = input(Fore.RED + "Введите имя для веток: ").strip()
            
            if not name:
                name = "Новая ветка"
            
            while True:
                try:
                    total_threads = int(input(Fore.RED + "Сколько веток создать? (от 1 до 50): "))
                    if 1 <= total_threads <= 50:
                        break
                    else:
                        print(Fore.RED + "Пожалуйста, введите число от 1 до 50.")
                except ValueError:
                    print(Fore.RED + "Пожалуйста, введите допустимое число.")
            
            print(f'\n{Fore.CYAN}Начинаю создание {total_threads} веток...\n')
            asyncio.run(self.create_threads(channel_id, name, total_threads))
            
        except KeyboardInterrupt:
            print(f'\n{Fore.RED}Прервано пользователем.')
        except Exception as e:
            print(f"{Fore.RED}Критическая ошибка: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    discord_thread_creator = DiscordThreadCreator()
    discord_thread_creator.run()