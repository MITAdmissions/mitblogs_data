##scrapes every blog link and writes to file for later use
##code by @peteyreplies

from bs4 import BeautifulSoup
import os
import csv
import string
import urllib
import urllib2

#define a base URL & page variable to increment 
baseURL = "http://mitadmissions.org/blogs/P"
p = 0 
headers = { 'User-Agent' : 'PeteyBlogBot' }

#loop through & download last (p==80 for test, p<=4620 for production as of 6/11/2014) blog links into a single stupidly huge document  
links = []
baseURL = "http://mitadmissions.org/blogs/P"
p = 0
while p<= 4620:
	html = urllib2.urlopen(baseURL + str(p)).read()
	entrySoup = BeautifulSoup(html)
	linkSoup = entrySoup.find_all("h3")
	for link in linkSoup:
		thisLink = str(link.a['href'])
		links.append(thisLink)
	p = p + 20

##write links to text file for quicker retrieval 
blogLinks = open('blogLinks.txt','w')
for n in links:
  blogLinks.write("%s\n" % n)
blogLinks.close()