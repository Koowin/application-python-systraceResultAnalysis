import boto3

def create_table():
    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.create_table(
        TableName='systrace',
        
        KeySchema=[
            {
                'AttributeName': 'app_name',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'systrace_key',
                'KeyType': 'RANGE'
            }
        ],

        AttributeDefinitions=[
            {
                'AttributeName': 'app_name',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'systrace_key',
                'AttributeType': 'N'
            },
        ],
        
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    return table

if __name__=='__main__':
    #table = create_table()
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('systrace')
    table.put_item(
        Item={
            'app_name': 'com.koowin.test',
            'systrace_key': 1235,
            'value': 'blabla'
        }
    )