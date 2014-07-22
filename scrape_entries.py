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
import json

#open database connection 
conn = sqlite3.connect("../DATADUMP/blogEntries.db")
db = conn.cursor()
db.execute('''CREATE TABLE IF NOT EXISTS mitblogs (AUTHOR TEXT, DATE_POSTED DATE, 
				TITLE TEXT, COURSE TEXT, CURRENT_BLOGGER BOOLEAN, CATEGORIES TEXT, LINK TEXT, TIME_STAMP TIMESTAMP, 
				DAYS_SINCE_POSTED INTEGER, ENTRYTEXT TEXT, COMMENTS INTEGER)''')

#who is currently a student blogger?
bloggers = []
bloggersHTML = urllib2.urlopen('http://mitadmissions.org/blogs/group/students').read()
bloggersSoup = BeautifulSoup(bloggersHTML)
bloggersNames = bloggersSoup.find_all("h5")
for blogger in bloggersNames:
	bloggers.append(blogger.string.encode('ascii','ignore'))

#set disqus base for later calling
disqusBase = 'http://disqus.com/api/3.0/threads/list.json?api_key=BytFIyujEVgnm4f00zNbvYUnOMeOnnSi2ri8LUWDpSM9ebQ2T1CLWB12Kn6PtLN7&forum=mitadmissions&thread=link:'
fbBase = 'https://api.facebook.com/method/links.getStats?urls=%%' 
fbEnd = '&format=json'

#load list of links from which to scrape data 
x = open('allBlogLinks.txt')
links = []
links = x.read().splitlines()
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

	#are they a current student blogger?
	currentBlogger = False
	if author in bloggers:
		currentBlogger = True

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
	
	#look for & count comments 
	hasDisqus = entrySoup.find('div',id='disqus_thread')
	hasLegacy = entrySoup.find('div',class_="comment")
	comments = 0
	dVotes = 0
	if hasDisqus != None:
		disqusBase 
		commentData = json.load(urllib2.urlopen(disqusBase + link))
		comments = commentData['response'][0]['posts']
	elif hasLegacy != None:
		commentData = entrySoup.find_all('div', id='', class_='comment')
		comments = len(commentData)

	#get FB engagement 
	fb = json.load(urllib2.urlopen(fbBase + link + fbEnd))
	fb_comments = fb[0]['comment_count']
	fb_likes = fb[0]['like_count']
	fb_shares = fb[0]['share_count']
	fb_total = fb_comments + fb_likes + fb_shares

	##insert these values into database
	db.execute('INSERT INTO mitblogs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
          (author, date, title, course, currentBlogger, cats,
          	link, stamp, delta, entryText, comments))
	conn.commit()

conn.close()
