import boto3
from boto3.dynamodb.conditions import Key

# Upload to AWS
def upload_value(type, app_name, id, value):
    type_string = ("disk", "sched", "database")
    dynamodb = boto3.resource('dynamodb')
    
    try:
        table = dynamodb.Table(type_string[type])
    except:
        print("Error: Wrong type")
        return
    response = table.get_item(
        Key={
            'app_name': app_name,
            'systrace_id': id
        }
    )
    try:
        response['Item']
        print("Error: Duplicate systrace file.")
        return
    except:
        table.put_item(
            Item={
                'app_name': app_name,
                'systrace_id': id,
                'value': str(value)
            }
        )

# Download from AWS
def download_all(app_name):
    dynamodb = boto3.resource('dynamodb')
    table_disk = dynamodb.Table('disk')
    table_sched = dynamodb.Table('sched')
    table_database = dynamodb.Table('database')

    response_disk = table_disk.query(
        KeyConditionExpression = Key('app_name').eq(app_name)
    )
    response_sched = table_sched.query(
        KeyConditionExpression = Key('app_name').eq(app_name)
    )
    response_database = table_database.query(
        KeyConditionExpression = Key('app_name').eq(app_name)
    )

    result_disk = response_disk['Items']
    result_sched = response_sched['Items']
    result_database = response_database['Items']

    count_disk = len(result_disk)
    count_sched = len(result_sched)
    count_database = len(result_database)

    sum_disk = 0
    sum_sched = 0
    sum_database = 0

    for item in result_disk:
        sum_disk += float(item['value'])

    for item in result_sched:
        sum_sched += float(item['value'])

    for item in result_database:
        sum_database += float(item['value'])
    
    result = []
    result.append([sum_disk, count_disk])
    result.append([sum_sched, count_sched])
    result.append([sum_database, count_database])
    return result