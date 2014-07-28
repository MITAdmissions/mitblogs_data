#####
#storing data from the blogs 
#written by @peteyreplies
#####

#import data libraries 
import sqlite3								#for writing to database 
import csv									#for writing to csv
import time 								#to compute time
from datetime import datetime, timedelta	#to convert time 

#set time for db naming
now = datetime.fromtimestamp(time.time()).strftime('as of %b %d %Y at %H_%M')

#open database connection
def initializeDatabase():
	conn = sqlite3.connect('../DATADUMP/blogData ' + now + '.db')
	db = conn.cursor()

	#create table for entry metadata
	db.execute('''CREATE TABLE IF NOT EXISTS entry_metadata (entry_author text, entry_title text,
				 	 entry_date date, entry_stamp timestamp, entry_delta int, 
				 	 entry_link text unique, author_course text, 
				 	 blogger_type text, categories text, comment_system text,
				 	 comment_count int, tweet_count int, fbtotal_count int,
				 	 wordcount int)''')

	#create table for entry content
	db.execute('''CREATE TABLE entry_content (entry_author text, entry_title text,
				 	 entry_date date, entry_stamp timestamp, entry_delta int, 
				 	 entry_link text unique, entry_text text)''')

	#create table for comments
	db.execute('''CREATE TABLE entry_comments (entry_author text, entry_title text,
				 	 entry_date date, entry_stamp timestamp, entry_delta int, 
				 	 entry_link text unique, commenter text, comment_date text, comment_stamp timestamp,
				 	 comment_text text, comment_system text, comment_sentiment int,
				 	 comment_num text, )''')

	#create table for entities mentioned
	db.execute('''CREATE TABLE entities (entry_author text, entry_title text,
				 	 entry_date date, entry_stamp timestamp, entry_delta int, 
				 	 entry_link text unique, entityCount int, entityName text, 
				 	 entityType text)''')

	#create table for places mentioned
	db.execute('''CREATE TABLE places (entry_author text, entry_title text,
				 	 entry_date date, entry_stamp timestamp, entry_delta int, 
				 	 entry_link text unique, placeName text, countryCode text, 
				 	 latitude int, longitude int, population int)''')

def insertMetaData(entryMeta):
	'''takes a dict & inserts it into the entry_metadata table'''
	conn = sqlite3.connect('../DATADUMP/blogData ' + now + '.db')
	db = conn.cursor()
	keys = ', '.join(entryMeta.keys())
	db.execute('INSERT INTO metadata VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
          (keys))
	conn.commit()

def insertEntryContent(entryContent):
	'''takes a dict & inserts it into the entry_content table'''

def insertComments(entryComments):
	'''takes a dict & inserts it into the comments table'''

def insertEntities(entitiesMentioned):
	'''takes a dict & inserts it into the entities table'''

def insertPlaces(placesMentioned):
	'''takes a dict & inserts it into the places table'''

