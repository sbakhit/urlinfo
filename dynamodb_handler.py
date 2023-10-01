import boto3
from decouple import config

# configs are read from local .env file
AWS_ACCESS_KEY_ID     = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
REGION_NAME           = config("REGION_NAME")

resource = boto3.resource(
    'dynamodb',
    aws_access_key_id     = AWS_ACCESS_KEY_ID,
    aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
    region_name           = REGION_NAME
)
URLInfoTable = resource.Table('URLInfo')

def AddItemToURLInfo(url: str, is_safe: bool):
    response = URLInfoTable.put_item(
        Item = {
            'url': url,
            'is_safe': is_safe
        }
    )
    return response

def GetItemFromURLInfo(url: str):
    response = URLInfoTable.get_item(
        Key = {
            'url': url
        },
        AttributesToGet=[
            'url', 'is_safe'
        ]
    )
    return response

def UpdateURLSafeFlag(url: str, is_safe: bool):
    response = URLInfoTable.update_item(
        Key = {
            'url': url
        },
        AttributeUpdates = {
            'is_safe': {
                'Value'  : is_safe,
                'Action': 'PUT'
            }
        },
        ReturnValues = "UPDATED_NEW"
    )
    return response

def DeleteAnItemFromURLInfo(url: str):
    response = URLInfoTable.delete_item(
        Key = {
            'url': url
        }
    )
    return response

