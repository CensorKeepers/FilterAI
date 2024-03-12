from selenium import webdriver
from typing import Union, Dict
from Logger import Logger
import os
import io
import shutil
from TextExtractor import TextExtractor


class ContentFetcher:
    def __init__(self, driver: Union[webdriver.Edge, webdriver.Chrome, webdriver.Firefox]):
        self.__driver = driver
        self.html_files_directory = "html_files"
        self.text_files_directory = "text_files"
        self.textExtractor = TextExtractor(self.text_files_directory)
        self.__reset_directories()

    def __reset_directories(self):
        for directory in [self.html_files_directory, self.text_files_directory]:
            if os.path.exists(directory):
                shutil.rmtree(directory)
            os.makedirs(directory)

    def fetchAndPrintHtmlContents(self, handlesDict, currentHandle):
        if currentHandle in handlesDict:
            url = handlesDict[currentHandle]
            current_html_content = self.__driver.page_source
            html_file_path = os.path.join(self.html_files_directory, f"{currentHandle}.txt")

            shouldExtractText = False
            if os.path.exists(html_file_path):
                with open(html_file_path, "r", encoding="utf-8") as file:
                    existing_html_content = file.read()
                if existing_html_content == current_html_content:
                    # Logger.warn(f"No changes detected in {url}. File {html_file_path} remains unchanged.")
                    return
                else:
                    shouldExtractText = True
            else:
                shouldExtractText = True

            if shouldExtractText:
                with open(html_file_path, "w", encoding="utf-8") as file:
                    file.write(current_html_content)
                Logger.warn(f"[HTML]: HTML content for {url} has been updated or saved to {html_file_path}.")
                self.textExtractor.extractAndSaveText(current_html_content, currentHandle)
        else:
            Logger.warn("Current handle is not found in handles dictionary.")

    def deleteFiles(self, deletedTabHandle):
        html_file_path = os.path.join(self.html_files_directory, f"{deletedTabHandle}.txt")
        text_file_path = os.path.join(self.text_files_directory, f"{deletedTabHandle}.txt")
        for file_path in [html_file_path, text_file_path]:
            if os.path.exists(file_path):
                os.remove(file_path)
                Logger.warn(f"Deleted file for closed tab {deletedTabHandle}")
            else:
                Logger.warn(f"File for deleted tab does not exist: {file_path}")
