
from selenium import webdriver
from typing import Union, Dict


class JSHandler():

    def __init__(self, driver: Union[webdriver.Edge, webdriver.Chrome, webdriver.Firefox]) -> 'JSHandler':
        self.__driver = driver

    def initialEmbeddings(self) -> None:
        self.__driver.execute_script('''
           window.isUserHere = true;
           document.addEventListener("visibilitychange", (event) => {
             if (document.visibilityState == "visible") {
               window.isUserHere = true;
             }
             else {
               window.isUserHere = false;
             }
           });
        ''')

    def isUserHere(self) -> bool:
        return self.isVariableExist('window')

    def isVariableExist(self, var: str) -> bool:
        try:
            self.__driver.execute_script(var)
            return True
        except:
            return False

    def makeAlert(self, message: str) -> None:
        self.__driver.execute_script(f'alert("{message}")')
