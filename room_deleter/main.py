import json
import boto3
from config import Config
from boto3.dynamodb.conditions import Key, Attr


def handler(event, context):
    print(event)
    client_id = event['clientId']
    
    #get the client's room
    dynamodb = boto3.resource('dynamodb', region_name=Config.AWS_REGION)
    table = dynamodb.Table(Config.ROOM_TABLE)
    response = table.scan(
        FilterExpression=Attr('host').eq(client_id)
    )
    data = response['Items']
    print(response)
    if len(data) == 1: #delete the room
        response = table.delete_item(
            Key={
                'roomName': data[0]['roomName']
            }
        )
        print('Closing room: ' + data[0]['roomName'])
        print(response)
    return {
        'statusCode': 200,
        'body': json.dumps('Ok')
    }