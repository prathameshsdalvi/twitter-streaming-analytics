# Create a kinesis stream
import boto3

client = boto3.client('kinesis')
response = client.create_stream(
   StreamName = 'twitter',
   ShardCount = 1
)