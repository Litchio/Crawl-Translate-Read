# -*- coding: utf-8 -*-
from deep_translator import GoogleTranslator
from deep_translator import exceptions
import pyttsx3
import urllib
import PySimpleGUI as sg
from bs4 import BeautifulSoup
import re

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
engine = pyttsx3.init()


def crawl(baseurl, starturl, HyperLinkText, depth):
    i = 0
    currenturl = starturl
    regex = r'<a[^(<a)]*href="[^(<a)]*">[^(<a)]*' + HyperLinkText + '[^(<a)]*</a>'
    urllist = []
    while i<int(depth):
        urllist.append(currenturl)
        try:
            request = urllib.request.Request(currenturl, None, headers=hdr)
        except:
            print("Error Requesting: " + currenturl)
        response = urllib.request.urlopen(request)
        htmlBytes = response.read()
        htmlStr = htmlBytes.decode("utf8")
        currenturl = re.search(regex, htmlStr).group(0)#, re.DOTALL).group(0)
        links = re.findall("href=[\"\'](.*?)[\"\']", currenturl)       
        print(currenturl, flush=True)
        currenturl = baseurl + links[0]
        
        i += 1
    return urllist


def TextOfHtml(file):
    print("Filter Text", flush=True)
    soup = BeautifulSoup(file, 'html.parser')
    all = ""
    for p in soup.find_all('p'):
        all += p.get_text() + "\n\n"
    print(all)
    return all


def ReadText(text, index):
    print("Text to Audiofile: " + str(index), flush=True)
    outfile = str(index) + ".wav"
    engine.setProperty('voice', "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0")
    engine.save_to_file(text, outfile)
    engine.runAndWait()


def FileFromURL(url):
    print("Request File of: " + url, flush=True)
    try:
        request = urllib.request.Request(url, None, headers=hdr)
    except:
            print("Error Requesting: " + url)
    file = urllib.request.urlopen(request).read()
    return file


def Translate(text):
    translator = GoogleTranslator(source='auto', target='en')
    splitted_text = text.split("\n")
    while '' in splitted_text:
        splitted_text.remove('')
    translation = ""
    for split in splitted_text:
        print("line: " + split, flush=True)
        try:
            temp = translator.translate(split)
        except (exceptions.NotValidPayload):
            temp = split
        if temp:
            print("translated line: " + temp, flush=True)
            translation +=  temp + "\n"
    return translation


if __name__ == "__main__":
    layout = [[sg.Text('BaseURL')], [sg.InputText(key='BaseURL')], 
             [sg.Text('StartURL')], [sg.InputText(key='StartURL')], 
             [sg.Text('HyperLinkText')], [sg.InputText(key='HyperLinkText')], 
             [sg.Text('SearchDepth')], [sg.InputText(key='SearchDepth')],
             [sg.Button("TTS"), sg.Button("Close")]]
    window = sg.Window('URL TTS', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        if event == "TTS":
            print("start crawling:", flush=True)
            urllist = crawl(values.get("BaseURL"), values.get("StartURL"),  values.get("HyperLinkText"), values.get("SearchDepth"))
            print("start TTS:", flush=True)
            for url in urllist:
                ReadText(Translate(TextOfHtml(FileFromURL(url))), urllist.index(url))
            print("Done", flush=True)  
        if event == "Close":
            window.close()
    window.close()
