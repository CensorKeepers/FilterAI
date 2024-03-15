from selenium import webdriver
from openai import OpenAI

from typing import Union, List
from dotenv import dotenv_values


class SentenceExtractor():

    def __init__(self, driver: Union[webdriver.Firefox, webdriver.Edge, webdriver.Chrome]) -> 'SentenceExtractor':
        self.__driver = driver
        self.__apiKey: str = dotenv_values('.env')['OPENAI_API_KEY']
        self.__openAiClient = OpenAI(api_key=self.__apiKey)
        self.__model = 'gpt-3.5-turbo'

    def extractSentences(self) -> List[str]:
        sentences: List[str] = []
        # TODO: text_files'dan driver'ın bağlı olduğu handle ID'ye ait dosyayı oku. Dosyayı satır satır gez ve satırın uzunluğuna göre ChatGPT'ye sorup sormama kararı al. Sormayacaksan lokal listeye at.
        return sentences
