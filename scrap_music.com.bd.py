#!/usr/bin/env python3
from bs4 import BeautifulSoup
import requests
import threading
import urllib
import sys
import re
import os
#base = "http://www.music.com.bd/download/browse/A/Ark/"
if len(sys.argv) < 2:
    exit(0)
if "https" in sys.argv[1]:
    base = "http" + sys.argv[1][5:]
else:    
    base = sys.argv[1]
regex = r'^'+base+"([a-zA-Z0-9\s]){1,}"

STAT = dict()

def mp3Writer(albumname, url):
    STAT[albumname][url[url.rfind('/')+1:]] = dict()
    if os.path.exists(albumname + os.path.sep + url[url.rfind('/')+1:]):
        STAT[albumname]["files"]["skipped"].append(url[url.rfind('/')+1:])
        return
    with open(albumname + os.path.sep + url[url.rfind('/')+1:],'wb') as mp3:
        mp3.write(requests.get(url).content)
        STAT[albumname]["files"]["created"].append(url[url.rfind('/')+1:])


soup = BeautifulSoup(requests.get(base).content,'html.parser').find('div',{"class":'list-group'})
for album in (soup.find_all('a',{'class':'list-group-item'})):
    if re.match(regex,album.get('href')):
        albumname = urllib.parse.unquote(album.get('href'))
        albumname = albumname[0:albumname.rfind('/')]
        albumname = albumname[albumname.rfind('/')+1:]
        try:
            STAT[albumname] = dict()
            STAT[albumname]["files"] = dict()
            STAT[albumname]["files"]["skipped"] = list()
            STAT[albumname]["files"]["created"] = list()
            os.mkdir(albumname)
            STAT[albumname]["skipped"] = False
        except FileExistsError:
            STAT[albumname]["skipped"] = True
        for data in BeautifulSoup(requests.get(album.get('href')).content,'html.parser').find_all('a',{'class':'list-group-item'}):
            if 'mp3' in data.get('href'):
                url = "http:" + str(data.get('href'))[:-5]
                threading.Thread(target=mp3Writer,args=(albumname,url)).start()
