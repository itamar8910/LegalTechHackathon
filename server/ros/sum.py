#!/usr/bin/python
# -*- coding: utf-8 -*-
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pickle
from googletrans import Translator
import urllib
from gensim.summarization import summarize

def get_url(hebrew_string):
    url_string = "https://he.wikisource.org/wiki/"
    new_u = hebrew_string.encode('utf-8')
    realy_new = ""
    for x in new_u:
        realy_new += "%"
        realy_new += hex(x)[2:]
    url_string += realy_new
    return url_string


def fuckkk(hebrew_string):
    response = urlopen(get_url(hebrew_string))
    page_source = response.read().decode("utf-8")
    response.close()
    page_source = page_source.split("title=\"")
    page_source = page_source[9:]
    page_source = page_source[:1009]
    name_list = []
    for x in page_source:
        name_list.append(x[:x.index('\"')])
    return name_list

def make_str_with_makaf(name_str):
    return name_str.replace(" ","_")

def trans(cool_text_heb, leng):
    translator = Translator()
    eng_text = ""
    index = 0
    while index + 3000 < len(cool_text_heb):
        eng_text += translator.translate(cool_text_heb[index:make_3000(cool_text_heb, index)], dest=leng).text
        eng_text += ' '
        index = make_3000(cool_text_heb, index) + 1
        print(index)
    eng_text += translator.translate(cool_text_heb[index:], dest=leng).text
    return eng_text

def make_3000(cool_text, index_start):
    index = index_start + 3000
    while cool_text[index] != "\u0020":
        index -= 1
    return index
names = pickle.load(open( "ros/dani_gay.pkl", "rb" ))

def sheilta(quote):
    rules = pickle.load(open("ros/dani_gay.pkl", "rb"))
    for x in rules:
        if x in quote:
            a = make_str_with_makaf(x)
            url_site = get_url(a)
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]  # wikipedia needs this

            resource = opener.open(url_site)
            data = resource.read()
            resource.close()
            soup = BeautifulSoup(data, "html5lib")
            text = ''.join(
                list(filter(lambda x: x < "\u0041" or (x > "\u005A" and x < "\u0061") or x > "\u007A", soup.text)))
            text = text.replace("\u000A", " ")
            text = text[:text.index("אזהרה: המידע")]
            text = text[text.find("1."):]
            text = ''.join(list(filter(lambda x: x >= "\u05D0" and x <= "\u05F4" or x == "\u0020", text)))

            #eng_text = trans(text, 'en')
            #sum = trans(''.join(summarize(eng_text, split=True)), 'iw')  # ratio=0.5, word_count=50
            return text
    return 0

"""
all_data = []
global_list = [10,123,920,777,504,92,6,72,620,515]
for x in global_list:

    a = make_str_with_makaf(names[x])
    url_site = get_url(a)
    webbrowser.open(url_site, new=0, autoraise=True)


    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')] #wikipedia needs this

    resource = opener.open(url_site)
    data = resource.read()
    resource.close()
    soup = BeautifulSoup(data,"html5lib")
    text = ''.join(list(filter(lambda x: x<"\u0041" or (x>"\u005A" and x<"\u0061") or x >"\u007A",soup.text)))
    text = text.replace("\u000A"," ")
    text = text[:text.index("אזהרה: המידע")]
    text = text[text.find("1."):]
    text = ''.join(list(filter(lambda x: x>="\u05D0" and x<="\u05F4" or x == "\u0020",text)))

    eng_text = trans(text,'en')
    sum = trans(''.join(summarize(eng_text, split=True)),'iw')  # ratio=0.5, word_count=50
    print(0)
    all_data.append((text,sum))
pickle.dump(all_data, open('shut_da_fuck.pkl', 'wb'))
"""

if __name__ == "__main__":
    print(sheilta("תן לי כל מה שאתה יודע על חוק ההוצאה לפועל")[0])