import threading
import pathlib
import json
from selenium import webdriver
from selenium.webdriver.firefox.service import Service

from Logger import Logger

from URLTracker import URLTracker

class FirefoxController():

    def __init__(self) -> 'FirefoxController':
        super().__init__()
        self.__driver: webdriver.Firefox = None
        self.__thread = threading.Thread(target=self.__process, args=())
        self.__ip: str = ''
        self.__port: int = 0
        self.__webdriverPath: str = ''
        self.__path: pathlib.Path = pathlib.Path(
            str(pathlib.Path(__file__).parent.parent) + '/config/FirefoxController.json')
        self.__config: dict = None
        self.__readConfigFile()
        self.__configureController()

    def __connect(self) -> None:
        firefoxService = Service(executable_path=self.__webdriverPath, port=3000, service_args=[
                                 '--marionette-port', str(self.__port), '--connect-existing'])
        while True:
            try:
                self.__driver = webdriver.Firefox(service=firefoxService)
                Logger.warn('Connected to Mozilla Firefox!')
                return
            except:
                Logger.warn(
                    f'Could not connect to Mozilla Firefox, retrying...')
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
        tracker = URLTracker(self.__driver)
        tracker.track_new_tabs()

    def start(self) -> None:
        self.__thread.start()

    def join(self) -> None:
        self.__thread.join()
