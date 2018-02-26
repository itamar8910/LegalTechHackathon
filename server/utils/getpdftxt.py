# -*- coding: utf-8 -*-
import textract
import requests

def get_pdf_text(url):
    pdf_content = requests.get(url).content
    with open('tmp_pdf.pdf', 'w') as f:
        f.write(pdf_content)
    text = textract.process('tmp_pdf.pdf')
    return text

if __name__ == "__main__":
    url = "https://www.nevo.co.il/psika_html/mechozi/ME-15-12-2310-11.pdf#xml=http://www.nevo.co.il/Handlers/Highlighter/PdfHighlighter.ashx?index=0&type=Main"
    print(get_pdf_text(url))