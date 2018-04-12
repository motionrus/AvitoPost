import requests
from bs4 import BeautifulSoup
import json
from telegram.ext import Updater

WAIT = 300
TOKEN = open('token.txt', 'r').read()
URL = 'https://www.avito.ru/moskva/noutbuki?s=104&q=lenovo+x1+carbon'
CHAT_ID = '75113933'
FILE_JSON = 'ad.json'


def get_all_url():
    r = requests.get(URL)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    list_url = []
    for url in (soup.find_all('div', attrs={'class': 'item item_table clearfix js-catalog-item-enum '})):
        list_url.append(url.find('a', attrs={'class': 'item-description-title-link'})['href'])
    return list_url


def get_new_url(current_url):
    diff_url = get_all_url()
    for url in diff_url:
        if url not in current_url:
            with open(FILE_JSON, 'w') as f:
                json.dump(diff_url, f)
            return 'http://avito.ru' + url


def callback(bot, job):
    url = get_new_url(json.load(open(FILE_JSON)))
    if url:
        bot.send_message(chat_id=CHAT_ID, text=url)


if __name__ == '__main__':
    u = Updater(TOKEN)
    j = u.job_queue
    j.run_repeating(callback, interval=WAIT, first=0)
    u.start_polling()
    u.idle()
