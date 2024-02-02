import threading
import json
import pathlib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from Logger import Logger


class ChromeController():

    def __init__(self) -> 'ChromeController':
        super().__init__()
        self.__driver: webdriver.Chrome = None
        self.__thread = threading.Thread(target=self.__process, args=())
        self.__ip: str = ''
        self.__port: int = 0
        self.__webdriverPath: str = ''
        self.__path: pathlib.Path = pathlib.Path(
            str(pathlib.Path(__file__).parent.parent) + '/config/ChromeController.json')
        self.__config: dict = None
        self.__readConfigFile()
        self.__configureController()

    def __connect(self) -> None:
        chromeOptions = Options()
        chromeOptions.add_experimental_option(
            'debuggerAddress', f'{self.__ip}:{self.__port}')
        while True:
            try:
                self.__driver = webdriver.Chrome(options=chromeOptions)
                Logger.warn('Connected to Google Chrome!')
                return
            except:
                Logger.warn(
                    f'Could not connect to Google Chrome, retrying...')
                continue

    def __readConfigFile(self) -> None:
        file = open(self.__path, mode='r', encoding='utf-8')
        self.__config = json.load(file)
        file.close()

    def __configureController(self) -> None:
        self.__ip = self.__config['ip']
        self.__port = self.__config['port']
        self.__webdriverPath = self.__config['webdriverPath']

    def __process(self) -> None:
        self.__connect()
        self.__driver.get('https://www.google.com.tr')

    def start(self) -> None:
        self.__thread.start()

    def join(self) -> None:
        self.__thread.join()
