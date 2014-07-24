#####
#custom functions for scraping the MITAdmissions blogs
#experimental, unconventional, mostly horrible code by @peteyreplies
####

##petey todo 
# - add comment sentiment score via DSTK call 
# - add google analytics function 
# - maybe break up meta entries even further - one for getting date, another for title, etc 
# - split up this doc into several different subdocs, i.e. for meta, comments, analytics, entities, etc 
# - tweets? 

##import various libraries we will need 
import nltk 							#lol 
import csv								#in case we need to write to csv
import string							#to do fancy string operations
import urllib, urllib2 					#to load URLs 
import json 							#to parse api strings 						
import sqlite3							#to connect to database 
import time 							#to compute time 
import datetime							#to convert time 
#from datetime import datetime 			#to convert times  
from datetime import timedelta			#to compute change in time
from bs4 import BeautifulSoup			#to scrape through html 

##load some private resources for later calling 
#get the API key for disqus
f = open('../RESOURCES/disqus_api_key.txt') 
disqusKey = f.read()

#get the URL for Civic CLIFF production server 
c = open('../RESOURCES/civic_cliff_server.txt')
cliffServer = c.read() 

#get the API key for google analytics
g = open('../RESOURCES/google_api_key.txt') 
disqusKey = g.read()

#define some base URLs for later requests 
fbBase = 'https://api.facebook.com/method/links.getStats?urls=%%'
fbEnd = '&format=json'
disqusCountBase = 'http://disqus.com/api/3.0/threads/list.json?api_key='
disqusContentBase = 'http://disqus.com/api/3.0/posts/list.json?api_key='
disqusMid = '&forum=mitadmissions&thread=link:'


##define custom functions
def getBlogLinks(num):
	'''scrapes however many pages of blogs are passed, writes to text file, returns filename'''

	#setup the file this will be written to 
	now = datetime.datetime.fromtimestamp(time.time()).strftime(' as of %b %d %Y at %H_%M')
	filename = '../DATADUMP/bloglinks/'+ str(num) + 'BlogsLinks' + now + '.txt'
	blogLinks = open(filename,'a')

	baseURL = "http://mitadmissions.org/blogs/P"
	p = 0
	baseURL = "http://mitadmissions.org/blogs/P"
	p = 0
	while p<= num:
		html = urllib2.urlopen(baseURL + str(p)).read()
		entrySoup = BeautifulSoup(html)
		linkSoup = entrySoup.find_all("h3")
		for link in linkSoup:
			thisLink = str(link.a['href'])
			blogLinks.write("%s\n" % thisLink)
			print thisLink
		p = p + 20 
	blogLinks.close()
	return filename

def getCurrentBloggers():
	'''returns a list of current student bloggers'''
	currentBloggers = []
	bloggersHTML = urllib2.urlopen('http://mitadmissions.org/blogs/group/students').read()
	bloggersSoup = BeautifulSoup(bloggersHTML)
	bloggersNames = bloggersSoup.find_all("h5")
	for blogger in bloggersNames:
		currentBloggers.append(blogger.string.encode('ascii','ignore'))
	return currentBloggers

def getEntrySoup(link):
	'''takes a link and returns Soup'''
	entryHTML = urllib2.urlopen(link).read()
	entrySoup = BeautifulSoup(entryHTML)
	return entrySoup

def getEntryMeta(entrySoup, currentBloggers):
	'''takes a soup of a blog entry & list of current bloggers, returns dict of entry metadata'''
	
	#get their username, stored in the <h5> tag of the blogger-meta div 
	author = entrySoup.find(id='blogger-meta').find('h5').string.encode('ascii','ignore')
	
	#are they a current student blogger?
	current = False
	if author in currentBloggers:
		current = True

	#get their course (some guest / alum bloggers don't have courses, so test for it first) 
	if entrySoup.find(id='blogger-meta').find('p') == None:
		course = "None"
	else: 
		course = entrySoup.find(id='blogger-meta').find('p').string.encode('ascii','ignore')
	
	#get the post title, stored in the <h2> tag of the blog-meta div
	title = entrySoup.find(id='blog-meta').find('h2').string.encode('ascii','ignore')

	#get post categories & add to a string (structure would be nice later)
	cats = ""
	theseCats = entrySoup.find('p', class_='categories').find_all('a')
	for c in theseCats:
		cats = cats + c.string + ","

	raw_date = entrySoup.find(id='blog-meta').contents[1].string.encode('ascii','ignore')
	#if there is a comma, remove it 
	if ',' in raw_date:
		raw_date = raw_date.replace(',', '')
	#convert to timestamp 
	stamp = time.mktime(time.strptime(raw_date, "%b %d %Y"))
	#now covert back to full month name for easier parsing 
	date = datetime.datetime.fromtimestamp(stamp).strftime('%B %d %Y')

	#compute delta 
	delta = (datetime.utcnow().date() - datetime.fromtimestamp(stamp).date()).days

	#write all of this to a dict 
	entryMeta = {
						'entry_author': author,
						'author_course': course,
						'entry_title': title,
						'entry_categories': cats,
						'entry_date': date,
						'entry_stamp':stamp,
						'entry_delta': delta,
						'author_currentBlogger?':current,
						}
	return entryMeta

