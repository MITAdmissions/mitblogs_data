#####
#scrapes entry text from MITAdmissions.org blogs & writes to text file 
#code by @peteyreplies
#####

#import libraries
from scrapeBlogs import * 					#bespoke functions for scraping the blogs
from storeBlogs import *					#bespoke functions for storing the blogs
from googleData import * 					#hack to get Google Analytics data

#scrape all (as of 8/1/14) bloglinks & save to file
toScrape = getBlogLinks(4660)

#load links into list 
x = open(toScrape)
links = []
links = x.read().splitlines()
typeLines = 'entryText'

#start loopin like JGL
for link in links:

	#print the link for debugging 
	print link
	entryLines = getEntryLines(getEntryHTML(link))
	for thisLine in entryLines:
		writeTXT(thisLine, typeLines)


