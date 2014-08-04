#####
#code to get unique pageviews from google analytics
#based on http://goo.gl/nOluHu, modified by @peteyreplies
#####


from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import SignedJwtAssertionCredentials
import httplib2
import os.path
from datetime import datetime, timedelta, date 	#to convert time  
import time 									#to compute time
from time import sleep 							#in case we hit a API problem 

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

f = file('%s/%s' % (SITE_ROOT,'../RESOURCES/google_key.p12'), 'rb')
key = f.read()
f.close()

email = (open('../RESOURCES/mygmail.txt')).read()
scope = 'https://www.googleapis.com/auth/analytics.readonly'
today = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d')
storage = Storage('../RESOURCES/analytics.dat')

def getGooglePageviews(linkpath, attempt):
	'''takes a linkpath & attempt count, returns count of unique pageviews from Google Analytics'''
	if attempt <= 1:
		try:
			http = httplib2.Http()
			credentials = storage.get()
			if credentials is None or credentials.invalid:
			    credentials = SignedJwtAssertionCredentials(email, key, scope)
			    storage.put(credentials)
			else:
			    credentials.refresh(http)
			http = credentials.authorize(http)
			service = build(serviceName='analytics', version='v3', http=http)
			data_query = service.data().ga().get(
			    ids = 'ga:22035378',
			    start_date = '2009-08-10',
			    end_date = today,
			    metrics = 'ga:uniquePageviews',
			    filters = 'ga:pagePathLevel3==/' + linkpath).execute()
			query = data_query.get('totalsForAllResults')
			count = int(query['ga:uniquePageviews'])
		except apiclient.errors.HttpError:
			#try once again after 20 seconds 
			attempt = attempt + 1
			sleep (20)
			return getGooglePageviews(linkpath, attempt)
	else:
		#503 error will be standardized at -1 pageviews 
		count = -1
	return count