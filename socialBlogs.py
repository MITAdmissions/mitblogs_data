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

##get list of best of the blogs links 
#define a base URL & page variable to increment 
baseURL = "http://mitadmissions.org/blogs/P"
p = 0 
headers = { 'User-Agent' : 'PeteyBlogBot' }

#loop through & download last (p==80 for test, p<=4600 for production as of 5/14/2014) blog links into a single stupidly huge document  
links = []
baseURL = "http://mitadmissions.org/blogs/P"
p = 0
while p<= 4600:
	html = urllib2.urlopen(baseURL + str(p)).read()
	entrySoup = BeautifulSoup(html)
	linkSoup = entrySoup.find_all("h3")
	for link in linkSoup:
		thisLink = str(link.a['href'])
		links.append(thisLink)
	p = p + 20

#load every link and get data 
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
	link = i
	author = entrySoup.find(id='blogger-meta').contents[1].string.encode('ascii','ignore')
	date = entrySoup.find(id='blog-meta').contents[1].string.encode('ascii','ignore').replace(',', '')
	title = entrySoup.find(id='blog-meta').contents[3].string.encode('ascii','ignore')
	stamp = time.mktime(time.strptime(date, "%b %d %Y"))
	delta = (datetime.utcnow().date() - datetime.fromtimestamp(stamp).date()).days
	
	#fb 
	fb_total = fb[0]['total_count']
	fb_comments = fb[0]['comment_count']
	fb_likes = fb[0]['like_count']
	fb_shares = fb[0]['share_count']
	#fb_spread = fb_likes + fb_shares

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
	sleep (2)

##write to csv and save to directory 
keys = ['DATE POSTED', 'AUTHOR', 'TITLE', 'LINK', 'DAYS SINCE POSTED', 'LIKES','SHARES','COMMENTS','TOTAL ENGAGEMENT']
f = open ('fbData.csv','wb')
DW = csv.DictWriter(f,keys)
DW.writer.writerow(keys)
DW.writerows(entries)
