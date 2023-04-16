import telegram
from app import app
from threading import Thread


class FlaskThread(Thread):
    def run(self) -> None:
        app.run(host = "127.0.0.1", port = 8000)

class TelegramThread(Thread):
    def run(self) -> None:
        telegram.bot.infinity_polling()


if __name__ == '__main__':
    flask_t = FlaskThread()
    flask_t.start()
    tgbot_t = TelegramThread()
    tgbot_t.start()