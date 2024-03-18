if __name__ != '__main__':
    raise ImportError('This module cannot be imported from outside.')

from Logger import Logger
from ChromeController import ChromeController
from EdgeController import EdgeController
from FirefoxController import FirefoxController

import signal
from time import sleep

from DetoxifySentences import load_model_detoxify

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

load_model_detoxify()

firefoxController.start()
chromeController.start()
edgeController.start()

while not shouldTerminate:
    sleep(0.1)

Logger.warn(f'shouldTerminate: {shouldTerminate}, All modules will be terminated soon.')
firefoxController.join()
Logger.warn('Firefox controller is terminated.')
chromeController.join()
Logger.warn('Chrome controller is terminated.')
edgeController.join()
Logger.warn('Edge controller is terminated.')