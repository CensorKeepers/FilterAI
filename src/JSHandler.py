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

    def restoreFilteredContent(self, body: str) -> None:
        self.__driver.execute_script(f'document.body.innerHTML = arguments[0];', body)

    def hideDocument(self) -> None:
        self.__driver.execute_script(f'document.body.style.visibility = "hidden";')

    def showDocument(self) -> None:
        self.__driver.execute_script(f'document.body.style.visibility = "visible";')

    def replace(self, old: str, new: str) -> None:
        self.__driver.execute_script('''
            function replaceInText(element, pattern, replacement) {
                const re = new RegExp(pattern, 'gi');
                for (let node of element.childNodes) {
                    switch (node.nodeType) {
                        case Node.ELEMENT_NODE:
                            replaceInText(node, pattern, replacement);
                            break;
                        case Node.TEXT_NODE:
                            if (node.textContent.match(re)) {
                                const span = document.createElement('span');
                                span.innerHTML = node.textContent.replace(re, replacement);
                                node.parentNode.replaceChild(span, node);
                            }
                            break;
                        case Node.DOCUMENT_NODE:
                            replaceInText(node, pattern, replacement);
                    }
                }
            }
            replaceInText(document.body, arguments[0], arguments[1]);
        ''', old, new)
