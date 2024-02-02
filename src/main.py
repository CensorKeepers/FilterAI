if __name__ != '__main__':
    raise ImportError('This module cannot be imported from outside.')

from Logger import Logger
from ChromeController import ChromeController
from EdgeController import EdgeController
from FirefoxController import FirefoxController

utilityObjects = []
utilityObjects.append(Logger())

chromeController: ChromeController = ChromeController()
edgeController: EdgeController = EdgeController()
firefoxController: FirefoxController = FirefoxController()

chromeController.start()
edgeController.start()
firefoxController.start()

chromeController.join()
edgeController.join()
firefoxController.join()
