##scrapes lots of stuff from individual blog entries on mitadmissions.org
##code by @peteyreplies

#import some stuff
from bs4 import BeautifulSoup
import os
import csv
import string
import urllib
import urllib2
import re
import unicodedata
import datetime
import time
import sqlite3

#load list of links from which to scrape data 
f = open('someBlogLinks.txt')
links = []
links = f.read().splitlines()
entries = []
for i in links:
	##scrape data from each entry into soup 
	entryHTML = urllib2.urlopen(i).read()
	entrySoup = BeautifulSoup(entryHTML)

	#print which link you're on for debugging
	print i

	#begin assigning data 
	link = i
	author = entrySoup.find(id='blogger-meta').find('h5').string.encode('ascii','ignore')
	#if not BrokenBecca, continue the loop and load more metadata
	if 'Becca H.' in author: continue

	course = entrySoup.find(id='blogger-meta').find('p').string.encode('ascii','ignore')
	title = entrySoup.find(id='blog-meta').find('h2').string.encode('ascii','ignore')
	
	#parse categories & add to string/structure
	cats = ""
	#catList = []
	theseCats = entrySoup.find('p', class_='categories').find_all('a')
	for c in theseCats:
		#catList.append(c.string)
		cats = cats + c.string + ","

	#parse date, timestamps, and days since posted 
	date = entrySoup.find(id='blog-meta').contents[1].string.encode('ascii','ignore')
	#if there is a comma, remove it, so time.strptime can parse it 
	if ',' in date:
		date = date.replace(',', '')
	stamp = time.mktime(time.strptime(date, "%b %d %Y"))
	delta = (datetime.utcnow().date() - datetime.fromtimestamp(stamp).date()).days

	##get entry text into one long string 
	lines = soup2.find_all('p', id='', class_='')

	#remove the 'see complete archives' outlier which always comes first 
	lines.pop(0)

	#then, iterate through this list of strings, get and clean the text, and add to big string
	entryText = ""
	for l in lines:
		if "Comments have been closed" in l:
			break
		if "No comments yet" in l:
			break 
		thisLine = l.getText().encode('ascii','ignore').replace('\n','').replace('\\','').replace('\t','')
		entryText = entryText + thisLine

	#now, write all this to a dict, and append that dict to the list 
	entry = {
				'DATE POSTED': date,
				'AUTHOR': author,
				'TITLE': title,
				'COURSE': course,
				'CATEGORIES': cats,
				'LINK': link,
				'TIMESTAMP': stamp,
				'DAYS SINCE POSTED': delta,
				'ENTRY TEXT': entryText,
				}
	entries.append(entry)





