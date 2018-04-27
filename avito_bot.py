import requests
from bs4 import BeautifulSoup
import json
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import sqlite3

WAIT = 60
TOKEN = open('token.txt', 'r').read()
URL = 'https://www.domofond.ru/arenda-nedvizhimosti/search?RegionId=81&GeographicPolygon=%5B%5B55.79678%2C37.49796%5D%2C%5B55.79639%2C37.49985%5D%2C%5B55.79591%2C37.50517%5D%2C%5B55.79571%2C37.51736%5D%2C%5B55.79639%2C37.52319%5D%2C%5B55.79736%2C37.52731%5D%2C%5B55.79871%2C37.5304%5D%2C%5B55.80335%2C37.5383%5D%2C%5B55.80702%2C37.54036%5D%2C%5B55.81601%2C37.53967%5D%2C%5B55.82056%2C37.53727%5D%2C%5B55.83022%2C37.52903%5D%2C%5B55.83708%2C37.52594%5D%2C%5B55.84172%2C37.52439%5D%2C%5B55.84529%2C37.5213%5D%2C%5B55.8478%2C37.51839%5D%2C%5B55.85186%2C37.51135%5D%2C%5B55.8535%2C37.50671%5D%2C%5B55.85456%2C37.50105%5D%2C%5B55.85572%2C37.47702%5D%2C%5B55.85553%2C37.4741%5D%2C%5B55.85408%2C37.46878%5D%2C%5B55.85234%2C37.46637%5D%2C%5B55.85021%2C37.46483%5D%2C%5B55.84799%2C37.46466%5D%2C%5B55.84336%2C37.46672%5D%2C%5B55.83631%2C37.47221%5D%2C%5B55.83399%2C37.47341%5D%2C%5B55.82616%2C37.47599%5D%2C%5B55.8221%2C37.4777%5D%2C%5B55.81785%2C37.4789%5D%2C%5B55.80896%2C37.48011%5D%2C%5B55.80683%2C37.48079%5D%2C%5B55.80161%2C37.48457%5D%2C%5B55.7991%2C37.48749%5D%2C%5B55.79784%2C37.49041%5D%2C%5B55.79571%2C37.49899%5D%2C%5B55.79591%2C37.50311%5D%5D&PropertyType=Room&PriceFrom=10000&RentalRate=Month&Mapped=True'
URL = 'https://www.avito.ru/rossiya/noutbuki?q=lenovo%20thinkpad%20x1%20carbon&sgtd=21'
CHAT_ID = '75113933'
FILE_JSON = 'ad.json'


def create_db():
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS links (id INTEGER PRIMARY KEY AUTOINCREMENT , url MESSAGE_TEXT, chat_id INTEGER NOT NULL, FOREIGN KEY (chat_id) REFERENCES users(chat_id) ON DELETE CASCADE );')
    cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT , chat_id INTEGER UNIQUE );')
    con.commit()
    con.close()


def get_all_url_avito():
    r = requests.get(URL)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    list_url = []
    for url in (soup.find_all('div', attrs={'class': 'item item_table clearfix js-catalog-item-enum '})):
        list_url.append(url.find('a', attrs={'class': 'item-description-title-link'})['href'])
    return list_url


def get_all_url_domofond():
    # Добить проверку новых объявлений
    r = requests.get(URL)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    list_url = []
    for url in (soup.find_all('div', attrs={'class': 'b-results-tile'})):
        print(url)


def get_new_url(current_url, site):
    if site == 'https://www.avito.ru':
        diff_url = get_all_url_avito()
        for url in diff_url:
            if url not in current_url:
                with open(FILE_JSON, 'w') as f:
                    json.dump(diff_url, f)
                return 'https://www.avito.ru' + url
    if site == 'https://domofond.ru':
        pass


def create_chat_id_file(chat_id, filter):

    pass


def callback(bot, job):
    site = 'https://www.avito.ru'  # необходимо реализовать проверку с Домофондом или Авито
    url = get_new_url(json.load(open(FILE_JSON)), site)
    if url:
        bot.send_message(chat_id=job.context, text=url)


def bot_help(bot, update):
    print(update.message.chat_id)
    bot.send_message(chat_id=update.message.chat_id, text='Тут будет помощь')


def bot_start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='Для работы Вам необходимо прислать мне ссылку')


def bot_list(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='Список подписок')
    # Берем json из файла


def bot_rule(bot, update, job_queue):
    chat_id = update.message.chat_id
    url = update.message.text
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute("INSERT INTO users (chat_id) VALUES ('%s')" % chat_id)
    # основная логика описанная в help
    if cur.execute("SELECT * FROM links WHERE url = '%s'" % url).fetchall():
        cur.execute("DELETE FROM links WHERE url = '%s'" % url)
    else:
        cur.execute("INSERT INTO links (url, chat_id) VALUES ('%s', (select id from users WHERE  chat_id = '%s'))" % (url, chat_id))
        job_queue.run_repeating(callback, interval=WAIT, first=0)


    con.commit()
    con.close()


    # написать логику проверки ссылок
    # и создания файлов если их нет





def start():
    u = Updater(TOKEN)
    dispatcher = u.dispatcher
    handlers = []
    # initial handlers
    handlers.append(CommandHandler('help', bot_help))
    handlers.append(CommandHandler('start', bot_start))
    handlers.append(CommandHandler('list', bot_list))
    handlers.append(MessageHandler(Filters.text, bot_rule, pass_job_queue=True))

    for handler in handlers:
        dispatcher.add_handler(handler)
    '''
    j = u.job_queue
    j.run_repeating(callback, interval=WAIT, first=0)
    '''
    u.start_polling()
    u.idle()

if __name__ == '__main__':
    import logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
    create_db()
    start()