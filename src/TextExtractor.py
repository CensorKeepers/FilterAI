from bs4 import BeautifulSoup
import os
from Logger import Logger
from DetoxifySentences import predict_detoxify

class TextExtractor:
    def __init__(self, text_files_directory) -> 'TextExtractor':
        self.text_files_directory = text_files_directory
        if not os.path.exists(self.text_files_directory):
            os.makedirs(self.text_files_directory)

    def extractAndSaveText(self, htmlBody: str, handle: str, isCompare) -> str: # Ensure this method always returns a string
        soup = BeautifulSoup(htmlBody, 'html.parser')
        for script_or_style in soup(["script", "style", "head", "footer", "nav", "aside"]):
            script_or_style.decompose()
        
        def split_line_if_needed(line):
            # Split line into words and yield each word followed by a newline.
            for word in line.split():
                #print(f"{word}          {predict_detoxify(word)}")
                yield word + "\n"
                
        lines = []
        for element in soup.stripped_strings:
            if element.endswith(('.', '!', '?', '...', ':', ';')):
                lines.extend(split_line_if_needed(element))
            else:
                lines.extend(split_line_if_needed(element + " "))
        text = "".join(lines).strip()

        if isCompare:
            output_file_path = os.path.join(self.text_files_directory, f"{handle}.txt")
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(text)
            Logger.warn(f"[TEXT]: Extracted text content has been saved to: {output_file_path}")
        # Return the extracted text in all cases
        return text

    def compareHTMLFiles(self, html_content, handle):
        text_file_path = os.path.join(self.text_files_directory, f"{handle}.txt")
        refreshedText = self.extractAndSaveText(html_content, handle, False)  
        
        try:
            with open(text_file_path, 'r', encoding='utf-8') as text_file:
                text_content = text_file.read()
            if (text_content.strip() == refreshedText.strip()):
                # Logger.warn("AYNI SAYFADAYIZ HİÇBİR SIKINTI YOK")
                return False
            else:
                # Logger.warn("CİDDEN DEĞİŞİKLİK OLDU ------------------------")
                return True
        except FileNotFoundError:
            Logger.warn("One of the files does not exist.")
            return True      