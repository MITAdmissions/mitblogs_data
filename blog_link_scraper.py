##scrapes every blog link and writes to file for later use
##code by @peteyreplies

from bs4 import BeautifulSoup
import os
import csv
import string
import urllib
import urllib2

#define a base indexical URL & page variable to increment 
#should eventually make this a method with flags
baseURL = "http://mitadmissions.org/blogs/P"
p = 0 
headers = { 'User-Agent' : 'PeteyBlogBot' }

#load each indexical page and scrape entry links into list
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

#write links to resource text file for quicker retrieval 
#should eventually make this only add new links 
blogLinks = open('blogLinks.txt','w')
for n in links:
  blogLinks.write("%s\n" % n)
blogLinks.close()