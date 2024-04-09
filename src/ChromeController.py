import threading
import pathlib
import json
import socket
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from Logger import Logger
from URLTracker import URLTracker

from time import sleep


class ChromeController():

    def __init__(self) -> 'ChromeController':
        self.__thread = threading.Thread(target=self.__process, args=())
        self.__tabThread = threading.Thread(target=self.__handleNewTabs, args=())
        self.__driver: webdriver.Chrome = None
        self.__webdriverPath: str = ''
        self.__webdriverIp: str = ''
        self.__webdriverPort: int = 0
        self.__remoteIp: str = None
        self.__remotePort: int = 0
        self.__socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__configPath: pathlib.Path = pathlib.Path(str(pathlib.Path(__file__).parent.parent) + '/config/ChromeController.json')
        self.__config: dict = None
        self.__shouldTerminate: bool = False
        self.__readAndApplyConfigFile()
        self.__configureController()

    def __connectToBrowser(self) -> bool:
        chromeOptions = Options()
        chromeOptions.add_experimental_option('debuggerAddress', f'{self.__webdriverIp}:{self.__webdriverPort}')

        while not self.__shouldTerminate:
            try:
                self.__driver = webdriver.Chrome(options=chromeOptions)
                Logger.warn('[CHROME]: Connected to Google Chrome!')
                return True
            except:
                Logger.warn(f'[CHROME]: Could not connect to Google Chrome, retrying...')
                continue

        return False

    def __readAndApplyConfigFile(self) -> None:
        file = open(self.__configPath, mode='r', encoding='utf-8')
        self.__config = json.load(file)
        file.close()

    def __configureController(self) -> None:
        self.__webdriverIp = self.__config['webdriverIp']
        self.__webdriverPort = self.__config['webdriverPort']
        self.__webdriverPath = self.__config['webdriverPath']
        self.__remoteIp = self.__config['remoteIp']
        self.__remotePort = self.__config['remotePort']

    def __process(self) -> None:
        if not self.__connectToBrowser():
            return

        while True:
            try:
                self.__socket.connect((self.__remoteIp, self.__remotePort))
                Logger.warn(f'[CHROME]: Connected to remote server {self.__remoteIp}:{self.__remotePort}.')
                break
            except:
                Logger.warn(f'[CHROME]: Could not connect to the remote server. Retrying...')
                continue

        self.__driver.get('https://www.google.com.tr')
        self.__tabThread.start()
        self.__tabThread.join()

        self.__driver.quit()

    def __handleNewTabs(self) -> None:
        tracker = URLTracker(self.__driver)
        while not self.__shouldTerminate:
            tracker.trackUrls()
            sleep(0)

    def start(self) -> None:
        self.__thread.start()
        Logger.warn('[CHROME]: Chrome controller has been started.')

    def join(self) -> None:
        self.__thread.join()

    def shouldTerminate(self) -> None:
        self.__shouldTerminate = True
