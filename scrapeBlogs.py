#####
# functions for scraping the MITAdmissions blogs
# by @peteyreplies
####

##import various libraries we will need 
import nltk 									#for hitting CLIFF 
import dstk										#to do DATA SCIENCE
import string									#to do fancy string operations
import urllib, urllib2 							#to load URLs 
import json 									#to parse api strings 						
import time 									#to compute time 	
from datetime import datetime, timedelta, date 	#to convert time  
from bs4 import BeautifulSoup					#to scrape through html

##load some private resources for later calling 
today = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d')

#load API keys & other credentials 
disqusKey = (open('../RESOURCES/disqus_api_key.txt')).read() 
cliffServer = (open('../RESOURCES/civic_cliff_server.txt')).read()

#define some base URLs for later requests 
fbBase = 'https://api.facebook.com/method/links.getStats?urls=%%'
fbEnd = '&format=json'
disqusCountBase = 'http://disqus.com/api/3.0/threads/list.json?api_key='
disqusContentBase = 'http://disqus.com/api/3.0/posts/list.json?api_key='
disqusMid = '&forum=mitadmissions&thread=link:'
countTweets = 'http://urls.api.twitter.com/1/urls/count.json?url='

#initiate a DSTK instance (use private server once RAM upgraded)
ds = (open('../RESOURCES/admdstk.txt')).read()
dstk = dstk.DSTK({'apiBase':ds})
#dstk = dstk.DSTK()

##define custom functions
#getting links to be analyzed 
def getBlogLinks(num):
	'''scrapes however many pages of blogs are passed, writes to text file, returns filename'''
	#setup the file this will be written to 
	now = datetime.fromtimestamp(time.time()).strftime(' as of %b %d %Y at %H_%M')
	filename = '../DATADUMP/bloglinks/'+ str(num) + ' BlogsLinks' + now + '.txt'
	blogLinks = open(filename,'a')
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

def getSomeBloggers(link):
	'''takes a link & returns a list of bloggers in that link's soup'''
	theseBloggers = []
	theseBloggersHTML = urllib2.urlopen(link).read()
	theseBloggersSoup = BeautifulSoup(theseBloggersHTML)

	#find blogger names (formatted w/ the h5 tag)
	theseBloggersNames = theseBloggersSoup.find_all("h5")

	#loop through the soup grabbing blogger names & appending to list 
	for t in theseBloggersNames:
		theseBloggers.append(t.string.encode('ascii','ignore'))
	return theseBloggers


def getAllBloggers():
	'''returns a dict of blogger:type pairs'''
	bloggers = {}

	#get lists of each type of bloggers 
	currentBloggers = getSomeBloggers('http://mitadmissions.org/blogs/group/students')
	staffBloggers = getSomeBloggers('http://mitadmissions.org/blogs/group/staff')
	guestBloggers = getSomeBloggers('http://mitadmissions.org/blogs/group/guests')
	alumBloggers = getSomeBloggers('http://mitadmissions.org/blogs/group/alums')

	#loop thru each list & add key[authorname]:value[authortype]
	for c in currentBloggers:
		bloggers[c] = 'currentBlogger'

	for s in staffBloggers:
		bloggers[s] = 'staffBlogger'

	for g in guestBloggers:
		bloggers[g] = 'guestBlogger'

	for a in alumBloggers: 
		bloggers[a] = 'alumBlogger'
	return bloggers


#getting entry metadata
def getLinkPath(link): 
	'''takes a link and returns the unique part (after the last slash) as a string'''
	path = link.rsplit('/')[-1]
	return path 

def getEntryHTML(link):
	'''takes a link and returns the entry's HTML'''
	entryHTML = urllib2.urlopen(link).read()
	return entryHTML

def getEntrySoup(entryHTML):
	'''takes entryHTML and returns BeautifulSoup object of the associated entry'''
	entrySoup = BeautifulSoup(entryHTML)
	return entrySoup

def getEntryAuthor(entrySoup):
	'''takes soup & returns author of the entry'''
	author = entrySoup.find(id='blogger-meta').find('h5').string.encode('ascii','ignore')
	return author

def getBloggerType(entrySoup, bloggers):
	'''takes soup & dict, returns type of blogger''' 
	author = getEntryAuthor(entrySoup)
	bloggerType = bloggers.get(author)
	return bloggerType


