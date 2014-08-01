mitblogs_data
================

a collection of instruments which help gather data on / from / about the mitadmissions blogs. mostly written by @peteyreplies, who is figuring this out as he goes along. 

##how it works
* scrapeBlogs contains a number of custom functions for scraping content from the blogs
* storeBlogs contains a number of custom functions for storing that content into SQLite / CSV
* googleData contains a separate function for querying google analytics for unique pageviews (which is really more complex than it has any right to be, get it to together Google)
* blogScraper snaps all of the above together to actually do the work of scraping & storing the blogs in a big loop 

