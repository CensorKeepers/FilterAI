import threading
import pathlib
import json
from selenium import webdriver
from selenium.webdriver.edge.options import Options

from Logger import Logger

from URLTracker import URLTracker

class EdgeController():

    def __init__(self) -> 'EdgeController':
        super().__init__()
        self.__driver: webdriver.Edge = None
        self.__thread = threading.Thread(target=self.__process, args=())
        self.__ip: str = ''
        self.__port: int = 0
        self.__webdriverPath: str = ''
        self.__path: pathlib.Path = pathlib.Path(
            str(pathlib.Path(__file__).parent.parent) + '/config/EdgeController.json')
        self.__config: dict = None
        self.__readConfigFile()
        self.__configureController()

    def __connect(self) -> None:
        edgeOptions = Options()
        edgeOptions.add_experimental_option(
            'debuggerAddress', f'{self.__ip}:{self.__port}')
        while True:
            try:
                self.__driver = webdriver.Edge(options=edgeOptions)
                Logger.warn('Connected to Microsoft Edge!')
                return
            except:
                Logger.warn(
                    f'Could not connect to Microsoft Edge, retrying...')
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
