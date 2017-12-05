# Understanding Product Perception with Twitter Streaming Analytics using AWS

AWS can be used to build a highly scalable architecture to perform near real-time analytics on streaming data.

Our project provides companies and businesses the ability to track what consumers are saying about their products and services, on Social Media. As a proof-of-concept, we took the new Apple iPhoneX as an example and worked with data from Twitter. We implemented our solution using AWS services, analyzed tweets, identified what features people liked and disliked, and tried to find key influencers, that could be targeted by companies, to increase their reach on social media. The analysis is presented on a dashboard made using Elasticsearch and Kibana.

These instructions help setup the architecture.


## Pre-requisites

We will be using twitter streaming data obtained using twitter's streaming API. Ensure that you have the following setup, before you proceed:

- AWS account with a key pair saved on your local machine at `~/.ssh/`
- Access to AWS `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
- Twitter `consumer_key`, `consumer_secret`, `access_token_key` and `access_token_secret`
- [EC2 ubuntu instance](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html) using AWS
- [Elasticsearch instance](http://docs.aws.amazon.com/elasticsearch-service/latest/developerguide/es-createupdatedomains.html) using AWS
- Google Chrome browser
- [ElasticSearch Head](https://chrome.google.com/webstore/detail/elasticsearch-head/ffmkiejjmecolpfloofpjologoblkegm?hl=en-US) chrome extension


## Setting up EC2 Instance

Follow the instructions provided in the `ec2_machine_setup.bash` file. The instructions help you:

- Connect to your EC2 instance
  + Go to your AWS EC2 dashboard and ensure that your EC2 instance is running (you may use the EC2 instance available as a part of the free tier)
  + Right click on the instance, click on `Connect` and note down the Public DNS which will be used to SSH to the EC2 instance
  + Open Bash
  + Follow the steps as per `ec2_machine_setup.bash` to connect to the machine
  
- Install Python 2.7 and the Python libraries
- Set your AWS region and store your AWS Keys as environment variables
- Create project directories
- Create file with your Twitter App credentials
- Create keywords file with variables that store keywords for various analyses (refer to sample file `keywords.py`)


## Creating AWS Kinesis Data Stream

The file `create_kinesis_stream.py` creates a kinesis stream with 1 shard. Read more about AWS Kinesis Data Streams [here](https://aws.amazon.com/kinesis/data-streams/).

We use the Python `boto3` library to do this. It will be used for creating most of the architecture.

```python
# Create a kinesis stream
import boto3

client = boto3.client('kinesis')
response = client.create_stream(
   StreamName = 'twitter',
   ShardCount = 1
)
```


## Feeding Twitter Stream to Kinesis

The file `twitter_to_kinesis.py` creates a producer which ingests the Twitter stream into the Kinesis stream that we created above.

```python
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
```


## Creating a Consumer to Test the Kinesis Stream

Create the `simple_consumer.py` file. This script creates a simple consumer that prints the data from the Kinesis stream.

```python
# Consume the data
import boto3
import time
import json

kinesis = boto3.client("kinesis")
shard_id = "shardId-000000000000"
shard_it = kinesis.get_shard_iterator(StreamName = "twitter", ShardId = shard_id, \
    ShardIteratorType = "LATEST")["ShardIterator"]

# Infinite loop to read data from Kinesis stream
while True:
  out = kinesis.get_records(ShardIterator = shard_it, Limit = 1)
  shard_it = out["NextShardIterator"]
  print out;
  time.sleep(1.0)
