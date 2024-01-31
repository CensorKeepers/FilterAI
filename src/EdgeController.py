import threading
from selenium import webdriver
from selenium.webdriver.edge.options import Options

from Logger import Logger


class EdgeController():

    def __init__(self) -> 'EdgeController':
        super().__init__()
        self.__driver: webdriver.Edge = None
        self.__thread = threading.Thread(target=self.__process, args=())

    def __connect(self) -> None:
        edgeOptions = Options()
        edgeOptions.add_experimental_option(
            'debuggerAddress', '127.0.0.1:9922')
        while True:
            try:
                self.__driver = webdriver.Edge(options=edgeOptions)
                Logger.warn('Connected to Microsoft Edge!')
                return
            except:
                Logger.warn(
                    f'Could not connect to Microsoft Edge, retrying...')
                continue

    def __process(self) -> None:
        self.__connect()
        Logger.warn('Closing the Edge.')
        self.__driver.quit()

    def start(self) -> None:
        self.__thread.start()

    def join(self) -> None:
        self.__thread.join()
