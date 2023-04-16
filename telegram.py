import telebot
import os
import sys
import datetime
from dbapi import DatabaseConnector

TOKEN = "6260187378:AAGuuzkGs8CqBvtagKeCITyUCtY5amY3ZXo"

db = DatabaseConnector()

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "Добро пожаловать в чат бота библиотеки! Для просмотра списка доступных команд введите /help")

#----------------------------------------------------------------------------------

@bot.message_handler(commands=['add'])
def add_book(message):

    bot.send_message(message.chat.id, "Введите название книги:")

    @bot.message_handler(content_types=['text'])
    def add_title(message):
        title = message.text

        bot.send_message(message.chat.id, "Введите автора:")

        @bot.message_handler(content_types=['text'])
        def add_author(message):
            author = message.text

            bot.send_message(message.chat.id, "Введите год издания:")

            @bot.message_handler(content_types=['text'])
            def add_year(message):
                year = message.text

                try:
                    datetime.datetime(int(year), 1, 1)
                    book_id = db.add(title, author, year)
                    bot.send_message(message.chat.id, f"Книга добавлена (id {book_id})")
                    return
                except:
                    bot.send_message(message.chat.id, "Ошибка при добавлении книги. Возможная ошибка - некорректно введенный год")
                    return

            bot.register_next_step_handler(message, add_year)

        bot.register_next_step_handler(message, add_author)

    bot.register_next_step_handler(message, add_title)

#----------------------------------------------------------------------------------

@bot.message_handler(commands=['delete'])
def delete_book(message):

    bot.send_message(message.chat.id, "Введите название книги:")

    @bot.message_handler(content_types=['text'])
    def delete_title(message):
        title = message.text
        bot.send_message(message.chat.id, "Введите автора:")

        @bot.message_handler(content_types=['text'])
        def delete_author(message):
            author = message.text
            bot.send_message(message.chat.id, "Введите год издания:")

            @bot.message_handler(content_types=['text'])
            def delete_year(message):
                year = message.text
                try:
                    book_id = db.get_book(title, author, year)
                    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
                    keyboard.add('Да', 'Нет')
                    bot.send_message(message.chat.id, f"Найдена книга: {title} {author} {year}. Удаляем?", reply_markup=keyboard)

                    @bot.message_handler(content_types=['text'])
                    def delete_book_confirm(message):
                        if message.text == 'Да':
                            for item in book_id:
                                db.delete(item)
                            bot.send_message(message.chat.id, "Книга удалена.")
                            return
                        else:
                            bot.send_message(message.chat.id, "Невозможно удалить книгу.")
                            return

                    bot.register_next_step_handler(message, delete_book_confirm)

                except:
                    bot.send_message(message.chat.id, "Книга не найдена.")
                    return
            
            bot.register_next_step_handler(message, delete_year)

        bot.register_next_step_handler(message, delete_author)

    bot.register_next_step_handler(message, delete_title)

#----------------------------------------------------------------------------------

@bot.message_handler(commands=['list'])
def list_books(message):
    books = db.list_books()
    wrd = ''
    values_list = list(books.values())
    for i in range(len(next(iter(values_list)))):
        curr = []
        for inner_dict in values_list:
            curr.append(list(inner_dict.values())[i])
        if curr[3] != None:
            wrd += f'{curr[0]}, {curr[1]}, {curr[2]} (удалена);\n'
        else:
            wrd += f'{curr[0]}, {curr[1]}, {curr[2]};\n'

    bot.send_message(message.chat.id, wrd)
    return

#----------------------------------------------------------------------------------

@bot.message_handler(commands=['find'])
def find_book(message):

    bot.send_message(message.chat.id, "Введите название книги:")

    @bot.message_handler(content_types=['text'])
    def find_title(message):
        title = message.text

        bot.send_message(message.chat.id, "Введите автора:")

        @bot.message_handler(content_types=['text'])
        def find_author(message):
            author = message.text

            bot.send_message(message.chat.id, "Введите год издания:")

            @bot.message_handler(content_types=['text'])
            def find_year(message):
                year = message.text

                try:
                    db.get_book(title, author, year)
                    bot.send_message(message.chat.id, f"Найдена книга: {title} {author} {year}")
                    return
                except:
                    bot.send_message(message.chat.id, "Такой книги у нас нет")
                    return

            bot.register_next_step_handler(message, find_year)

        bot.register_next_step_handler(message, find_author)

    bot.register_next_step_handler(message, find_title)

