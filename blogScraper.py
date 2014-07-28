#####
#scrapes lots of stuff from the MITAdmissiongs blogs & writes them to a database for analysis
#written by @peteyreplies
#####

#import libraries
from scrapeBlogs import * 					#bespoke functions for scraping the blogs
from storeBlogs import *					#bespoke functions for storing the blogs

#scrape last 100 bloglinks & save to file
toScrape = getBlogLinks(20)

#load all the bloggers & their types
bloggers = getAllBloggers()

#make a count for becca
becca = 0

#set database
initializeDatabase()

#load links into list 
x = open(toScrape)
links = []
links = x.read().splitlines()

debug = [] 
#start looping like bruce willis
for link in links:

	#print the link for debugging 
	print link

	#make static calls and protect against becca 
	entrySoup = getEntrySoup(link)
	entryText = getEntryText(link)
	basicMeta = getBasicMeta(entrySoup, link)
	cliffData = getCLIFFData(entryText)

	#if 'Becca H.' in getEntryAuthor(entrySoup): becca = becca + 1; continue
	
	##start loading into dicts using functions from scrapeBlogs
	
	#make a dict of entry metadata & stats 
	print 'getting meta'
	entryMeta = {
					'author_course': getAuthorCourse(entrySoup),
					'blogger_type': getBloggerType(entrySoup, bloggers),
					'categories': getCategories(entrySoup),
					'comment_system': getEntryCommentSystem(entrySoup),
					'comment_count': getEntryCommentCount(entrySoup, link),
					'tweet_count': getTweetCount(link),
					'fbtotal_count': getEntryFBData(link)['FB_TOTAL'],
					'wordcount': getEntryWords(entryText),
	}
	entryMeta.update(basicMeta)
	insertMetaData(entryMeta)

	#make a dict of entry full-text content & meta 
	print 'getting content'
	entryContent = {
					'entry_text': entryText,
	}
	entryContent.update(basicMeta)

	print 'getting comments'
	#get a list of dicts representing full text comments associated w/ entry 
	entryComments = getEntryComments(entrySoup, link)

	print 'getting entities'
	#get a list of dicts representing entitites mentioned in the entry 
	entitiesMentioned = getEntryOrgs(basicMeta, cliffData, link)
	entitiesMentioned.append(getEntryPeople(basicMeta, cliffData, link))

	print 'getting places'
	#get a list of dicts representing places mentioned in the entry
	placesMentioned = getEntryPlaces(basicMeta, cliffData, link)


