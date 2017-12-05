# Process tweets and store in DynamoDB
import boto3
import time
import json
import sys
from textblob import TextBlob
import numpy as np
import time
from keywords import *

reload(sys)
sys.setdefaultencoding('utf8')

# Connent to the kinesis stream
kinesis = boto3.client("kinesis")
shard_id = 'shardId-000000000000'
shard_it = kinesis.get_shard_iterator(StreamName = "twitter", ShardId = shard_id, ShardIteratorType = "LATEST")["ShardIterator"]

# Define the DynamoDB table to store data
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('big_data_tweets')

# Function to extract and process kinesis stream
def write_processed_tweet(item):
	tweet = {}	
	data = json.loads(item['Data'])
	tweet['id'] = data.get('id')
	tweet['created_at'] = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(data.get('created_at'),'%a %b %d %H:%M:%S +0000 %Y'))
	if 'quoted_status' in data:
		text = str(data.get('text')) + ' "' + str(data.get('quoted_status').get('text')) + '"'
	else:
		text = data.get('text')
	tweet['text'] = text
	tweet['in_reply_to_status_id'] = data.get('in_reply_to_status_id')
	tweet['in_reply_to_screen_name'] = data.get('in_reply_to_screen_name')
	tweet['quote_count'] = data.get('quote_count')
	tweet['reply_count'] = data.get('reply_count')
	tweet['retweet_count'] = data.get('retweet_count')
	tweet['favorite_count'] = data.get('favorite_count')
	tweet['possibly_sensitive'] = data.get('possibly_sensitive')
	tweet['user.id'] = data.get('user').get('id')
	tweet['user.name'] = data.get('user').get('name')
	tweet['user.screen_name'] = data.get('user').get('screen_name')
	tweet['user.location'] = data.get('user').get('location')
	tweet['user.followers_count'] = data.get('user').get('followers_count')
	tweet['user.created_at'] = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(data.get('user').get('created_at'),'%a %b %d %H:%M:%S +0000 %Y'))
	tweet['user.id'] = data.get('user').get('id')
	htags = data.get('entities').get('hashtags')
	htag_list = []
	for ht in htags:
		htag = ht['text']
		htag_list.append(htag)
	tweet['entities.hashtags'] = htag_list
	if TextBlob(text).sentiment.polarity > 0:
		sentiment = 'Positive'
	elif TextBlob(text).sentiment.polarity < 0:
		sentiment = 'Negative'
	else:
		sentiment = 'Neutral'
	tweet['sentiment'] = sentiment
	
	features = []
	if np.any([keyword in text for keyword in np.array(screen.split(', '))]):	
		features.append('Screen')
	if np.any([keyword in text for keyword in np.array(battery.split(', '))]):	
		features.append('Battery')
	if np.any([keyword in text for keyword in np.array(camera.split(', '))]):	
		features.append('Camera')
	if np.any([keyword in text for keyword in np.array(size.split(', '))]):	
		features.append('Size')
	if np.any([keyword in text for keyword in np.array(weight.split(', '))]):	
		features.append('Weight')
	if np.any([keyword in text for keyword in np.array(microphone.split(', '))]):	
		features.append('Microphone')
	if np.any([keyword in text for keyword in np.array(dot_projector.split(', '))]):	
		features.append('Dot Projector')
	if np.any([keyword in text for keyword in np.array(sensors.split(', '))]):	
		features.append('Sensors')
	if np.any([keyword in text for keyword in np.array(flood_illuminator.split(', '))]):	
		features.append('Flood Illuminator')
	if np.any([keyword in text for keyword in np.array(speaker.split(', '))]):	
		features.append('Speaker')
	if np.any([keyword in text for keyword in np.array(faceid.split(', '))]):	
		features.append('Face ID')
	if np.any([keyword in text for keyword in np.array(apple_pay.split(', '))]):	
		features.append('Apple Pay')
	if np.any([keyword in text for keyword in np.array(price.split(', '))]):	
		features.append('Price')
	if np.any([keyword in text for keyword in np.array(color.split(', '))]):	
		features.append('Color')
	if np.any([keyword in text for keyword in np.array(capacity.split(', '))]):	
		features.append('Capacity')
	if np.any([keyword in text for keyword in np.array(siri.split(', '))]):	
		features.append('Siri')
	if np.any([keyword in text for keyword in np.array(gpu.split(', '))]):	
		features.append('GPU')
	if np.any([keyword in text for keyword in np.array(memory.split(', '))]):	
		features.append('Memory')
	if np.any([keyword in text for keyword in np.array(design.split(', '))]):	
		features.append('Design')
	if np.any([keyword in text for keyword in np.array(gestures.split(', '))]):	
		features.append('Gestures')
	if np.any([keyword in text for keyword in np.array(carrier.split(', '))]):	
		features.append('Carrier')
	if np.any([keyword in text for keyword in np.array(connectivity.split(', '))]):	
		features.append('Connectivity')
	if np.any([keyword in text for keyword in np.array(headphone.split(', '))]):	
		features.append('Earphones')
	if np.any([keyword in text for keyword in np.array(animoji.split(', '))]):	
		features.append('Animoji')
	if np.any([keyword in text for keyword in np.array(ios.split(', '))]):	
		features.append('iOS')

	tweet['features.name'] = features
	
	table.put_item(Item = tweet)


# Infinite loop that requests data from Kinesis stream
while True:
	request = kinesis.get_records(ShardIterator = shard_it, Limit = 50)
	batch = request['Records']
	for item in batch:
		try:
			write_processed_tweet(item)
		except:
			pass
	shard_it = request["NextShardIterator"]
	time.sleep(1.0)