def getAuthorCourse(entrySoup):
	'''takes soup & returns the course of the entry's author (if applicable)'''
	#get their course (some guest / alum bloggers don't have courses, so test for it first) 
	if entrySoup.find(id='blogger-meta').find('p') == None:
		course = "None"
	else: 
		course = entrySoup.find(id='blogger-meta').find('p').string.encode('ascii','ignore')
	return course


def getEntryTitle(entrySoup):
	'''takes soup & returns the title of the post'''
	#get the post title, stored in the <h2> tag of the blog-meta div
	title = entrySoup.find(id='blog-meta').find('h2').string.encode('ascii','ignore')
	return title


def getCategories(entrySoup):
	'''takes soup & returns the entry's categories as a string'''
	cats = entrySoup.find('p', class_='categories').find_all('a')
	categories = ''
	for c in cats:
		thisCat = c.string.encode('ascii', 'ignore')
		categories = categories + thisCat + ' '
	return categories


def getEntryDateTime(entrySoup):
	'''takes soup & returns a dict of date and time stuff''' 
	raw_date = entrySoup.find(id='blog-meta').contents[1].string.encode('ascii','ignore')
	#if there is a comma, remove it 
	if ',' in raw_date:
		raw_date = raw_date.replace(',', '')

	#convert to stamp 
	stamp = time.mktime(time.strptime(raw_date, '%b %d %Y'))

	#convert stamp back to more readable date
	#date = datetime.fromtimestamp(stamp).strftime('%B %d %Y') // more human readable but less computable
	date = datetime.fromtimestamp(stamp).strftime('%m-%d-%Y')

	#compute delta 
	delta = (datetime.utcnow().date() - datetime.fromtimestamp(stamp).date()).days
	
	#create dict 
	entryDateTime = {
						'entry_date': date,
						'entry_stamp': stamp,
						'entry_delta': delta,
	}
	return entryDateTime 

def getBasicMeta(entrySoup, link):
	'''takes soup & link, returns basic, commonly used metadata'''
	basicMeta = {
					'entry_author': getEntryAuthor(entrySoup),
					'entry_title': getEntryTitle(entrySoup),
					'entry_link': link,
					}
	basicMeta.update(getEntryDateTime(entrySoup))
	return basicMeta


def getEntryLines(entryHTML):
	'''takes entryHTML, runs it against the DSTK story extractor, & returns a list of lines''' 
	#run the HTML against DSTK's boilerpipe story detection service  
	text = dstk.html2story(entryHTML)

	#grab the value of the returned dict & read it into an ASCII string 
	textstring = text['story'].encode('ascii','ignore')

	#split at newline character for cleaning & counting 
	lines = textstring.split('\n')

	#remove the categories entry w/ comes first & the last two blank spaces 
	lines.pop(0)
	return lines

def getEntryText(entryLines):
	'''takes a list of lines in an entry and returns a string of them all stuck together'''
	entryText = ''
	for l in entryLines:
		entryText = entryText + l + ' ' 
	return entryText

def getEntryWords(entryText):
	'''takes a string of an entry's text & returns count of words based on whitespace split''' 
	words = entryText.split(' ')
	return len(words)


#getting entry comment counts & comment content 
def getEntryCommentSystem(entrySoup):
	'''takes soup & returns a string of the type of comment system'''
	#if it has a comment class, it's legacy system, & just count len of list of comment classes
	if entrySoup.find('div',class_="comment") != None:
		system = 'legacy'
	else: 
		system = 'disqus'
	return system


def getEntryCommentCount(entrySoup, link):
	'''takes a soup & link and returns associated comment count'''
	if getEntryCommentSystem == 'legacy':
		comments = len(entrySoup.find_all('div', id='', class_='comment'))
	else:
		disqusData = json.load(urllib2.urlopen(disqusCountBase + disqusKey + disqusMid + link))
 		comments = disqusData['response'][0]['posts']
 	return comments

def getCommentSentiment(commentText):
	'''takes a string of a comment & returns int of sentiment computed by DSTK'''
	sentiment = dstk.text2sentiment(commentText)['score']
	return sentiment

