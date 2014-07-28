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
conn = sqlite3.connect('../DATADUMP/blogdb/blogData ' + now + '.db')
db = conn.cursor()

#open database connection
def initializeDatabase():
	#create table for entry metadata
	db.execute('''CREATE TABLE IF NOT EXISTS entry_metadata (entry_author text, entry_title text,
				 	 entry_date date, entry_stamp timestamp, entry_delta int, 
				 	 entry_link text unique, author_course text, 
				 	 blogger_type text, categories text, comment_system text,
				 	 comment_count int, tweet_count int, fbtotal_count int,
				 	 wordcount int)''')

	#create table for entry content
	db.execute('''CREATE TABLE IF NOT EXISTS entry_content (entry_author text, entry_title text,
				 	 entry_date date, entry_stamp timestamp, entry_delta int, 
				 	 entry_link text unique, entry_text text)''')

	#create table for comments
	db.execute('''CREATE TABLE IF NOT EXISTS entry_comments (entry_author text, entry_title text,
				 	 entry_date date, entry_stamp timestamp, entry_delta int, 
				 	 entry_link text unique, commenter text, comment_date text, comment_stamp timestamp,
				 	 comment_text text, comment_system text, comment_sentiment int,
				 	 comment_num int)''')

	#create table for entities mentioned
	db.execute('''CREATE TABLE IF NOT EXISTS entry_entities (entry_author text, entry_title text,
				 	 entry_date date, entry_stamp timestamp, entry_delta int, 
				 	 entry_link text unique, entityCount int, entityName text, 
				 	 entityType text)''')

	#create table for places mentioned
	db.execute('''CREATE TABLE IF NOT EXISTS entry_places (entry_author text, entry_title text,
				 	 entry_date date, entry_stamp timestamp, entry_delta int, 
				 	 entry_link text unique, placeName text, countryCode text, 
				 	 latitude int, longitude int, population int)''')

def insertMetaData(entryMeta):
	'''takes a dict & inserts it into the entry_metadata table'''
	sql = ""
	sql += 'INSERT OR IGNORE INTO entry_metadata ('
	sql += ', '.join(entryMeta.keys())
	sql += ')'
	sql += ' VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
	db.execute(sql, entryMeta.values())
	conn.commit()

def insertEntryContent(entryContent):
	'''takes a dict & inserts it into the entry_content table'''
	sql = ""
	sql += 'INSERT OR IGNORE INTO entry_content ('
	sql += ', '.join(entryContent.keys())
	sql += ')'
	sql += ' VALUES (?,?,?,?,?,?,?)'
	db.execute(sql, entryContent.values())
	conn.commit()

def insertComments(c):
	'''takes a dict & inserts it into the comments table'''
	sql = ""
	sql += 'INSERT OR IGNORE INTO entry_comments ('
	sql += ', '.join(c.keys())
	sql += ')'
	sql += ' VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)'
	db.execute(sql, c.values())
	conn.commit()

def insertEntities(e):
	'''takes a dict & inserts it into the entities table'''
	sql = ""
	sql += 'INSERT OR IGNORE INTO entry_entities ('
	sql += ', '.join(e.keys())
	sql += ')'
	sql += ' VALUES (?,?,?,?,?,?,?,?,?)'
	db.execute(sql, e.values())
	conn.commit()

def insertPlaces(p):
	'''takes a dict & inserts it into the places table'''
	sql = ""
	sql += 'INSERT OR IGNORE INTO entry_entities ('
	sql += ', '.join(p.keys())
	sql += ')'
	sql += ' VALUES (?,?,?,?,?,?,?,?,?,?,?)'
	db.execute(sql, p.values())
	conn.commit()

