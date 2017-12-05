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