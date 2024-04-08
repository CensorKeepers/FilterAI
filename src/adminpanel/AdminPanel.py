if __name__ != '__main__':
    raise ImportError('This module cannot be imported from outside.')

import tkinter as tk
from tkinter import font
import json
import pathlib
import socket
from DetoxifySentences import load_model_detoxify, predict
from enum import StrEnum
from typing import List, Dict


class Client():
    def __init__(self, ip: str) -> 'Client':
        self.__ip: str = ip
        self.__port: int = 0

    def setPort(self, port: int) -> None:
        self.__port = port


class Server():
    def __init__(self, clientIp: str, port: int) -> 'Server':
        self.__ip: str = self.__findIp()
        self.__clientIp: str = clientIp
        self.__port: int = port

    def __findIp(self) -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            s.connect(('10.254.254.254', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()

        return ip

    def getClientIp(self) -> str:
        return self.__clientIp


class FilterStyle(StrEnum):
    BLUR = 'blur'
    CONFUSCATION = 'confuscation'
    RED_HIGHLIGHT = 'redHightlight'
    RED_LINE = 'redLine'


class AdminPanel():
    def __init__(self) -> 'AdminPanel':
        self.__configPath: pathlib.Path = pathlib.Path(str(pathlib.Path(__file__).parent.parent.parent) + '/config/AdminPanel.json')
        self.__config: dict = None
        self.__connectionDict: Dict[Server, List[Client]] = {}
        self.__shouldLoadLLMOnStart: bool = False
        self.__isChatGPTEnabled: bool = False
        self.__filterStyle: FilterStyle = None
        self.__openAiApiKey: str = None
        self.__root: tk.Tk = None
        self.__servicesStatusLabel: tk.Label = None
        self.__LLMStatusLabel: tk.Label = None
        self.__ChatGPTStatusLabel: tk.Label = None
        self.__filterStyleStatusLabel: tk.Label = None
        self.__readAndApplyConfigFile()
        self.__configureAdminPanel()
        self.__makeGUI()

    def __readAndApplyConfigFile(self) -> None:
        file = open(self.__configPath, mode='r', encoding='utf-8')
        self.__config = json.load(file)
        file.close()

    def __configureAdminPanel(self) -> None:
        self.__shouldLoadLLMOnStart = self.__config['loadLLMOnStart']
        self.__isChatGPTEnabled = self.__config['ChatGPT']
        self.__filterStyle = self.__config['filterMode']

        clients: List[Dict[str, int]] = self.__config['clients']
        for obj in clients:
            clientIp = obj['clientIp']
            serverPort = obj['serverPort']
            server = Server(clientIp, serverPort)
            self.__connectionDict[server] = []

    def __makeGUI(self) -> None:
        WINDOW_WIDTH = 1400
        WINDOW_HEIGHT = 800
        self.__root = tk.Tk()
        self.__root.title(self.__config['windowName'])
        self.__root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}')

        topPanel = tk.Frame(self.__root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT // 8, bg="black")
        topPanel.pack(side='top', fill='x')

        labelFont = font.Font(size=20)
        label1 = tk.Label(topPanel, text="Services:", fg="white", bg="black", font=labelFont)
        label1.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        self.__servicesStatusLabel = tk.Label(topPanel, text="Not Running", fg="red", bg="black", font=labelFont)
        self.__servicesStatusLabel.grid(row=0, column=1, padx=10, pady=20)
        label2 = tk.Label(topPanel, text="Language Model:", fg="white", bg="black", font=labelFont)
        label2.grid(row=0, column=2, padx=20, pady=10, sticky="w")
        self.__LLMStatusLabel = tk.Label(topPanel, text="Not Running", fg="red", bg="black", font=labelFont)
        self.__LLMStatusLabel.grid(row=0, column=3, padx=10, pady=20)
        label3 = tk.Label(topPanel, text="ChatGPT:", fg="white", bg="black", font=labelFont)
        label3.grid(row=0, column=4, padx=20, pady=10, sticky="w")
        self.__ChatGPTStatusLabel = tk.Label(topPanel, text="Disabled", fg="red", bg="black", font=labelFont)
        self.__ChatGPTStatusLabel.grid(row=0, column=5, padx=10, pady=20)
        label4 = tk.Label(topPanel, text="Filter Style:", fg="white", bg="black", font=labelFont)
        label4.grid(row=0, column=6, padx=20, pady=10, sticky="w")
        self.__filterStyleStatusLabel = tk.Label(topPanel, text=self.__config['filterMode'], fg="white", bg="black", font=labelFont)
        self.__filterStyleStatusLabel.grid(row=0, column=7, padx=10, pady=20)

        bottomPanel = tk.Frame(self.__root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT - (WINDOW_HEIGHT // 8), bg='#303030')
        bottomPanel.pack(side='bottom', fill='both', expand=True)

        buttonWidth = 40
        buttonHeight = 5
        buttonPadX = 25
        buttonPadY = 10
        button1 = tk.Button(bottomPanel, text='Start Services', bg='gray', width=buttonWidth, height=buttonHeight)
        button1.grid(row=0, column=0, padx=buttonPadX, pady=buttonPadY, sticky="we")
        button2 = tk.Button(bottomPanel, text='Stop Services', bg='gray', width=buttonWidth, height=buttonHeight)
        button2.grid(row=0, column=1, padx=buttonPadX, pady=buttonPadY, sticky="we")
        button3 = tk.Button(bottomPanel, text='Restart Services', bg='gray', width=buttonWidth, height=buttonHeight)
        button3.grid(row=0, column=2, padx=buttonPadX, pady=buttonPadY, sticky="we")
        button3 = tk.Button(bottomPanel, text='Force Stop Services', bg='#942828', width=buttonWidth, height=buttonHeight)
        button3.grid(row=0, column=3, padx=buttonPadX, pady=buttonPadY, sticky="we")

        button4 = tk.Button(bottomPanel, text='Change OPENAI API Key', bg='gray', width=buttonWidth, height=buttonHeight)
        button4.grid(row=1, column=0, padx=buttonPadX, pady=buttonPadY, sticky="we")
        button5 = tk.Button(bottomPanel, text='Enable ChatGPT', bg='gray', width=buttonWidth, height=buttonHeight)
        button5.grid(row=1, column=1, padx=buttonPadX, pady=buttonPadY, sticky="we")
        button6 = tk.Button(bottomPanel, text='Disable ChatGPT', bg='gray', width=buttonWidth, height=buttonHeight)
        button6.grid(row=1, column=2, padx=buttonPadX, pady=buttonPadY, sticky="we")

        button7 = tk.Button(bottomPanel, text='Manage Clients', bg='#2b47b8', width=buttonWidth, height=buttonHeight)
        button7.grid(row=2, column=0, padx=buttonPadX, pady=buttonPadY, sticky="we")
        button8 = tk.Button(bottomPanel, text='Change Settings', bg='gray', width=buttonWidth, height=buttonHeight)
        button8.grid(row=2, column=1, padx=buttonPadX, pady=buttonPadY, sticky="we")
        button9 = tk.Button(bottomPanel, text='Load Language Model', bg='gray', width=buttonWidth, height=buttonHeight)
        button9.grid(row=2, column=2, padx=buttonPadX, pady=buttonPadY, sticky="we")
        button10 = tk.Button(bottomPanel, text='Restart Language Model', bg='gray', width=buttonWidth, height=buttonHeight)
        button10.grid(row=2, column=3, padx=buttonPadX, pady=buttonPadY, sticky="we")

        label5 = tk.Label(bottomPanel, text="Filter Style:", fg="white", bg="#303030", font=labelFont)
        label5.grid(row=3, column=0, padx=20, pady=60, sticky="w")

        button11 = tk.Button(bottomPanel, text='Blur', bg='gray', width=buttonWidth, height=buttonHeight)
        button11.grid(row=4, column=0, padx=buttonPadX, pady=buttonPadY, sticky="we")
        button12 = tk.Button(bottomPanel, text='Confuscation', bg='gray', width=buttonWidth, height=buttonHeight)
        button12.grid(row=4, column=1, padx=buttonPadX, pady=buttonPadY, sticky="we")
        button13 = tk.Button(bottomPanel, text='Red Highlight', bg='gray', width=buttonWidth, height=buttonHeight)
        button13.grid(row=4, column=2, padx=buttonPadX, pady=buttonPadY, sticky="we")
        button14 = tk.Button(bottomPanel, text='Red Line', bg='gray', width=buttonWidth, height=buttonHeight)
        button14.grid(row=4, column=3, padx=buttonPadX, pady=buttonPadY, sticky="we")

    def mainloop(self) -> None:
        self.__root.mainloop()


gui = AdminPanel()
gui.mainloop()
