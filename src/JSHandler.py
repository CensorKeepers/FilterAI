from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from typing import List, Union


class JSHandler():

    def __init__(self, driver: Union[webdriver.Firefox, webdriver.Edge, webdriver.Chrome]) -> 'JSHandler':
        self.__driver = driver

    def initialEmbeddings(self) -> None:
        self.embedUniqueHTMLElement()

    def embedUniqueHTMLElement(self) -> None:
        handle = self.__driver.current_window_handle
        WebDriverWait(self.__driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        self.__driver.execute_script(f'''
            window.myTabId = '{handle}';
            let element = document.createElement('div');
            element.id = '{handle}';
            element.style.display = 'none';
            document.body.appendChild(element);
        ''')

    def isPageRefreshed(self) -> bool:
        handle = self.__driver.current_window_handle
        return self.__driver.execute_script(f'''return document.getElementById('{handle}') === null;''')
