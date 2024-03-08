from selenium import webdriver
from typing import Union, Dict
import threading
from Logger import Logger
import os
import io

# refresh nereye konulcak
# html contentleri buradan alabiliriz. print kisimlarinda degisen url ve eklenen tab'a gore alinir


class ContentFetcher:
    def __init__(self, driver: Union[webdriver.Edge, webdriver.Chrome, webdriver.Firefox]):
        self.__driver = driver
        self.__visitedTabUrlPair: Dict[str, str] = {}

    def reset(self):
        self.__visitedTabUrlPair = {}

    def fetchAndPrintHtmlContents(self, pair: Dict[str, str]):
        for tabId, url in pair.items():
            if tabId not in self.__visitedTabUrlPair:
                self.__visitedTabUrlPair[tabId] = url
                # Logger.warn(f"YENİ TAB {tabId} ve {url}")
                self.__htmlContentForTab(tabId, url, True)
            else:
                if url != self.__visitedTabUrlPair[tabId]:
                    self.__visitedTabUrlPair[tabId] = url
                    # Logger.warn(f"YENİ URL tab {tabId} ve {url}")
                    self.__htmlContentForTab(tabId, url, True)
                else:
                    pass

        tabs_to_delete = [tab_id for tab_id in self.__visitedTabUrlPair if tab_id not in pair]

        for tabId in tabs_to_delete:
            Logger.warn(f"Bu {tabId} ve {self.__visitedTabUrlPair[tabId]} silindi ")

            del self.__visitedTabUrlPair[tabId]
            self.__htmlContentForTab(tabId, url, False)

    def __htmlContentForTab(self, tabId: str, url: str, isOpen: bool):
        directory = '/home/ubuntu/FilterAI/html_files'
        if not os.path.exists(directory):
            os.makedirs(directory)

        file_path = os.path.join(directory, f"{tabId}.txt")

        if isOpen:
            self.__driver.get(url)
            html_content = self.__driver.page_source

            with io.open(file_path, 'w', encoding='utf-8') as file:
                file.write(html_content)
                # Logger.warn(f"HTML content for tab {tab_id} has been saved to {file_path}")
        else:
            if os.path.exists(file_path):
                os.remove(file_path)

    def __handleHTMLchanges(self) -> None:
        pass
