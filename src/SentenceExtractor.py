from selenium import webdriver
from openai import OpenAI
from typing import Union, List
import os
import socket
import sys

from Logger import Logger


class SentenceExtractor():

    def __init__(self, driver: Union[webdriver.Firefox, webdriver.Edge, webdriver.Chrome], text_files_directory) -> 'SentenceExtractor':
        self.__driver = driver
        self.__openAiClient: OpenAI = None
        self.__model = 'gpt-3.5-turbo'
        self.__textFilesDirectory = text_files_directory
        if not os.path.exists(self.__textFilesDirectory):
            os.makedirs(self.__textFilesDirectory)

    def correctWords(self, clientSocket: socket.socket) -> List[str]:
        try:
            clientSocket.send('1'.encode(encoding='utf-8'))
            answer = self.__receiveBytes(clientSocket, 1).decode()
            if answer == '1':
                currentHandle = self.__driver.current_window_handle
                textFilesPath = os.path.join(self.__textFilesDirectory, f"{currentHandle}.txt")
                file = open(textFilesPath, "r", encoding="utf-8")
                text = file.read()
                file.close()
                words: List[str] = list(filter(None, text.splitlines()))
                return words
        except:
            Logger.warn(f'[CHATGPT]: ChatGPT has been skipped.')
            return

        try:
            clientSocket.send('3'.encode(encoding='utf-8'))
        except:
            Logger.warn(f'[CHATGPT]: Could not ask for OpenAI API key.')
            return

        try:
            keyLength = int.from_bytes(self.__receiveBytes(clientSocket, 4), byteorder=sys.byteorder, signed=False)
        except:
            Logger.warn(f'[CHATGPT]: Could not receive key length from the server.')
            return

        try:
            key = self.__receiveBytes(clientSocket, keyLength).decode()
        except:
            Logger.warn(f'[CHATGPT]: Could not receive the API key from the server.')
            return

        self.__openAiClient = OpenAI(api_key=key)
        currentHandle = self.__driver.current_window_handle
        textFilesPath = os.path.join(self.__textFilesDirectory, f"{currentHandle}.txt")
        file = open(textFilesPath, "r", encoding="utf-8")
        text = file.read()
        file.close()
        words: List[str] = list(filter(None, text.splitlines()))
        # TODO: burada latin harfi icermeyen kelimeleri discard et.
        Logger.warn('[CHATGPT]: Sentence extraction has begun.')
        correctedWords = self.__askChatGPT(words)
        Logger.warn('[CHATGPT]: Sentence extraction has finished.')
        return correctedWords

    def __receiveBytes(self, socket: socket.socket, count: int) -> bytes:
        bytesReceived = 0
        buffer = b''
        while bytesReceived < count:
            bytes = socket.recv(count - bytesReceived)
            buffer += bytes
            bytesReceived += len(bytes)
        return buffer

    def __askChatGPT(self, words: List[str]) -> List[str]:
        bucket: List[List[str]] = []
        limit = 500
        current = 0
        while True:
            if limit > len(words):
                bucket.append(words[current:])
                break
            else:
                bucket.append(words[current:limit])
                current = limit
                limit += 500

        for wordList in bucket:
            content = f'"{wordList}" In this list, write the correct form of any misspelled words. ' \
                'Only provide the answer, without any explanation. ' \
                'The response format should be as follows: <incorrect>:<correct>\n<incorrect>:<correct>. ' \
                'If all words are correct, simply write ALL:ALL as the response. ' \
                'Corrected words must contain only a single word without any spaces. ' \
                'Skip words that do not contain Latin alphabet characters. ' \
                'Do not include < or > in the output.'

            apiObject = {'role': 'user', 'content': content}
            response = self.__openAiClient.chat.completions.create(model=self.__model, messages=[apiObject])
            # Logger.warn(f'ChatGPT Response: {response.choices[0].message.content}')
            if response.choices[0].message.content == 'ALL:ALL':
                continue

            while ':' not in response.choices[0].message.content:
                Logger.warn(f'CHATGPT answer is not correct.')
                content = f'PLEASE USE THIS LOGIC WHEN YOU ARE ANSWERING! \
                            "{wordList}" In this list, write the correct form of any misspelled words. \
                            Only provide the answer, without any explanation. \
                            The response format should be as follows: <incorrect>:<correct>\n<incorrect>:<correct>. \
                            If all words are correct, simply write ALL:ALL as the response. \
                            Corrected words must contain only a single word without any spaces. \
                            Skip words that do not contain Latin alphabet characters. \
                            Do not include < or > in the output.'

                apiObject = {'role': 'user', 'content': content}
                response = self.__openAiClient.chat.completions.create(model=self.__model, messages=[apiObject])
                # Logger.warn(f'ChatGPT Response: {response.choices[0].message.content}')
                if response.choices[0].message.content == 'ALL:ALL':
                    continue

            wordPairs = response.choices[0].message.content.splitlines()
            for wordPair in wordPairs:
                if ':' in wordPair:
                    currentWord = wordPair[:wordPair.index(':')]
                    correctedWord = wordPair[wordPair.index(':') + 1:]
                    wordList = [w.replace(currentWord, correctedWord) for w in wordList]
                else:
                    Logger.warn(f"Expected ':' in word pair but not found. WordPair: {wordPair}")

        answer: List[str] = [word for wordList in bucket for word in wordList]
        return answer
