from selenium import webdriver
from typing import Union, Dict
import threading
from Logger import Logger
import os
import io
#dict_items([('09167a15-92e3-4fa8-8e04-78a98e6416d3', 'https://www.google.com.tr/'), ('f2298a78-d1a8-4870-a70f-7f45509d61ba', 'https://www.google.com.tr/'), ('79448917-5a97-43fc-9e0d-0a9043d0f922', 'https://ubs.etu.edu.tr/'), ('f04e67bd-4845-4f88-8584-adb6d7e4da61', 'https://store.epicgames.com/'), ('d469e004-402a-430a-8777-56d445dde49d', 'about:newtab')])

#refresh nereye konulcak
#html contentleri buradan alabiliriz. print kisimlarinda degisen url ve eklenen tab'a gore alinir


class ContentFetcher:
    def __init__(self, driver: Union[webdriver.Edge, webdriver.Chrome, webdriver.Firefox]):
        self.__driver = driver
        self.__visitedTabUrlPair : Dict[str, str] = {}
        self.reset()
        self.__thread = threading.Thread(target=self.__process, args=())
        self.__sensorThread = threading.Thread(target=self.__handleHTMLchanges, args=())

    def reset(self):
        self.__visitedTabUrlPair = {}
        
    def fetchAndPrintHtmlContents(self, pair: Dict[str, str]):
        for tab_id, url in pair.items():
            if tab_id not in self.__visitedTabUrlPair:
                self.__visitedTabUrlPair[tab_id] = url
                Logger.warn(f"YENİ TAB {tab_id} ve {url}")
                self.__htmlContentForTab(tab_id, url, True)
            else:
                if url != self.__visitedTabUrlPair[tab_id]:
                    self.__visitedTabUrlPair[tab_id] = url
                    Logger.warn(f"YENİ URL tab {tab_id} ve {url}")
                    self.__htmlContentForTab(tab_id, url, True)
                else:
                    pass

        tabs_to_delete = [tab_id for tab_id in self.__visitedTabUrlPair if tab_id not in pair]

        for tab_id in tabs_to_delete:
            Logger.warn(f"Bu {tab_id} ve {self.__visitedTabUrlPair[tab_id]} silindi ")
            
            del self.__visitedTabUrlPair[tab_id]
            self.__htmlContentForTab(tab_id, url, False)
    
    def __htmlContentForTab(self, tab_id: str, url: str, isOpen: bool):
        directory = r"C:\\bitirme_496\\src\\html_files"
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        file_path = os.path.join(directory, f"{tab_id}.txt")
        
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

    def __process(self) -> None:
        self.__sensorThread.start()
        self.__sensorThread.join()
    
    def start(self) -> None:
        self.__thread.start()

    def join(self) -> None:
        self.__thread.join()