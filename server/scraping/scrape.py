import os
from bs4 import BeautifulSoup
import json

def scrape(html_path, save_path):
    with open(html_path, 'r') as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    psak_dins = soup.findAll('div', attrs={'class':'searchItem'})
    all_data = []
    for psak_din in psak_dins:
        title = " ".join([b.text for b in psak_din.findAll('b') if b.has_attr('title')])
        judges_div = psak_din.find('div', attrs={'class':'body'})
        judegs_line = [x for x in judges_div.text.split("\n") if x.strip() != ""][1]
        judges = judegs_line.split(",")
        text_lines = judges_div.text.split("\n")
        res = ""
        type = ""
        if 'תיק סגור:' in text_lines:
            res = text_lines[text_lines.index('תיק סגור:') + 1].strip()
        if 'סוג עניין:' in text_lines:
            type = text_lines[text_lines.index('סוג עניין:') + 1].strip()
        mini = judges_div.find('div', attrs={'class':'miniRatz'}).text
        pdf_url = judges_div.find('a', attrs={'class':'boxIcon icon_Pdf'})
        all_data.append({
            'title': title,
            'judges': judges,
            'res': res,
            'mini': mini,
            'pdf_url':pdf_url
        })

    with open(save_path, 'w') as f:
        json.dump(all_data, f)
if __name__ == "__main__":
    for f in os.listdir('htmls'):
        f = f.replace(".html", "")
        scrape("htmls/{}.html".format(f), "{}_json.json".format(f))