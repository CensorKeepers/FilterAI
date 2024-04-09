if __name__ != '__main__':
    raise ImportError('This module cannot be imported from outside.')

from Logger import Logger
from ChromeController import ChromeController
from EdgeController import EdgeController
from FirefoxController import FirefoxController
from DetoxifySentences import load_model_detoxify
import json
import pathlib
import signal
import socket
from time import sleep


def signalHandler(sig, frame):
    global shouldTerminate
    Logger.warn('SIGINT Received.')
    edgeController.shouldTerminate()
    chromeController.shouldTerminate()
    firefoxController.shouldTerminate()
    shouldTerminate = True


signal.signal(signal.SIGINT, signalHandler)
load_model_detoxify()

shouldTerminate: bool = False

utilityObjects = []
utilityObjects.append(Logger())

chromeController: ChromeController = ChromeController()
edgeController: EdgeController = EdgeController()
firefoxController: FirefoxController = FirefoxController()

configPath: pathlib.Path = pathlib.Path(str(pathlib.Path(__file__).parent.parent) + '/config/Application.json')
file = open(configPath, mode='r', encoding='utf-8')
config = json.load(file)
file.close()

SERVER_IP = config['remoteIp']
SERVER_PORT = config['remotePort']

isClosed = True
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

while True:
    try:
        clientSocket.connect((SERVER_IP, SERVER_PORT))
        Logger.warn(f'[MAIN]: Connected to server {SERVER_IP}:{SERVER_PORT}.')
    except:
        break

while not shouldTerminate:

    if isClosed:
        while True:
            try:
                byte = clientSocket.recv(1).decode()
                if byte == '1':
                    Logger.warn(f'[MAIN]: Server has started the service.')
                    isClosed = False
                    break
            except:
                Logger.warn(f'[MAIN]: Waiting signal from server to start controllers.')
                continue

    firefoxController.start()
    chromeController.start()
    edgeController.start()

    while True:
        try:
            byte = clientSocket.recv(1).decode()
            if byte == '0':
                Logger.warn(f'[MAIN]: Server has closed the service.')
                isClosed = True
                break
        except:
            continue

    firefoxController.join()
    Logger.warn('Firefox controller is terminated.')
    chromeController.join()
    Logger.warn('Chrome controller is terminated.')
    edgeController.join()
    Logger.warn('Edge controller is terminated.')


Logger.warn(f'shouldTerminate: {shouldTerminate}, All modules will be terminated soon.')
firefoxController.join()
Logger.warn('Firefox controller is terminated.')
chromeController.join()
Logger.warn('Chrome controller is terminated.')
edgeController.join()
Logger.warn('Edge controller is terminated.')
clientSocket.close()
