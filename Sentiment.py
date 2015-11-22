import json
from pprint import pprint
import string
import oauth2 as oauth
import urllib2 as urllib
import re

api_key = "zKmzrkwmZsnp4UxN6wafDomUr"
api_secret = "VTHof2Q2BgPAHodIY1zeoEKG8eKvt3LRmB8rFdZwH9Vtqjiw9t"
access_token_key = "484501495-CqCJy1Ah9cqDkr5ewYjJKt82mR4wi8Iauru3dLRW"
access_token_secret = "alS2kkV7tRTheBPnNLTkhVvJAEKcL2VGsDjfO7UFGTKF8"

_debug = 0

oauth_token    = oauth.Token(key=access_token_key, secret=access_token_secret)
oauth_consumer = oauth.Consumer(key=api_key, secret=api_secret)

signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()

http_method = "GET"


http_handler  = urllib.HTTPHandler(debuglevel=_debug)
https_handler = urllib.HTTPSHandler(debuglevel=_debug)

'''
Construct, sign, and open a twitter request
using the hard-coded credentials above.
'''
def twitterreq(url, method, parameters):
	req = oauth.Request.from_consumer_and_token(oauth_consumer,
                                             	token=oauth_token,
                                             	http_method=http_method,
                                             	http_url=url, 
                                             	parameters=parameters)

	req.sign_request(signature_method_hmac_sha1, oauth_consumer, oauth_token)

	headers = req.to_header()

	if http_method == "POST":
		encoded_post_data = req.to_postdata()
	else:
		encoded_post_data = None
		url = req.to_url()

	opener = urllib.OpenerDirector()
	opener.add_handler(http_handler)
	opener.add_handler(https_handler)

	response = opener.open(url, encoded_post_data)

	return response

def fetchsamples(query,filename):
	url = 'https://api.twitter.com/1.1/search/tweets.json?q='+query+'&lang=en&count=100&result_type=mixed'
	parameters = []
	response = twitterreq(url, "GET", parameters)
	f = open(filename,'w+')
	for line in response:
		f.write(line.strip())
	f.close()

def parseTweets(query,outputFile,parsedFile):
	fetchsamples(query,outputFile)

	with open(outputFile) as data_file:    
	    data = json.load(data_file)

	jsonFile = open(parsedFile,'w+')
	for key in data['statuses']:
		my_str = key['text'].replace('\n', ' ').replace('\r', '')
		result = re.sub(r"http\S+", "", my_str)
		texto = filter(lambda x: x in string.printable, result)
		jsonFile.write(str(key['user']['id']) +'|'+ texto + '\n')
	jsonFile.close()

#Main()
parseTweets('Bernie%20Sanders','bernard.txt','jsonBernie.data')
parseTweets('Hillary%20Clinton','hillary.txt','jsonHillary.data')