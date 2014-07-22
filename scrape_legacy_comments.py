##scrapes legacy (movabletype/ee) comments from mitadmissions.org
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

conn = sqlite3.connect("../DATADUMP/blogLegacyComments.db")
db = conn.cursor()
db.execute('''CREATE TABLE IF NOT EXISTS legacyComments (COMMENTER TEXT, DATE_POSTED DATE, 
				TIME_STAMP TIMESTAMP, COMMENT_TEXT TEXT, ENTRY TEXT)''')

x = open('allBlogLinks.txt')
links = []
links = x.read().splitlines()
for i in links:
	##scrape data from each entry into soup 
	entryHTML = urllib2.urlopen(i).read()
	entrySoup = BeautifulSoup(entryHTML)

	#print which link you're on for debugging
	print i

	#are there comments here?
	hasComments = entrySoup.find('div',class_="comment")
	if hasComments == None:
		continue
	else:
		hasComments = True
		comments = entrySoup.find_all('div', id='', class_='comment')
		for c in comments:
			posted = c.find(class_='commenter').getText().encode('ascii','ignore')
			postedBy = posted.lstrip('Posted by: ')
			print postedBy #for debugging
			postedDateList = postedBy.split()[-3:]
			date = ''
			for d in postedDateList:
				date = date + d + ' '
			date = date.rstrip(' ').replace(',', '')
			stamp = time.mktime(time.strptime(date, "%B %d %Y"))
			postedUserList = postedBy.split()[:-4]
			user = ''
			for u in postedUserList:
				user = user + u + ' '
			user = user.rstrip(' ')
			text = c.getText().replace(posted,'').replace('\n',' ').encode('ascii','ignore')

			##insert these values into database
			db.execute('INSERT INTO legacyComments VALUES (?, ?, ?, ?, ?)',
          	(user, date, stamp, text, i))
			conn.commit()

			##write 
			with open('../DATADUMP/legacyComments.txt', 'a') as out_file:
				out_file.write(' ' + text)