def getLegacyComments(entrySoup, link):
	'''takes soup & link and returns a list of dicts for comments associated w/ that entry'''
	#get the basic meta for the associated entry 
	basicMeta = getBasicMeta(entrySoup, link)

	#construct a list of soup components which have a comment class 
	rawComments = entrySoup.find_all('div', id='', class_='comment')
	cleanedComments = []

	#for each item in the comment list
	#set ordinal rank for computing firstpost 
	num = 0

	for c in rawComments:
		num = num + 1 

		#grab commenter class & clean out the standard 'posted by' leading language 
		posted = c.find(class_='commenter').getText().encode('ascii','ignore')
		cleaned = posted.lstrip('Posted by: ')

		#grab last 3 elements of posted (components of date) & format as date
		postedDateList = cleaned.split()[-3:]
		raw_date = ''
		for d in postedDateList:
			raw_date = raw_date + d + ' '
		raw_date = raw_date.rstrip(' ').replace(',', '')
		stamp = time.mktime(time.strptime(raw_date, "%B %d %Y"))
		date = datetime.fromtimestamp(stamp).strftime('%m-%d-%Y')
		
		#now pop the last 4 (date) elements out, you're left w/ the username 
		postedUserList = cleaned.split()[:-4]
		user = ''
		for u in postedUserList:
			user = user + u + ' '
		user = user.rstrip(' ')

		#last, grab the textstring of the comment 
		textstring = c.getText().replace(posted,'').replace('\n',' ').encode('ascii','ignore')

		#what type of comment is this? 
		system = 'legacy'
		thisComment = {
						'commenter': user,
						'comment_date':date,
						'comment_stamp': stamp,
						'comment_text': textstring,
						'comment_system': system,
						'comment_sentiment': getCommentSentiment(textstring),
						'comment_num': num,
						'entry_link':link, 
											}
		thisComment.update(basicMeta)
		cleanedComments.append(thisComment)
	return cleanedComments


def getDisqusComments(entrySoup, link):
	'''takes soup & link and returns a list of dicts for comments associated w/ that entry'''
	#get basicMeta for this Soup
	basicMeta = getBasicMeta(entrySoup, link)

	#create a place to put the comments 
	cleanedComments = [] 

	#give disqus API link, get back dict of 'posts' i.e. comments 
	disqusData = json.load(urllib2.urlopen(disqusContentBase + disqusKey + disqusMid + link))

	#inside that dict is a list; inside that list is a dict, so loop & get comments
	#comments are in reverse chronological order, so count down 
	num = len(disqusData['response'])
	for c in disqusData['response']: 
		#get the text of the comment 
		textstring = c['raw_message'].encode('ascii','ignore')

		#get the commenter's name 
		user = c['author']['name'].encode('ascii','ignore')

		#get & format date of the comment 
		raw_date = c['createdAt'].encode('ascii','ignore')[0:10]
		stamp = time.mktime(time.strptime(raw_date, '%Y-%m-%d'))
		date = datetime.fromtimestamp(stamp).strftime('%m-%d-%Y')

		#what type of comment is this? 
		system = 'disqus'
		thisComment = {
						'commenter': user,
						'comment_date':date,
						'comment_stamp': stamp,
						'comment_text': textstring,
						'comment_system': system,
						'comment_num': num, 
						'comment_sentiment': getCommentSentiment(textstring),
						'entry_link': link, 
											}
		thisComment.update(basicMeta)
		cleanedComments.append(thisComment)
		#decrement num 
		num = num - 1
	return cleanedComments

def getEntryComments(entrySoup, link):
	'''takes soup & link, returns dict of comments associated w/ entry)'''
	if getEntryCommentSystem(entrySoup) == 'legacy':
		comments = getLegacyComments(entrySoup, link)
	else:
		comments = getDisqusComments(entrySoup, link)
	return comments

#getting analytics from web & social media 
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
				'FB_TOTAL': fbt,
				}
	return fbData

def getTweetCount(link):
	'''takes a link and returns an int == count of times this link has been tweeted'''
	#ask twitter for a json dict of count of times a link has been tweeted 
	data = json.loads((urllib2.urlopen(countTweets + link).read()))
	count = data['count']
	return count 

#getting entity extraction data from CLIFF 
def getCLIFFData(entryText):
	'''takes the entryText and runs it against the Civic CLIFF server for analysis, returns a json dict. '''
	'''based on code by @natematias'''
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
						'entityCount': o['count'],
						'entityName': o['name'].encode('ascii','ignore'),
						'entityType': 'organization',
						'entry_link': link, 
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
						'entityCount': p['count'],
						'entityName': p['name'].encode('ascii','ignore'),
						'entry_link': link, 
						'entityType': 'person'
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
						'entry_link': link, 
					  }
			thisPlace.update(basicMeta)
			places.append(thisPlace)
	return places


