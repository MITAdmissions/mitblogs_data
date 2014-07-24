##looks up facebook social data for every mitadmissions blog post 
##code by @peteyreplies

from bs4 import BeautifulSoup
import os
import csv
import string
import urllib
import urllib2
import re
import unicodedata
import json
from datetime import datetime
from datetime import timedelta
import time
from time import sleep 

#load every link and get data 
x = open('blogLinks.txt')
links = []
links = x.read().splitlines()
entries = []
for i in links:
	##scrape data from blogs
	entryHTML = urllib2.urlopen(i).read()
	entrySoup = BeautifulSoup(entryHTML)

	##scrape data from facebook
	url = 'https://api.facebook.com/method/links.getStats?urls=%%' + i + '&format=json'
	fb = json.load(urllib2.urlopen(url))

	##load / clean data in place 
	#blogs
	print i
	link = i
	author = entrySoup.find(id='blogger-meta').contents[1].string.encode('ascii','ignore')

	#many of becca's blogs are broken, so skip her for now (jump to top of while loop)
	if 'Becca H.' in author: continue

	#if not BrokenBecca, go ahead and load everything 
	date = entrySoup.find(id='blog-meta').contents[1].string.encode('ascii','ignore')#.replace(',', '')
	if ',' in date:
		date = date.replace(',', '')
	title = entrySoup.find(id='blog-meta').contents[3].string.encode('ascii','ignore')
	stamp = time.mktime(time.strptime(date, "%b %d %Y"))
	delta = (datetime.utcnow().date() - datetime.fromtimestamp(stamp).date()).days
	
	#fb 
	fb_comments = fb[0]['comment_count']
	fb_likes = fb[0]['like_count']
	fb_shares = fb[0]['share_count']
	fb_total = fb_comments + fb_likes + fb_shares

	#add to dict
	entry = {
				'DATE POSTED': date,
				'AUTHOR': author,
				'TITLE': title,
				'LINK': link,
				#'Timestamp': stamp,
				'DAYS SINCE POSTED': delta,
				'LIKES': fb_likes,
				'SHARES': fb_shares,
				'COMMENTS': fb_comments,
				'TOTAL ENGAGEMENT': fb_total,
				#'Likes + Shares': fb_spread,
	}
	entries.append(entry)

	#wait 2 seconds before asking facebook again to avoid rate limits
	#sleep (2)

##write to csv and save to directory 
keys = ['DATE POSTED', 'AUTHOR', 'TITLE', 'LINK', 'DAYS SINCE POSTED', 'LIKES','SHARES','COMMENTS','TOTAL ENGAGEMENT']
f = open ('../DATADUMP/fbData.csv','wb')
DW = csv.DictWriter(f,keys)
DW.writer.writerow(keys)
DW.writerows(entries)
