# Feed data into a kinesis stream
from TwitterAPI import TwitterAPI
import boto3
import json
from twitterCreds import *
from keywords import *

api = TwitterAPI(consumer_key, consumer_secret, access_token_key, access_token_secret)

kinesis = boto3.client('kinesis')

# Keywords
terms = iphone

# Tweet Language
language = 'en'

# Request Twitter api and filter on keywords and language
request = api.request('statuses/filter', {'track':terms, 'language':language})

# Ingest into kinesis stream
while True:
	try:
		for item in request:
			if 'text' in item:
				kinesis.put_record(StreamName = "twitter", Data = json.dumps(item), PartitionKey = "filler")
	except:
		pass