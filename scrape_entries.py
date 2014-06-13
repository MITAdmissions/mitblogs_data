##scrapes lots of stuff from individual blog entries on mitadmissions.org
##code by @peteyreplies

#import some stuff
import os
import csv
import string
import urllib
import urllib2
import re
import unicodedata
import sqlite3
import time
from datetime import datetime
from datetime import timedelta
from bs4 import BeautifulSoup

#load list of links from which to scrape data 
x = open('blogLinks.txt')
links = []
links = x.read().splitlines()
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

	#some guest bloggers don't have courses, so test for it 
	if entrySoup.find(id='blogger-meta').find('p') == None:
		course = "null"
	else: 
		course = entrySoup.find(id='blogger-meta').find('p').string.encode('ascii','ignore')
	title = entrySoup.find(id='blog-meta').find('h2').string.encode('ascii','ignore')
	
	#parse categories & add to string/structure
	cats = ""
	theseCats = entrySoup.find('p', class_='categories').find_all('a')
	for c in theseCats:
		cats = cats + c.string + ","

	#parse date, timestamps, and days since posted 
	date = entrySoup.find(id='blog-meta').contents[1].string.encode('ascii','ignore')
	#if there is a comma, remove it, so time.strptime can parse it 
	if ',' in date:
		date = date.replace(',', '')
	stamp = time.mktime(time.strptime(date, "%b %d %Y"))
	delta = (datetime.utcnow().date() - datetime.fromtimestamp(stamp).date()).days

	##get entry text into one long string 
	lines = entrySoup.find_all('p', id='', class_='')

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

##write to sqlite database, which is located 1 level up to not clog repo
conn = sqlite3.connect("../blogEntries.db")
db = conn.cursor()
db.execute('''CREATE TABLE IF NOT EXISTS mitblogs (AUTHOR TEXT, DATE_POSTED DATE, 
				TITLE TEXT, COURSE TEXT, CATEGORIES TEXT, LINK TEXT, TIME_STAMP TIMESTAMP, 
				DAYS SINCE POSTED TEXT, ENTRYTEXT TEXT)''')

for s in entries:
	db.execute('INSERT INTO mitblogs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
          (s['AUTHOR'], s['DATE POSTED'], s['TITLE'], s['COURSE'], s['CATEGORIES'],
          	s['LINK'], s['TIMESTAMP'], s['DAYS SINCE POSTED'], s['ENTRY TEXT']))
	conn.commit()

conn.close()
