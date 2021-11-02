import boto3
from boto3.dynamodb.conditions import Key

class AwsConnector:
    #생성자
    def __init__(self, option, app_name, systrace_key):
        self.option = option
        self.app_name = app_name
        self.systrace_key = systrace_key
        self.dynamodb = boto3.resource('dynamodb')

    # 업로드
    # 성공: True, 실패: False
    def insert_data(self, *value):
        if self.option == 'w':
            table = self.dynamodb.Table('systrace')
            response = table.get_item(
                Key={
                    'app_name': self.app_name,
                    'systrace_key': self.systrace_key
                }
            )
            try:
                response['Item']
                print("중복된 데이터가 있습니다.")
                return False
            except:
                #중복된 데이터가 없을 경우 저장함
                table.put_item(
                    Item={
                        'app_name': self.app_name,
                        'systrace_key': self.systrace_key,
                        'operating_ratio': str(value[0])
                    }
                )
                return True
    
    def get_all_item(self):
        table = self.dynamodb.Table('systrace')
        response = table.query(
            ProjectionExpression = 'operating_ratio',
            KeyConditionExpression = Key('app_name').eq(self.app_name)
        )
        print(response)
        return response['Items']