#----------------------------------------------------------------------------------

@bot.message_handler(commands=['borrow'])
def borrow_book(message):

    bot.send_message(message.chat.id, "Введите название книги:")

    @bot.message_handler(content_types=['text'])
    def borrow_title(message):
        title = message.text
        bot.send_message(message.chat.id, "Введите автора:")

        @bot.message_handler(content_types=['text'])
        def borrow_author(message):
            author = message.text
            bot.send_message(message.chat.id, "Введите год издания:")

            @bot.message_handler(content_types=['text'])
            def borrow_year(message):
                year = message.text

                try:
                    book_id = db.get_book(title, author, year)
                    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
                    keyboard.add('Да', 'Нет')
                    bot.send_message(message.chat.id, f"Найдена книга: {title} {author} {year}. Берем", reply_markup=keyboard)

                    @bot.message_handler(content_types=['text'])
                    def borrow_book_confirm(message):
                        if message.text == 'Да':
                            id = db.borrow(book_id, message.chat.id)
                            if id == False:
                                bot.send_message(message.chat.id, f"Книгу нельзя взять")
                            else:
                                bot.send_message(message.chat.id, f"Вы взяли книгу {id}")
                            return
                        else:
                            return

                    bot.register_next_step_handler(message, borrow_book_confirm)

                except:
                    bot.send_message(message.chat.id, "Книгу сейчас невозможно взять") 
                    return

            bot.register_next_step_handler(message, borrow_year)

        bot.register_next_step_handler(message, borrow_author)

    bot.register_next_step_handler(message, borrow_title)

#----------------------------------------------------------------------------------

@bot.message_handler(commands=['retrieve'])
def retrieve_book(message):
    try:
        dict = db.retrieve(message.chat.id)
        curr = []
        for i in dict:
            curr.append(dict[i][0])
        bot.send_message(message.chat.id, f"Вы вернули книгу {curr[0]} {curr[1]} {curr[2]}")
        return

    except:
        return

#----------------------------------------------------------------------------------

@bot.message_handler(commands=['stats'])
def stats_book(message):

    bot.send_message(message.chat.id, "Введите название книги:")

    @bot.message_handler(content_types=['text'])
    def stats_title(message):
        title = message.text

        bot.send_message(message.chat.id, "Введите автора:")

        @bot.message_handler(content_types=['text'])
        def stats_author(message):
            author = message.text

            bot.send_message(message.chat.id, "Введите год издания:")

            @bot.message_handler(content_types=['text'])
            def stats_year(message):
                year = message.text

                try:
                    book_id = db.get_book(title, author, year)
                    bot.send_message(message.chat.id, f"Статистика доступна по адресу: http://127.0.0.1:8000/download/{book_id[0]}")
                    return
                except Exception as e:
                    print(e)
                    bot.send_message(message.chat.id, "Нет такой книги")
                    return

            bot.register_next_step_handler(message, stats_year)

        bot.register_next_step_handler(message, stats_author)

    bot.register_next_step_handler(message, stats_title)

#----------------------------------------------------------------------------------

@bot.message_handler(commands=['help'])
def send_help(message):
    commands_list = ['/start - начать работу', '/restart - перезапуск бота', '/add - добавить книгу', '/delete - удалить книгу', '/list - открыть список книг', 
        '/find - найти книгу', '/borrow - взять книгу', '/retrieve - вернуть книгу', '/stats - посмотреть статистику']
    bot.send_message(message.chat.id, '\n'.join(commands_list))

#----------------------------------------------------------------------------------

@bot.message_handler(commands=['restart'])
def restart_bot(message):
    bot.send_message(message.chat.id, "Перезапуск бота...")
    os.execl(sys.executable, sys.executable, *sys.argv)

#----------------------------------------------------------------------------------
