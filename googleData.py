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

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

f = file('%s/%s' % (SITE_ROOT,'../RESOURCES/googlekey.p12'), 'rb')
key = f.read()
f.close()

email = (open('../RESOURCES/mygmail.txt')).read()
scope = 'https://www.googleapis.com/auth/analytics.readonly'
today = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d')

def getGooglePageviews(linkpath):
	'''takes a linkpath & returns count of unique pageviews from Google Analytics'''
	http = httplib2.Http()
	storage = Storage('../RESOURCES/analytics.dat')
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
	return count