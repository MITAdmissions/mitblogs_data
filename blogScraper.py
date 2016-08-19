#####
#scrapes lots of stuff from the MITAdmissiongs blogs & writes them to a database for analysis
#written by @peteyreplies
#####

#import libraries
from scrapeBlogs import * 					#bespoke functions for scraping the blogs
from storeBlogs import *					#bespoke functions for storing the blogs
from googleData import * 					#hack to get Google Analytics data

#scrape last 20 bloglinks & save to file (4660 for production as of 8/4/14)
toScrape = getBlogLinks(300)

#or, load some recently scraped list of links to not start anew
#toScrape = '../DATADUMP/bloglinks/allLinks.txt'

#load all the bloggers & their types
bloggers = getAllBloggers()

#make a count for link & for becca
i = 1
becca = 0
totalTime = 0

#create database
initializeDatabase()

#load links into list 
x = open(toScrape)
links = []
links = x.read().splitlines()

#start looping like bruce willis
for link in links:

	#print the link & time for debugging 
	print str(i) + ': ' + link
	start = time.time()

	#make static calls and protect against becca, who breaks the scraper for some reason (sorry becca -___-)
	print 'loading static' 
	entryHTML = getEntryHTML(link)
	entrySoup = getEntrySoup(entryHTML)

	if 'Becca H.' in getEntryAuthor(entrySoup): 
		print 'BECCA BROKE'
		becca = becca + 1
		continue

	#entryLines = getEntryLines(entryHTML)
	#entryText = getEntryText(entryLines)
	basicMeta = getBasicMeta(entrySoup, link)
	#cliffData = getCLIFFData(entryText)
	
	#make a dict of entry metadata + stats, then load into database + csv
	print 'getting meta'
	entryMeta = {
					'author_course': getAuthorCourse(entrySoup),
					'blogger_type': getBloggerType(entrySoup, bloggers),
					'categories': getCategories(entrySoup),
					'comment_system': getEntryCommentSystem(entrySoup),
					'comment_count': getEntryCommentCount(entrySoup, link),
					#'tweet_count': getTweetCount(link),
					#'fbtotal_count': getEntryFBData(link)['FB_TOTAL'],
					'unique_pageviews': getGooglePageviews(getLinkPath(link), 0),
					#'wordcount': getEntryWords(entryText),
	}
	entryMeta.update(basicMeta)
	insertMetaData(entryMeta)
	writeCSV(entryMeta, 'entry_metadata')

# # 
# 	#make a dict of entry full-text content + meta & load into database 
# 	print 'getting content'
# 	#entryContent = {
# 					'entry_text': entryText,
# 	}
# 	entryContent.update(basicMeta)
# 	insertEntryContent(entryContent)
# 	writeCSV(entryContent, 'entry_content')
# #

	print 'getting comments'
	#get a list of dicts representing full text comments associated w/ entry & load into database 
	entryComments = getEntryComments(entrySoup, link)
	for c in entryComments:
		insertComments(c)
		writeCSV(c, 'entry_comments')
		writeTXT(c['comment_text'],'commentLines')

	# print 'getting entities'
	# #get a list of dicts representing entitites mentioned in the entry & load into database
	# try: 
	# 	orgs = getEntryOrgs(basicMeta, cliffData, link)
	# 	people = getEntryPeople(basicMeta, cliffData, link)
	# 	entitiesMentioned = orgs + people
	# 	for e in entitiesMentioned:
	# 		insertEntities(e)
	# 		writeCSV(e, 'entry_entities')
	# except KeyError:
	# 	print 'NO ENTITIES'


	# print 'getting places'
	# #get a list of dicts representing places mentioned in the entry & load into database 
	# try: 
	# 	placesMentioned = getEntryPlaces(basicMeta, cliffData, link)
	# 	for p in placesMentioned:
	# 		insertPlaces(p)
	# 		writeCSV(p, 'entry_places')
	# except KeyError:
	# 	print 'NO PLACES'

	#print 'writing lines'
	#gets the lines of the entry & writes them to a text file for feeding @mitblogs_ebooks
	#for thisLine in entryLines:
	#	writeTXT(thisLine, 'entryLines')

	i = i + 1
	elapsed = time.time() - start
	print 'took ' + str(elapsed) + ' seconds'
	totalTime = totalTime + elapsed
	#end loop

print 'total time = ' + str(totalTime) + ' seconds'
print 'becca count = ' + str(becca)
print 'done!'