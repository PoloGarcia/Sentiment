import json
import math
from pprint import pprint
import string
import oauth2 as oauth
import urllib2 as urllib
from nltk.corpus import stopwords
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
	url = 'https://api.twitter.com/1.1/search/tweets.json?q='+query+'&lang=en&count=15&result_type=popular'
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
		result = re.sub(r"(?:\@|https?\://)\S+", "", my_str)
		texto = filter(lambda x: x in string.printable, result)
		jsonFile.write(str(key['user']['id']) +'|'+ texto + '\n')
	jsonFile.close()

def parseDataSet(file,separatror):
	file = open(file,'r')
	allLines = file.readlines()[1:]
	subset_size = int(math.ceil(len(allLines) * 0.8))
	lines = allLines[:subset_size]
	sentimentDic = {}
	cachedStopWords = stopwords.words("english")
	for idx, word in enumerate(cachedStopWords):
		cachedStopWords[idx] = word.encode('ascii', 'ignore')
	exclude = set(string.punctuation)
	for line in lines:
		data = line.rstrip().split(separatror)
		sentimentDic[data[1]]={}
		sentimentDic[data[1]]['sentiment']= data[0].replace('"', '').strip()
		text = str(data[5])
		text = re.sub(r"(?:\@|https?\://)\S+", "", text)
		text = ''.join(ch for ch in text if ch not in exclude).lower()
		text = ' '.join([word for word in text.split() if word not in cachedStopWords])
		sentimentDic[data[1]]['text']= text.split()
	file.close()

	return sentimentDic, subset_size

def extract_features(tweet):
		cachedStopWords = stopwords.words("english")
		exclude = set(string.punctuation)
		for idx, word in enumerate(cachedStopWords):
			cachedStopWords[idx] = word.encode('ascii', 'ignore')
		text = tweet
		text = ''.join(ch for ch in text if ch not in exclude).lower()
		text = ' '.join([word for word in text.split() if word not in cachedStopWords])
		feature_vector = text.split()

		return feature_vector

def feature_probability(feature, sentiment):
	times = 1
	words = 1
	v = 0
	for key in sentimentDic.keys():
		v += len(sentimentDic[key]['text'])
		if sentimentDic[key]['sentiment'] == sentiment:
			words += len(sentimentDic[key]['text'])
			if feature in sentimentDic[key]['text']:
				times += 1

	print v
	return float(times) / float(v + words)


def classify_tweet(feature_vector):
	# P(positive|tweet) = P(tweet|positive)*P(positive)
	# P(tweet|positive) = P(T1|positive)*P(T2|positive)*...*(Tn|positive)

	p_tweet_positive = 0
	for feature in feature_vector:
		prob_f = feature_probability(feature, "4")
		p_tweet_positive += prob_f

	p_tweet_negative = 0
	for feature in feature_vector:
		prob_f = feature_probability(feature, "0")
		p_tweet_negative += prob_f

	p_tweet_neutral = 0
	for feature in feature_vector:
		prob_f = feature_probability(feature, "2")
		p_tweet_neutral += prob_f

	p_positive = 0.33 + p_tweet_positive
	p_negative = 0.33 + p_tweet_negative
	p_neutral = 0.33 + p_tweet_neutral

	array = [p_positive,p_negative,p_neutral]
	#print array
	index = array.index(max(array))

	if index == 0:
		return "4"
	elif index == 1:
		return "0"
	else:
		return "2"

def test(filename, separator, subset_size):
	successes = 0
	failures = 0
	file = open(filename, 'r')
	lines = file.readlines()[:subset_size + 1]
	cachedStopWords = stopwords.words("english")
	exclude = set(string.punctuation)

	for idx, word in enumerate(cachedStopWords):
		cachedStopWords[idx] = word.encode('ascii', 'ignore')

	for line in lines:
		data = line.rstrip().split(separator)
		features = extract_features(str(data[5]))
		print features
		label = classify_tweet(features)
		print label
		sentiment = data[0].replace('"', '').strip()
		if sentiment == label:
			print "success"
			successes += 1
		else:
			print "fail...cometiste un fail"
			failures += 1

	return float(successes) / float(successes + failures)

#Main()
parseTweets('Donald%20Trump','1.txt','1.data')
#parseTweets('Hunger%20Games','2.txt','2.data')
sentimentDic, subset_size = parseDataSet('testdata.manual.2009.06.14.csv',',')

tweet = "my car is shit"
tweets = open('2.data','r')
lines = tweets.readlines()

test('testdata.manual.2009.06.14.csv',',',subset_size)
"""
for tweet in lines:
	data = tweet.rstrip().split('|')
	print data[1]
	features = extract_features(str(data[1]))
	label = classify_tweet(features)

	if label == "4":
		print 'positive'
	elif label == "2":
		print 'neutral'
	else: 
		print 'negative'
"""