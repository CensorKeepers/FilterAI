from selenium import webdriver
from typing import Union, Dict, List
from Logger import Logger
import os
import re
import shutil
from TextExtractor import TextExtractor
from SentenceExtractor import SentenceExtractor
from JSHandler import JSHandler
from DetoxifySentences import predict


class ContentFetcher:
    def __init__(self, driver: Union[webdriver.Edge, webdriver.Chrome, webdriver.Firefox]):
        self.__driver = driver
        self.html_files_directory = "html_files"
        self.text_files_directory = "text_files"
        self.detoxify_result_directory = "detoxify_results"
        self.textExtractor = TextExtractor(self.text_files_directory)
        self.__sentenceExtractor = SentenceExtractor(self.__driver, self.text_files_directory)
        self.__reset_directories()

    def __reset_directories(self):
        for directory in [self.html_files_directory, self.text_files_directory, self.detoxify_result_directory]:
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

            html_file_path = os.path.join(self.html_files_directory, f"{currentHandle}.txt")

            shouldExtractText = False
            if os.path.exists(html_file_path):
                with open(html_file_path, "r", encoding="utf-8") as file:
                    existing_html_content = file.read()
                if existing_html_content == current_html_content:
                    # Logger.warn(f"No changes detected in {url}. File {html_file_path} remains unchanged.")
                    return
                else:
                    shouldExtractText = self.textExtractor.compareHTMLFiles(current_html_content, currentHandle)

            else:
                shouldExtractText = True

            if shouldExtractText:
                with open(html_file_path, "w", encoding="utf-8") as file:
                    file.write(current_html_content)
                Logger.warn(f"[HTML]: HTML content for {url} has been updated or saved to {html_file_path}.")
                self.textExtractor.extractAndSaveText(current_html_content, currentHandle, True)
                self.__filterText(jsHandler)
        else:
            Logger.warn("Current handle is not found in handles dictionary.")

    def __loadDetoxifyResults(self):
        detoxify_results_path = os.path.join(self.detoxify_result_directory, "detoxify_results.txt")
        if not os.path.exists(detoxify_results_path):
            return {}

        with open(detoxify_results_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        results = {}
        for line in lines:
            parts = line.strip().split(":")
            if len(parts) == 2:
                results[parts[0]] = float(parts[1])

        return results

    def __saveDetoxifyResult(self, word, toxicity):
        detoxify_results_path = os.path.join(self.detoxify_result_directory, "detoxify_results.txt")
        with open(detoxify_results_path, "a", encoding="utf-8") as file:
            file.write(f"{word}:{toxicity}\n")

    def __filterText(self, jsHandler: JSHandler) -> None:
        currentHandle = self.__driver.current_window_handle
        html_file_path = os.path.join(self.html_files_directory, f"{currentHandle}.txt")
        jsHandler.hideDocument()

        words = self.__sentenceExtractor.correctWords()
        Logger.warn(f'[LLM]: Predicting the words...')
        Logger.warn(f'[FILTER]: Filtering has begun.')
        detoxifyResults = self.__loadDetoxifyResults()

        for currentWord in words:
            if currentWord not in detoxifyResults:
                toxicity = predict(currentWord)
                # Logger.warn(f"------------------------------------------ YENİ KELİME KAYDEDİLDİ {currentWord} -> {toxicity}")
                self.__saveDetoxifyResult(currentWord, toxicity)
                detoxifyResults[currentWord] = toxicity

            if detoxifyResults[currentWord] >= 0.8:
                modifiedWord = f'<span style="color: red;">{currentWord}</span>'
                Logger.warn(f'[FILTER]: The word "{currentWord}" is being filtered with toxicity: {detoxifyResults[currentWord]}')
                jsHandler.replace(currentWord, modifiedWord)

        Logger.warn(f'[FILTER]: Filtering has finished.')
        jsHandler.showDocument()

        pageSource = self.__driver.page_source
        file = open(html_file_path, "w", encoding="utf-8")
        file.write(pageSource)
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
