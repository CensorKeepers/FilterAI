if __name__ != '__main__':
    raise ImportError('This module cannot be imported from outside.')

import tkinter as tk
from tkinter import font
import json
import pathlib
import socket
from enum import StrEnum
from typing import List, Dict
import threading
import sys
import os
from time import sleep


class Client():
    def __init__(self, ip: str, port: int) -> 'Client':
        self.__ip: str = ip
        self.__port: int = port

    def getIp(self) -> str:
        return self.__ip

    def setIp(self, ip: str) -> None:
        self.__ip = ip

    def getPort(self) -> int:
        return self.__port

    def setPort(self, port: int) -> None:
        self.__port = port


class Server():
    def __init__(self, clientIp: str, port: int) -> 'Server':
        self.__ip: str = self.__findIp()
        self.__clientIp: str = clientIp
        self.__port: int = port
        self.__connectionStatus: str = 'Not Connected'
        self.__serviceStatus: str = ''

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

    def getIp(self) -> str:
        return self.__ip

    def getPort(self) -> int:
        return self.__port

    def getClientIp(self) -> str:
        return self.__clientIp

    def getServerPort(self) -> int:
        return self.__port

    def getConnectionStatus(self) -> str:
        return self.__connectionStatus

    def setConnectionStatus(self, status: str) -> None:
        self.__connectionStatus = status

    def getServiceStatus(self) -> str:
        return self.__serviceStatus

    def setServiceStatus(self, status: str) -> None:
        self.__serviceStatus = status


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
        self.__serverThreads: List[threading.Thread] = []
        self.__shouldTerminate: bool = False
        self.__isStopClientsCliecked: bool = False
        self.__isStartClientsCliecked: bool = False
        self.__isChatGPTEnabled: bool = False
        self.__filterStyle: FilterStyle = None
        self.__openAiApiKey: str = None
        self.__stringVar: tk.StringVar = None
        self.__root: tk.Tk = None
        self.__servicesStatusLabel: tk.Label = None
        self.__ChatGPTStatusLabel: tk.Label = None
        self.__filterStyleStatusLabel: tk.Label = None
        self.__readAndApplyConfigFile()
        self.__prepareGUI()
        self.__configureAdminPanel()
        self.__preapreThreads()

    def __readAndApplyConfigFile(self) -> None:
        file = open(self.__configPath, mode='r', encoding='utf-8')
        self.__config = json.load(file)
        file.close()

    def __configureAdminPanel(self) -> None:
        self.__isChatGPTEnabled = self.__config['ChatGPT']
        self.__filterStyle = self.__config['filterMode']

        clients: List[Dict[str, int]] = self.__config['clients']
        for obj in clients:
            clientIp = obj['clientIp']
            serverPort = obj['serverPort']
            server = Server(clientIp, serverPort)
            self.__connectionDict[server] = []

        if self.__isChatGPTEnabled:
            self.__ChatGPTStatusLabel.config(text='Enabled', fg='green')
        else:
            self.__ChatGPTStatusLabel.config(text='Disabled', fg='red')

        if self.__filterStyle == '':
            self.__filterStyle = FilterStyle.BLUR
            self.__filterStyleStatusLabel.config(text='Blur')
        else:
            self.__filterStyleStatusLabel.config(text=self.__filterStyle)

    def __preapreThreads(self) -> None:
        for server in self.__connectionDict.keys():
            thread = threading.Thread(target=self.__handleClients, args=(server,))
            thread.start()
            self.__serverThreads.append(thread)

    def __receiveBytes(self, socket: socket.socket, count: int) -> bytes:
        bytesReceived = 0
        buffer = b''
        while bytesReceived < count:
            bytes = socket.recv(count - bytesReceived)
            buffer += bytes
            bytesReceived += len(bytes)
        return buffer

    def __handleClients(self, server: Server) -> None:
        clients: List[Client] = self.__connectionDict[server]
        clientThreads: List[threading.Thread] = []
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverIp: str = server.getIp()
        serverPort: int = server.getPort()
        serverSocket.bind((serverIp, serverPort))
        serverSocket.listen()

        while not self.__shouldTerminate:
            try:
                clientSocket, clientAddr = serverSocket.accept()
                print(f'[ADMIN]: New connection from {clientAddr[0]}:{clientAddr[1]}')
                server.setConnectionStatus('Connected')
                client = Client(ip=clientAddr[0], port=int(clientAddr[1]))
                clients.append(client)
                if len(clientThreads) == 0:
                    thread = threading.Thread(target=self.__handleMainClient, args=(server, clientSocket))
                    server.setServiceStatus('Not Running')
                else:
                    thread = threading.Thread(target=self.__handleControllerClient, args=(server, clientSocket))
                    server.setServiceStatus('Running')
                thread.start()
                clientThreads.append(thread)
            except:
                continue

        for thread in clientThreads:
            thread.join()

    def __handleMainClient(self, server: Server, clientSocket: socket.socket) -> None:
        while not self.__shouldTerminate:
            if self.__isStopClientsCliecked and server.getServiceStatus() == 'Running':
                try:
                    clientSocket.send('0'.encode(encoding='utf-8'))
                    server.setServiceStatus('Not Running')
                except:
                    continue

            elif self.__isStartClientsCliecked and server.getServiceStatus() == 'Not Running':
                try:
                    clientSocket.send('1'.encode(encoding='utf-8'))
                    server.setServiceStatus('Running')
                except:
                    continue

            sleep(0)

    def __handleControllerClient(self, server: Server, clientSocket: socket.socket) -> None:
        while not self.__shouldTerminate:
            try:
                message = self.__receiveBytes(clientSocket, 1).decode()
                print(f'[ADMIN]: Message received: "{message}"')
            except:
                continue

            if message == '1':  # question for ChatGPT
                answer = '0'
                if self.__isChatGPTEnabled:
                    answer = '0'
                else:
                    answer = '1'

                try:
                    clientSocket.send(answer.encode(encoding='utf-8'))
                except:
                    print(f'[ADMIN]: Could not send the answer to the client.')

            elif message == '2':  # question for filter style
                answer = '0'
                if self.__filterStyle == FilterStyle.BLUR:
                    answer = '1'
                elif self.__filterStyle == FilterStyle.CONFUSCATION:
                    answer = '2'
                elif self.__filterStyle == FilterStyle.RED_HIGHLIGHT:
                    answer = '3'
                else:
                    answer = '4'
                try:
                    clientSocket.send(answer.encode(encoding='utf-8'))
                except:
                    print(f'[ADMIN]: Could not send the answer to the client.')

            elif message == '3':    # Asking for API Key
                try:
                    clientSocket.send(len(self.__openAiApiKey).to_bytes(byteorder=sys.byteorder, length=4, signed=False))
                except:
                    print(f'[ADMIN]: Could not send the key length to the client.')
                    continue

                try:
                    clientSocket.send(self.__openAiApiKey.encode(encoding='utf-8'))
                except:
                    print(f'[ADMIN]: Could not send the API key to client.')
                    continue

            sleep(0)

    def __startServices(self) -> None:
        self.__isStartClientsCliecked = True
        while True:
            shouldBreak = True
            for server in self.__connectionDict.keys():
                if server.getConnectionStatus() == 'Not Connected':
                    continue

                if server.getServiceStatus() == 'Not Running':
                    shouldBreak = False
                    break

            if shouldBreak:
                break

        self.__isStartClientsCliecked = False
        self.__servicesStatusLabel.config(text='Running', fg='green')

    def __stopServices(self) -> None:
        self.__isStopClientsCliecked = True
        while True:
            shouldBreak = True
            for server in self.__connectionDict.keys():
                if server.getConnectionStatus() == 'Not Connected':
                    continue

                if server.getServiceStatus() == 'Running':
                    shouldBreak = False
                    break

            if shouldBreak:
                break

        self.__isStopClientsCliecked = False
        self.__servicesStatusLabel.config(text='Not Running', fg='red')

    def __restartServices(self) -> None:
        self.__stopServices()
        self.__startServices()

    def __enableChatGPT(self) -> None:
        if self.__isChatGPTEnabled:
            return

        self.__isChatGPTEnabled = True
        self.__ChatGPTStatusLabel.config(text='Enabled', fg='green')

    def __disableChatGPT(self) -> None:
        if not self.__isChatGPTEnabled:
            return

        self.__isChatGPTEnabled = False
        self.__ChatGPTStatusLabel.config(text='Disabled', fg='red')

    def __changeSettingsFile(self) -> None:
        os.startfile(str(self.__configPath))

    def __setFilterStyle(self, button: tk.Button) -> None:
        style = button.cget('text')
        if style == 'Blur':
            self.__filterStyle = FilterStyle.BLUR
            self.__filterStyleStatusLabel.config(text='Blur')
        elif style == 'Confuscation':
            self.__filterStyle = FilterStyle.CONFUSCATION
            self.__filterStyleStatusLabel.config(text='Confuscation')
        elif style == 'Red Highlight':
            self.__filterStyle = FilterStyle.RED_HIGHLIGHT
            self.__filterStyleStatusLabel.config(text='Red Highlight')
        elif style == 'Red Line':
            self.__filterStyle = FilterStyle.RED_LINE
            self.__filterStyleStatusLabel.config(text='Red Line')

    def __openAiApiKeyChangedEvent(self, *args) -> None:
        key = self.__stringVar.get()
        self.__setOpenAiApiKey(key)

    def __setOpenAiApiKey(self, key: str) -> None:
        self.__openAiApiKey = key
        print('[ADMIN]: OpenAI API key has been changed.')

    def __manageClientsWindow(self) -> None:
        window = tk.Toplevel(self.__root)
        window.title("Manage Clients")
        window.geometry("270x500")

        scrollbar = tk.Scrollbar(window, orient="vertical")
        scrollbar.pack(side='right', fill='y')

        canvas = tk.Canvas(window, bg="#303030", yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill="both", expand=True)

        scrollbar.config(command=canvas.yview)

        content_frame = tk.Frame(canvas, bg="#303030")
        canvas.create_window((0, 0), window=content_frame, anchor="nw")

        i = 0
        for server in self.__connectionDict.keys():
            panel = tk.Frame(content_frame, bg="#404040", width=270, height=150)
            panel.grid(row=i, column=0, padx=10, pady=10, sticky="ew")

            ipLabel = tk.Label(panel, text=f"IP: {server.getClientIp()}", bg="#404040", fg="white")
            ipLabel.grid(row=0, column=0, padx=10, pady=10, sticky="w")

            portLabel = tk.Label(panel, text=f"PORT: {server.getServerPort()}", bg="#404040", fg="white")
            portLabel.grid(row=0, column=1, padx=10, pady=10, sticky="e")

            statusLabel = tk.Label(panel, text="Status:", bg="#404040", fg="white")
            statusLabel.grid(row=1, column=0, padx=10, pady=10, sticky="w")

            connectionLabel = tk.Label(panel, text=f"{server.getConnectionStatus()}", bg="#404040", fg="white")
            connectionLabel.grid(row=1, column=1, padx=10, pady=10, sticky="e")

            serviceLabel = tk.Label(panel, text=f"{server.getServiceStatus()}", bg="#404040", fg="white")
            serviceLabel.grid(row=1, column=2, padx=10, pady=10, sticky="e")
            i += 1

            canvas.update_idletasks()
            canvas.config(scrollregion=content_frame.bbox('all'))

    def __setApiKeyWindow(self) -> None:
        window = tk.Toplevel(self.__root)
        window.title("Set OPENAI API Key")
        window.geometry("600x50")

        self.__stringVar = tk.StringVar()
        self.__stringVar.set(self.__openAiApiKey)
        self.__stringVar.trace_add("write", self.__openAiApiKeyChangedEvent)

        frame = tk.Frame(window, bg="#303030")
        frame.pack(expand=True, fill="both")

        key_label = tk.Label(frame, text="Key:", bg="#303030", fg="white", font=("Helvetica", 16))
        key_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        key_entry = tk.Entry(frame, bg="white", fg="black", font=("Helvetica", 16), textvariable=self.__stringVar)
        key_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

    def __prepareGUI(self) -> None:
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
        button1 = tk.Button(bottomPanel, text='Start Services', bg='gray', width=buttonWidth, height=buttonHeight, command=self.__startServices)
        button1.grid(row=0, column=0, padx=buttonPadX, pady=buttonPadY, sticky="we")
        button2 = tk.Button(bottomPanel, text='Stop Services', bg='gray', width=buttonWidth, height=buttonHeight, command=self.__stopServices)
        button2.grid(row=0, column=1, padx=buttonPadX, pady=buttonPadY, sticky="we")
        button3 = tk.Button(bottomPanel, text='Restart Services', bg='gray', width=buttonWidth, height=buttonHeight, command=self.__restartServices)
        button3.grid(row=0, column=2, padx=buttonPadX, pady=buttonPadY, sticky="we")
        button3 = tk.Button(bottomPanel, text='Force Stop Services', bg='#942828', width=buttonWidth, height=buttonHeight, command=self.__stopServices)
        button3.grid(row=0, column=3, padx=buttonPadX, pady=buttonPadY, sticky="we")

        button4 = tk.Button(bottomPanel, text='Change OPENAI API Key', bg='gray', width=buttonWidth, height=buttonHeight, command=self.__setApiKeyWindow)
        button4.grid(row=1, column=0, padx=buttonPadX, pady=buttonPadY, sticky="we")
        button5 = tk.Button(bottomPanel, text='Enable ChatGPT', bg='gray', width=buttonWidth, height=buttonHeight, command=self.__enableChatGPT)
        button5.grid(row=1, column=1, padx=buttonPadX, pady=buttonPadY, sticky="we")
        button6 = tk.Button(bottomPanel, text='Disable ChatGPT', bg='gray', width=buttonWidth, height=buttonHeight, command=self.__disableChatGPT)
        button6.grid(row=1, column=2, padx=buttonPadX, pady=buttonPadY, sticky="we")

        button7 = tk.Button(bottomPanel, text='Manage Clients', bg='#2b47b8', width=buttonWidth, height=buttonHeight, command=self.__manageClientsWindow)
        button7.grid(row=2, column=0, padx=buttonPadX, pady=buttonPadY, sticky="we")
        button8 = tk.Button(bottomPanel, text='Change Settings', bg='gray', width=buttonWidth, height=buttonHeight, command=self.__changeSettingsFile)
        button8.grid(row=2, column=1, padx=buttonPadX, pady=buttonPadY, sticky="we")

        label5 = tk.Label(bottomPanel, text="Filter Style:", fg="white", bg="#303030", font=labelFont)
        label5.grid(row=3, column=0, padx=20, pady=60, sticky="w")

        button11 = tk.Button(bottomPanel, text='Blur', bg='gray', width=buttonWidth, height=buttonHeight, command=lambda: self.__setFilterStyle(button11))
        button11.grid(row=4, column=0, padx=buttonPadX, pady=buttonPadY, sticky="we")
        button12 = tk.Button(bottomPanel, text='Confuscation', bg='gray', width=buttonWidth, height=buttonHeight, command=lambda: self.__setFilterStyle(button12))
        button12.grid(row=4, column=1, padx=buttonPadX, pady=buttonPadY, sticky="we")
        button13 = tk.Button(bottomPanel, text='Red Highlight', bg='gray', width=buttonWidth, height=buttonHeight, command=lambda: self.__setFilterStyle(button13))
        button13.grid(row=4, column=2, padx=buttonPadX, pady=buttonPadY, sticky="we")
        button14 = tk.Button(bottomPanel, text='Red Line', bg='gray', width=buttonWidth, height=buttonHeight, command=lambda: self.__setFilterStyle(button14))
        button14.grid(row=4, column=3, padx=buttonPadX, pady=buttonPadY, sticky="we")

    def mainloop(self) -> None:
        self.__root.mainloop()


gui = AdminPanel()
gui.mainloop()
