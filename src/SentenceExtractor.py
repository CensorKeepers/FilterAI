from selenium import webdriver
from openai import OpenAI

from typing import Union, List
from dotenv import dotenv_values

import os

from Logger import Logger


class SentenceExtractor():

    def __init__(self, driver: Union[webdriver.Firefox, webdriver.Edge, webdriver.Chrome], text_files_directory) -> 'SentenceExtractor':
        self.__driver = driver
        self.__apiKey: str = dotenv_values('.env')['OPENAI_API_KEY']
        self.__openAiClient = OpenAI(api_key=self.__apiKey)
        self.__model = 'gpt-3.5-turbo'
        self.__textFilesDirectory = text_files_directory
        if not os.path.exists(self.__textFilesDirectory):
            os.makedirs(self.__textFilesDirectory)

    def correctWords(self) -> List[str]:
        currentHandle = self.__driver.current_window_handle
        textFilesPath = os.path.join(self.__textFilesDirectory, f"{currentHandle}.txt")
        file = open(textFilesPath, "r", encoding="utf-8")
        text = file.read()
        file.close()
        words: List[str] = list(filter(None, text.splitlines()))
        Logger.warn('[CHATGPT]: Sentence extraction has begun.')
        correctedWords = self.__askChatGPT(words)
        Logger.warn('[CHATGPT]: Sentence extraction has finished.')
        return correctedWords

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
            content = f'{wordList} içerisinde yazımı yanlış kelimelerin doğrusunu yaz. Sadece cevabı yaz, açıklama yazma. Cevap formatı şu şekilde: <yanlış>:<doğrusu>\n<yanlış>:<doğrusu>. Eğer tüm kelimeler doğruysa cevap olarak sadece ALL:ALL yaz. Düzeltilmiş kelimeler tek kelime içermeli kesinlikle. Boşluk içermemeli. Latin alfabesi içermeyen kelimeleri es geç. Çıktıda < veya > koyma.'
            apiObject = {'role': 'user', 'content': content}
            response = self.__openAiClient.chat.completions.create(model=self.__model, messages=[apiObject])
            # Logger.warn(f'ChatGPT Response: {response.choices[0].message.content}')
            if response.choices[0].message.content == 'ALL':
                continue

            wordPairs = response.choices[0].message.content.splitlines()
            for wordPair in wordPairs:
                currentWord = wordPair[:wordPair.index(':')]
                correctedWord = wordPair[wordPair.index(':') + 1:]
                wordList = [w.replace(currentWord, correctedWord) for w in wordList]

        answer: List[str] = [word for wordList in bucket for word in wordList]
        return answer