def getBasicMeta(entrySoup, link):
	'''takes soup and returns a dict of basic, often-used metadata'''

	raw_date = entrySoup.find(id='blog-meta').contents[1].string.encode('ascii','ignore')
	#if there is a comma, remove it 
	if ',' in raw_date:
		raw_date = raw_date.replace(',', '')
	#convert to timestamp 
	stamp = time.mktime(time.strptime(raw_date, "%b %d %Y"))
	#now covert back to full month name for easier parsing 
	date = datetime.datetime.fromtimestamp(stamp).strftime('%B %d %Y')

	#some metadata 
	basicMeta = {
				  'entry_title': entrySoup.find(id='blog-meta').find('h2').string.encode('ascii','ignore'),
				  'entry_author': entrySoup.find(id='blogger-meta').find('h5').string.encode('ascii','ignore'),
				  'entry_date': date,
				  'entry_stamp': stamp,
				  'entry_link': link,
				}
	return basicMeta
	

def getEntryText(entrySoup):
	'''takes a soup of a blog entry and returns a string of that entry's text'''

	#put every <p> (which lacks other ids / classes) into a list of strings 
		#note: this loses entry text in (e.g.) lists & blockquotes! fix later 
	lines = entrySoup.find_all('p', id='', class_='')

	#remove the 'see complete archives' line which always comes first 
	lines.pop(0)

	#then, iterate through this list of strings, get and clean the text, and add to big string
	entryText = ""
	for l in lines:
		#make sure this isn't the comments lines at the end of legacy comment system posts
		if "Comments have been closed" in l:
			break
		if "No comments yet" in l:
			break 
		#otherwise, get the text of the line, 
		thisLine = l.getText().encode('ascii','ignore').replace('\n','').replace('\\','').replace('\t','')
		entryText = entryText + thisLine

	return entryText

def getEntryCommentCount(entrySoup, link):
	'''takes a soup & a link and returns associated comment count for either legacy or disqus'''

	#if it has a comment class, it's legacy system, & just count len of list of comment classes
	if entrySoup.find('div',class_="comment") != None:
		comments = len(entrySoup.find_all('div', id='', class_='comment'))
	
	#if not, it's disqus, so ask their API for how many posts that thread has 
	else:
		disqusData = json.load(urllib2.urlopen(disqusCountBase + disqusKey + disqusMid + link))
		comments = disqusData['response'][0]['posts']

	return comments

def getEntryFBData(link):
	'''takes a link and returns a dict of facebook engagement data'''

	#ask for engagement data from facebook's API
	fbd = json.load(urllib2.urlopen(fbBase + link + fbEnd))
	fbc = fbd[0]['comment_count']
	fbl = fbd[0]['like_count']
	fbs = fbd[0]['share_count']
	fbt = fbc + fbl + fbs

	fbData = {
				'FB_LIKES': fbl,
				'FB_SHARES': fbs,
				'FB_COMMENTS': fbc,
				'FB_ENGAGEMENT': fbt,
				}

	return fbData

def getLegacyComments(entrySoup, link):
	'''takes soup & link and returns a list of dicts for comments associated w/ that entry'''

	#construct a list of soup components which have a comment class 
	rawComments = entrySoup.find_all('div', id='', class_='comment')
	cleanedComments = []

	#get basicMeta for this soup
	basicMeta = getBasicMeta(entrySoup)

	#for each item in the comment list 
	for c in rawComments:

		#grab commenter class & clean out the standard 'posted by' leading language 
		posted = c.find(class_='commenter').getText().encode('ascii','ignore')
		cleaned = posted.lstrip('Posted by: ')

		#grab last 3 elements of posted (components of date) & format as date
		postedDateList = cleaned.split()[-3:]
		date = ''
		for d in postedDateList:
			date = date + d + ' '
		date = date.rstrip(' ').replace(',', '')
		stamp = time.mktime(time.strptime(date, "%B %d %Y"))
		
		#now pop the last 4 (date) elements out, you're left w/ the username 
		postedUserList = cleaned.split()[:-4]
		user = ''
		for u in postedUserList:
			user = user + u + ' '
		user = user.rstrip(' ')

		#last, grab the text of the comment 
		text = c.getText().replace(posted,'').replace('\n',' ').encode('ascii','ignore')

		#what type of comment is this? 
		system = 'legacy'

		thisComment = {
						'commenter': user,
						'comment_date':date,
						'comment_stamp': stamp,
						'comment_text': text,
						'comment_system': system,
						'link':link, 
											}
		thisComment.update(basicMeta)
		cleanedComments.append(thisComment)

	return cleanedComments

