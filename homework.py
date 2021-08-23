import os
import datetime
import logging
import time
import requests
import telegram

from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('my_logger.log', maxBytes=50000000, backupCount=5)
logger.addHandler(handler)

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# проинициализируйте бота здесь,
# чтобы он был доступен в каждом нижеобъявленном методе,
# и не нужно было прокидывать его в каждый вызов
bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    if homework['status'] == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    proxies = {"https": "80.152.180.204:8080"}
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    homework_statuses = requests.get(url, headers=headers, params=payload, proxies=proxies)
    return homework_statuses.json()


def send_message(message):
    return bot.send_message(CHAT_ID, message)


def main():
    # current_timestamp = int(time.time())  # Начальное значение timestamp
    current_timestamp = int(datetime.datetime.timestamp(
        datetime.datetime.now() - datetime.timedelta(days=30)))
    while True:
        try:
            logger.debug('Отслеживание статуса запущено')
            send_message(
                parse_homework_status(
                    get_homeworks(current_timestamp)['homeworks'][0]
                )
            )
            logger.info('Бот отправил сообщение')
            time.sleep(5 * 60)  # Опрашивать раз в пять минут

        except Exception as e:
            error_message = f'Бот упал с ошибкой: {e}'
            logger.error(error_message)
            bot.send_message(CHAT_ID, error_message)
            time.sleep(5)


if __name__ == '__main__':
    main()