```

To test your stream, run the following on the your current Bash window.

```python
python ~/big_data_project/final_pipeline/twitter_to_kinesis.py
```

This starts feeding Twitter stream into the Kinesis Stream

Open another Bash window, SSH to the same EC2 machine and run your consumer.

```python
python ~/big_data_project/testing/simple_consumer.py
```

If everything works well, executing the above commands should start printing the output to your BASH window which has the consumer running. Your output should look similar to the sample output given in `kinesis_tweets.txt`.


## Creating DynamoDB Table

We now create a DynamoDB table which stores data from our stream (`create_dynamodb_table.py`). 

```python
# Create DynamoDB table
# Just id is required
# Schema need not be given since DynamoDB is built for unstructured data
import boto3
dynamodb = boto3.resource('dynamodb')
table = dynamodb.create_table(
  TableName='big_data_tweets',
  KeySchema=[
    { "AttributeName": "id", "KeyType": "HASH" }
  ],
  AttributeDefinitions=[
    { "AttributeName": "id", "AttributeType": "N" }
  ],
  # pricing determined by ProvisionedThroughput
  ProvisionedThroughput={
    'ReadCapacityUnits': 5,
    'WriteCapacityUnits': 5
  }
)
table.meta.client.get_waiter('table_exists').wait(TableName='big_data_tweets')
```


## Processing and Storing Stream in DynamoDB

Before we store our stream in the DynamoDB table, we process it to extract the fields from the raw tweet which are useful to us. We also add additional features to our processed tweet. Refer to `kinesis_to_dynamodb.py` for the code.

Execute this code:

```python
python ~/big_data_project/final_pipeline/kinesis_to_dynamodb.py
```

To check if data is being processed and stored in your DynamoDB table, go to your DynamoDB dashboard in AWS, click on `Tables`, then on `big_data_tweets`. Go to `Items` tab and you should see your data being indexed here.


## Setting Up DynamoDB Stream

Go back to the `Overview` tab on the DynamoDB dashboard and click on `Manage Stream`. Select `New Image` and click on `Enable` to enable the DynamoDB stream.

Note down your DynamoDB table ARN and the DynamoDB stream ARN.

Similarly, go to Elasticsearch Service and note down the ARN and Endpoint and Kibana URLs.


## Creating IAM Roles for Lambda

Go to `IAM` under `Services` and click on `Roles` and then `Create role`. Select `AWS service` role and `Lambda`, as service. Select `AWSLambdaBasicExecutionRole` as permission policy and click `Next`. Name your role, *dynamodb-to-es*.

Now we add policies to our role which will let the Lambda function access the DynamoDB table, its stream and the Elasticsearch Service.

Click `Add inline policy` and select `Custom Policy`. Create the following inline policies:

- Access DynamoDB table *Access-to-the-DynamoDB*
  
  ```
  {
      "Version": "2012-10-17",
      "Statement": [
          {
              "Action": [
                  "dynamodb:DescribeTable",
                  "dynamodb:Scan"
              ],
              "Effect": "Allow",
              "Resource": [
                  "arn:aws:dynamodb:us-east-1:your-dynamodb-table-arn:table/elements"
              ]
          }
      ]
  }
  ```
  
- Access DynamoDB stream *Access-to-the-DynamoDB-stream*
  
  ```
  {
      "Version": "2012-10-17",
      "Statement": [
          {
              "Action": [
                  "dynamodb:DescribeStream",
                  "dynamodb:GetRecords",
                  "dynamodb:GetShardIterator",
                  "dynamodb:ListStreams"
              ],
              "Effect": "Allow",
              "Resource": [
                  "arn:aws:dynamodb:us-east-1:your-dynamodb-stream-arn:table/elements/stream/
		  2017-09-14T14:16:12.788"
              ]
          }
      ]
  }
  ```
  
- Access Elasticsearch *Lambda-to-Amazon-ES*
  
  ```
    {
      "Version": "2012-10-17",
      "Statement": [
          {
              "Action": [
                  "es:ESHttpPost"
              ],
              "Effect": "Allow",
              "Resource": "arn:aws:es:us-east-1:your-es-arn:domain/elementsdomain/*"
          }
      ]
  }
  ```
  
  Note the `/*` after the ARN.
  
  
## Creating Lambda Function

- Go to `Lambda` under `Services` and click on `Create function` then `Author from scratch`. Name the function *dynamodb_to_es*, select runtime as `Python 2.7`, `Choose an existing role` as role, select the `dynamodb_to_es` IAM role as the existing role and create the function.

- Scroll down and paste the code in `lambda.py` in the function code window labeled `lambda_function`. Ensure to change the ES_ENDPOINT in the code to your Elasticsearch Endpoint. It should be of the form `search-your-es-endpoint-xxxxxxxxxxxxxxxxxxxxxxxxxx.us-east-1.es.amazonaws.com/` without the `https://`.

- Scroll down further and under Basic settings, set timeout to 5 minutes.

- Scroll back up and add DynamoDB as a trigger from the list of triggers given in the left panel. Scroll down and select `big_data_tweets` as the DynamoDB table, check `Enable trigger` and click on `Add`.

- Scroll back up and DynamoDB should be added on the left. The right panel lists the resources the function's role has access to. There should be three resources listed here, CloudWatch Logs, DynamoDB and Elasticsearch Service. Click on `Save` to deploy the Lambda function.


## Creating Elasticsearch Mapping

- A mapping in Elasticsearch is a schema that defines how the data is indexed for search and aggregation. Here we create custom analyzers which enable various text fields to be analyzed in multiple ways. Phone features and Hashtags have multi-fields, one each for aggregation and search. They support partial search and are not case sensitive. The tweet text also uses multi-fields, with aggregation supported for the complete tweet and a search which supports searching for words with the same root and is not case sensitive.

- To create the mapping, click on the ElasticSearch Head extension icon in Google Chrome. Paste the Elasticsearch endpoint in the empty box at the top and click `Connect`. After a few seconds, you should be connected to the instance.

- Go to the `Any Request` tab, expand `Query`, paste the Elasticsearch endpoint link in the top-most box, `big_data_tweets` in the box below it and select `PUT` from the drop-down menu. `PUT` is used to create an index named `big_data_tweets` in the mentioned Elasticsearch instance.

- In the big white box below, paste the mapping given in `es_mapping.json` and click `Request`. If you get an output as below on the right, your index is created:

  ```
  {
  "acknowledged": true,
  "shards_acknowledged": true
  }
  ```
 
- You can go back to `Overview` tab, click on `Refresh` on the upper right corner and you should see the index created.


## Deploying Codes

- Go back to your EC2 and finally deploy your codes to complete the setup using the following commands

  ```python
  python ~/big_data_project/final_pipeline/twitter_to_kinesis.py &
  python ~/big_data_project/final_pipeline/kinesis_to_dynamodb.py &
  ```

- Once the codes start running, go back to the DynamoDB table and check if the new items are getting indexed.

- Then go to the ElasticSearch Head extension window and refresh the overview tab. You should see the data getting indexed in your index.


## Creating Kibana Dashboard

Use your Kibana link to open the Kibana dashboard. You are all set to visualize your live analyzed twitter stream according to your need! Learn more about creating Kibana dashboards [here](https://www.elastic.co/guide/en/kibana/5.5/dashboard-getting-started.html).

## Scope and Applications

- **360 product overview**   
  Build a holistic understanding of your products, by integrating social media with internal data

- **Key Influencers**   
  Find people who are brand advocates and have a big following, to be potential brand ambassadors

- **Competitive Analytics**   
  Understand your competitors' strategy and engagement with user on social media

- **Policy making**   
  Gauge how the public reacts to important policy decisions
