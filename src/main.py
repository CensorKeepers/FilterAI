if __name__ != '__main__':
    raise ImportError('This module cannot be imported from outside.')

from Logger import Logger
from ChromeController import ChromeController
from EdgeController import EdgeController
from FirefoxController import FirefoxController

import signal
from time import sleep


def signalHandler(sig, frame):
    global shouldTerminate
    Logger.warn('SIGINT Received.')
    edgeController.shouldTerminate()
    chromeController.shouldTerminate()
    firefoxController.shouldTerminate()
    shouldTerminate = True


signal.signal(signal.SIGINT, signalHandler)

shouldTerminate: bool = False

utilityObjects = []
utilityObjects.append(Logger())

chromeController: ChromeController = ChromeController()
edgeController: EdgeController = EdgeController()
firefoxController: FirefoxController = FirefoxController()

chromeController.start()
edgeController.start()
firefoxController.start()

while not shouldTerminate:
    sleep(0.1)

Logger.warn(f'shouldTerminate: {shouldTerminate}, All modules will be terminated soon.')
chromeController.join()
Logger.warn('Chrome is terminated.')
edgeController.join()
Logger.warn('Edge is terminated.')
firefoxController.join()
Logger.warn('Firefox is terminated.')
