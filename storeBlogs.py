#####
#storing data from the blogs 
#written by @peteyreplies
#####

#import data libraries 
import sqlite3								#for writing to database 
import csv									#for writing to csv
import time 								#to compute time
from datetime import datetime, timedelta	#to convert time 

#set time for this run 
now = datetime.fromtimestamp(time.time()).strftime('as of %b %d %Y at %H_%M')

#set db info for this run
conn = sqlite3.connect('../DATADUMP/blogdb/blogData ' + now + '.db')
db = conn.cursor()

#set names of csvs for this run
csvs = {
		'entry_metadata': '../DATADUMP/blogdb/entry_metadata ' + now + '.csv',
		'entry_content':  '../DATADUMP/blogdb/entry_content ' + now + '.csv',
		'entry_comments': '../DATADUMP/blogdb/entry_comments ' + now + '.csv',
		'entry_entities': '../DATADUMP/blogdb/entry_entities ' + now + '.csv',
		'entry_places':   '../DATADUMP/blogdb/entry_places ' + now + '.csv',
}

#open database connection
def initializeDatabase():
	#create table for entry metadata
	db.execute('''CREATE TABLE IF NOT EXISTS entry_metadata (entry_author text, entry_title text,
				 	 entry_date text, entry_stamp timestamp, entry_delta int, 
				 	 entry_link text, author_course text, 
				 	 blogger_type text, categories text, comment_system text,
				 	 comment_count int, unique_pageviews int, tweet_count int, 
				 	 fbtotal_count int, wordcount int)''')

	#create table for entry content
	db.execute('''CREATE TABLE IF NOT EXISTS entry_content (entry_author text, entry_title text,
				 	 entry_date text, entry_stamp timestamp, entry_delta int, 
				 	 entry_link text, entry_text text)''')

	#create table for comments
	db.execute('''CREATE TABLE IF NOT EXISTS entry_comments (entry_author text, entry_title text,
				 	 entry_date text, entry_stamp timestamp, entry_delta int, 
				 	 entry_link text, commenter text, comment_date text, comment_stamp timestamp,
				 	 comment_text text, comment_system text, comment_sentiment int,
				 	 comment_num int)''')

	#create table for entities mentioned
	db.execute('''CREATE TABLE IF NOT EXISTS entry_entities (entry_author text, entry_title text,
				 	 entry_date text, entry_stamp timestamp, entry_delta int, 
				 	 entry_link text, entityCount int, entityName text, 
				 	 entityType text)''')

	#create table for places mentioned
	db.execute('''CREATE TABLE IF NOT EXISTS entry_places (entry_author text, entry_title text,
				 	 entry_date text, entry_stamp timestamp, entry_delta int, 
				 	 entry_link text, placeName text, countryCode text, 
				 	 latitude int, longitude int, population int)''')

#insert info into database 
def insertMetaData(entryMeta):
	'''takes a dict & inserts it into the entry_metadata table'''
	sql = ""
	sql += 'INSERT OR IGNORE INTO entry_metadata ('
	sql += ', '.join(entryMeta.keys())
	sql += ')'
	sql += ' VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
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
	sql += 'INSERT OR IGNORE INTO entry_places ('
	sql += ', '.join(p.keys())
	sql += ')'
	sql += ' VALUES (?,?,?,?,?,?,?,?,?,?,?)'
	db.execute(sql, p.values())
	conn.commit()

#for writing data into csvs
def writeCSV(info, csvName):
	'''takes a dict of info & a string csv name, which is found & written to'''
	#open the file 
	f = open(csvs[csvName],'a')
	DW = csv.DictWriter(f,info.keys())
	
	#if this is the first time the file has been opened, write the keys + values
	if f.tell() == 0:
		DW.writer.writerow(info.keys())
		DW.writer.writerow(info.values())
	#else, just write the values 
	else:
		DW.writer.writerow(info.values())

#for writing data to textfile
def writeTXT(thisLine, typeLines):
	'''takes a string & a type and writes it to a text file'''
	#open the file
	f = open('../DATADUMP/blogtxt/' + typeLines + ' as of ' + now + '.txt')
	f.write("%s\n" % thisLine)
	f.close()