def getDisqusComments(entrySoup, link):
	'''takes soup & link and returns a list of dicts for comments associated w/ that entry'''

	#get basicMeta for this Soup
	basicMeta = getBasicMeta(entrySoup)

	#create a place to put the comments 
	cleanedComments = [] 

	#give disqus API link, get back dict of 'posts' i.e. comments 
	disqusData = json.load(urllib2.urlopen(disqusContentBase + disqusKey + disqusMid + link))

	#inside that dict is a list; inside that list is a dict, so loop & get comments
	for c in disqusData['response']: 
		
		#get the text of the comment 
		text = ['raw_message'].encode('ascii','ignore')

		#get the commenter's name 
		user = ['author']['name'].encode('ascii','ignore')

		#get & format date of the comment 
		raw_date = ['createdAt'].encode('ascii','ignore')[0:10]
		stamp = time.mktime(time.strptime(raw_date, '%Y-%m-%d'))
		date = datetime.datetime.fromtimestamp(stamp).strftime('%b %d %Y')

		#what type of comment is this? 
		system = 'disqus'

		thisComment = {
						'commenter': user,
						'comment_date':date,
						'comment_stamp': stamp,
						'comment_text': text,
						'comment_system': system,
						'entry_link': link, 
											}
		thisComment.update(basicMeta)
		cleanedComments.append(thisComment)
	return cleanedComments

def getCLIFFData(entryText):
	'''takes the entryText and runs it against the Civic CLIFF server for analysis, returns a json dict. based on code by @natematias'''
	
	#query the server for analysis 
	text = {"q":entryText}
	query = urllib.urlencode(text)
	req = urllib2.Request(cliffServer,query)
	cliffData = json.loads((urllib2.urlopen(req).read()))

	return cliffData
		
def getEntryOrgs(basicMeta, cliffData, link):
	'''takes the soup, cliffData, and a link, extracts organizations, returns a list of dicts'''

	#create a list to hold the dicts of orgs
	organizations = []

	##if any orgs,  
	if cliffData['results']['organizations'] != None: 
		for o in cliffData['results']['organizations']:
			thisOrg = {
						'orgCount': o['count'].encode('ascii','ignore'),
						'orgName': o['name'].encode('ascii','ignore'),
						'entry_url': link, 
					  }
			thisOrg.update(basicMeta)
			organizations.append(thisOrg)
	return organizations

def getEntryPeople(basicMeta, cliffData, link):
	'''takes the soup, cliffData, and a link, extracts people, returns a list of dicts'''

	#create a list to hold the dicts of orgs
	people = []

	##if any orgs,  
	if cliffData['results']['people'] != None: 
		for p in cliffData['results']['people']:
			thisPerson = {
						'personCount': p['count'].encode('ascii','ignore'),
						'personName': p['name'].encode('ascii','ignore'),
						'entry_url': link, 
					  }
			thisPerson.update(basicMeta)
			people.append(thisPerson)
	return people

def getEntryPlaces(basicMeta, cliffData, link):
	'''takes the soup, cliffData, and a link, extracts people, returns a list of dicts'''

	#create a list to hold the dicts of orgs
	places = []

	##if any places mentioned (not about), grab some *very basic* data   
	if cliffData['results']['places']['mentions'] != None: 
		for m in cliffData['results']['places']['mentions']:
			thisPlace = {
						'placeName': m['name'].encode('ascii','ignore'),
						'countryCode': m['countryCode'].encode('ascii','ignore'),
						'latitude': m['lat'],
						'longitude': m['lon'],
						'population': m['population'],
						'entry_url': link, 
					  }
			thisPlace.update(basicMeta)
			places.append(thisPlace)
	return places

#def getGoogleAnalyticsData(link):
	'''takes a link and returns # of unique pageviews from GA'''
