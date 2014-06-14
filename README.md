mitblogs_data
================

a collection of instruments which help gather data on / from / about the mitadmissions blogs. mostly written by @peteyreplies, who is figuring this out as he goes along. 

#scripts
* blog_link_scraper: scrapes links to individual entries based on index url 
* blog_FB_data: runs links against (deprecated) facebook API for link_stat social engagement information (w/ some entry metadata as well)
* scrape_entries: loads links and scrapes metadata + entry text into sqlite database

#resources & results
* allBlogLinks.txt is a list of all links to all blog entries ever written (as of whenever it was last updated)
* someBlogLinks.txt is a list of ~20 or so links (for a more manageable test corpus) 
* fb_data.csv is all the social engagement data collected by blog_FB_data

