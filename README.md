mitblogs_fb_data
================

scrapes data on every mitadmissions blog post ever to see performance on facebook hidden to traditional analytics

* blogScraper.py scrapes the blogs for every link and writes it to blogLinks.txt
* blogData.py loads blogLinks.txt, runs each line through the link_stat table of the (deprecated) Facebook API, and writes it to fbData.csv