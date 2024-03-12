from bs4 import BeautifulSoup
import os

class TextExtractor:
    def __init__(self, text_files_directory):
        self.text_files_directory = text_files_directory
        if not os.path.exists(self.text_files_directory):
            os.makedirs(self.text_files_directory)

    def extractAndSaveText(self, html_content, handle):
        soup = BeautifulSoup(html_content, 'html.parser')
        for script_or_style in soup(["script", "style", "head", "footer", "nav", "aside"]):
            script_or_style.decompose()


        lines = []
        for element in soup.stripped_strings:
            if element.endswith(('.', '!', '?')):
                lines.append(element + "\n")
            else:
                lines.append(element + " ")
        text = "".join(lines).strip()

        output_file_path = os.path.join(self.text_files_directory, f"{handle}_extracted.txt")

        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(text)
        print(f"Extracted text content has been saved to: {output_file_path}")

