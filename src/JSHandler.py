
from selenium import webdriver
from typing import Union, Dict


class JSHandler():

    def __init__(self, driver: Union[webdriver.Edge, webdriver.Chrome, webdriver.Firefox]) -> 'JSHandler':
        self.__driver = driver

    def deleteLocalStorage(self) -> None:
        self.__driver.execute_script(f'window.localStorage.removeItem("activeHandle");')

    def setLocalStorageToActiveHandle(self) -> None:
        activeHandle = self.__driver.current_window_handle
        self.__driver.execute_script(f'window.localStorage.setItem("activeHandle", "{activeHandle}");')

    def initialEmbeddings(self) -> None:
        currentHandle = self.__driver.current_window_handle
        self.__driver.execute_script(f'window.myTabId = "{currentHandle}";')
        self.__driver.execute_script('''
           document.addEventListener("visibilitychange", (event) => {
             if (document.visibilityState == "visible") {
               window.localStorage.setItem('activeHandle', window.myTabId);
               console.log(window.localStorage.getItem('activeHandle'))
             }
           });
        ''')

    def isVariableExist(self, var: str) -> bool:
        try:
            self.__driver.execute_script(var)
            return True
        except:
            return False

    def getActiveTab(self) -> str:
        return self.__driver.execute_script(f'return window.localStorage.getItem("activeHandle");')
