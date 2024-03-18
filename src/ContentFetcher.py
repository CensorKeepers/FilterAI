from selenium import webdriver
from typing import Union, Dict
from Logger import Logger
import os
import re
import shutil
from TextExtractor import TextExtractor
from SentenceExtractor import SentenceExtractor
from CensorDecider import CensorDecider
from JSHandler import JSHandler


class ContentFetcher:
    def __init__(self, driver: Union[webdriver.Edge, webdriver.Chrome, webdriver.Firefox]):
        self.__driver = driver
        self.html_files_directory = "html_files"
        self.text_files_directory = "text_files"
        self.textExtractor = TextExtractor(self.text_files_directory)
        self.__sentenceExtractor = SentenceExtractor(self.__driver)
        self.__censorDecider = CensorDecider()
        self.__reset_directories()

    def __reset_directories(self):
        for directory in [self.html_files_directory, self.text_files_directory]:
            if os.path.exists(directory):
                shutil.rmtree(directory)
            os.makedirs(directory)

    def fetchAndPrintHtmlContents(self, handlesDict, currentHandle, jsHandler: JSHandler):
        if currentHandle in handlesDict:
            url = handlesDict[currentHandle]
            try:
                current_html_content = self.__driver.page_source
            except:
                return
            body = current_html_content[current_html_content.index('<body'):current_html_content.index('</body>') + 7]
            html_file_path = os.path.join(self.html_files_directory, f"{currentHandle}.txt")

            shouldExtractText = False
            if os.path.exists(html_file_path):
                with open(html_file_path, "r", encoding="utf-8") as file:
                    existingBody = file.read()
                if existingBody == body:
                    # Logger.warn(f"No changes detected in {url}. File {html_file_path} remains unchanged.")
                    return
                else:
                    shouldExtractText = True
            else:
                shouldExtractText = True

            if shouldExtractText:
                with open(html_file_path, "w", encoding="utf-8") as file:
                    file.write(body)
                Logger.warn(f"[HTML]: HTML content for {url} has been updated and saved to {html_file_path}.")
                self.textExtractor.extractAndSaveText(body, currentHandle)
                self.__filterText(jsHandler)
        else:
            Logger.warn("Current handle is not found in handles dictionary.")

    def __filterText(self, jsHandler: JSHandler) -> None:
        # TODO: html_files dizininde diriver'ın bağlı olduğu handle ID'ye ait HTML dosyasını aç. İçeriğini oku ve değişkene kaydet.
        currentHandle = self.__driver.current_window_handle
        html_file_path = os.path.join(self.html_files_directory, f"{currentHandle}.txt")
        # file = open(html_file_path, "r", encoding="utf-8")
        # body = file.read()
        # file.close()
        jsHandler.hideDocument()
        sentences = self.__sentenceExtractor.extractSentences()
        Logger.warn('[FILTER]: Filtering has begun.')
        for sentence in sentences:
            # TODO: Modele 'sentence' yi sor. Gelen cevaba göre 'sentence'yi düzenle ve başka bir değikene koy.
            # TODO: Düzenlenmemiş 'sentence'yi HTML dosyasında ara ve düzenlenmişiyle yer değiştir.
            # print(f'Sentence: {sentence}')
            modifiedSentence = sentence + '$$$$$$$'
            jsHandler.replace(sentence, modifiedSentence)
            # body = re.sub(re.escape(sentence), modifiedSentence, body)

        Logger.warn('[FILTER]: Filtering has finished.')
        jsHandler.showDocument()
        pageSource = self.__driver.page_source
        body = pageSource[pageSource.index('<body'):pageSource.index('</body>') + 7]
        file = open(html_file_path, "w", encoding="utf-8")
        file.write(body)
        file.close()

    def deleteFiles(self, deletedTabHandle):
        html_file_path = os.path.join(self.html_files_directory, f"{deletedTabHandle}.txt")
        text_file_path = os.path.join(self.text_files_directory, f"{deletedTabHandle}.txt")
        for file_path in [html_file_path, text_file_path]:
            if os.path.exists(file_path):
                os.remove(file_path)
                Logger.warn(f"Deleted file for closed tab {deletedTabHandle}")
            else:
                Logger.warn(f"File for deleted tab does not exist: {file_path}")
