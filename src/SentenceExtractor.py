from selenium import webdriver
from openai import OpenAI

from typing import Union, List
from dotenv import dotenv_values

import os

from Logger import Logger


class SentenceExtractor():

    def __init__(self, driver: Union[webdriver.Firefox, webdriver.Edge, webdriver.Chrome]) -> 'SentenceExtractor':
        self.__driver = driver
        self.__apiKey: str = dotenv_values('.env')['OPENAI_API_KEY']
        self.__openAiClient = OpenAI(api_key=self.__apiKey)
        self.__model = 'gpt-3.5-turbo'
        self.__textFilesDirectory = "text_files"

    def extractSentences(self) -> List[str]:
        # TODO: text_files'dan driver'ın bağlı olduğu handle ID'ye ait dosyayı oku. Dosyayı satır satır gez ve satırın uzunluğuna göre ChatGPT'ye sorup sormama kararı al. Sormayacaksan lokal listeye at.
        sentences: List[str] = []
        currentHandle = self.__driver.current_window_handle
        textFilesPath = os.path.join(self.__textFilesDirectory, f"{currentHandle}.txt")
        file = open(textFilesPath, "r", encoding="utf-8")
        text = file.read()
        file.close()
        Logger.warn('[CHATGPT]: Sentence extraction has begun.')
        for sentence in text.splitlines():
            sentences += self.__askChatGPT(sentence)
        Logger.warn('[CHATGPT]: Sentence extraction has finished.')
        return list(filter(None, sentences))

    def __askChatGPT(self, sentence: str) -> List[str]:
        content = f'Sana bir görev vereceğim. Cevap verirken şu kriterlere uy. 1) Sadece cevabı yaz. Cevap dışında herhangi bir şey yazma. 2) Cevap birden fazla cümleden oluşuyorsa cümleleri newline(\n) karakteriyle ayırarak yaz. 3) Eğer cevap tek bir cümleyse o cümleyi kelimelerine ayırmaya çalışma. Cümleyi olduğu gibi yaz. "{sentence}" yazısını anlamlı cümlelere ayır'
        apiObject = {'role': 'user', 'content': content}
        response = self.__openAiClient.chat.completions.create(model=self.__model, messages=[apiObject])
        return response.choices[0].message.content.splitlines()
