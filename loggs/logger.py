import logging


class Log:
    def __init__(self, name):
        self.log = logging.getLogger(name)
        self.log.setLevel(logging.DEBUG)

        handler = logging.FileHandler('logs.log')
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        if not self.log.handlers:
            self.log.addHandler(handler)

    def info(self, message):
        self.log.info(message)

    def error(self, message):
        self.log.error(message)
