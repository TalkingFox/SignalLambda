import random, boto3, awsgi, json

from datetime import datetime
from flask import (
    Flask,
    jsonify,
    request
)
from flask_cors import CORS, cross_origin
from config import Config
from boto3.dynamodb.conditions import Key


app = Flask(__name__)
cors = CORS(app)

@app.route('/')
@cross_origin()
def index():
    return jsonify(status=200, message='OK') 

@app.route('/rooms', methods=['POST'])
@cross_origin()
def create_room():
    host_info = request.get_json()
    dynamodb = boto3.resource('dynamodb', region_name=Config.AWS_REGION)
    table = dynamodb.Table(Config.ROOM_TABLE)
    room = get_open_room(table)
    response = table.put_item(
        Item={
            'RoomName': room,
            'Created': datetime.now().isoformat(),
            'Host': host_info,
            'Players': []
        }
    )    
    return jsonify(room)

@app.route('/rooms/<name>', methods=['DELETE'])
@cross_origin()
def delete_room(name):
    dynamodb = boto3.resource('dynamodb', region_name=Config.AWS_REGION)
    table = dynamodb.Table(Config.ROOM_TABLE)
    table.delete_item(
        Key={
            'RoomName': name
        }
    )
    return jsonify(success=True)
@app.route('/rooms/<name>', methods=['PUT'])
@cross_origin()
def join_room(name):
    player_info = request.get_json()
    dynamodb = boto3.resource('dynamodb', region_name=Config.AWS_REGION)
    table = dynamodb.Table(Config.ROOM_TABLE)
    updateResponse = table.update_item(
        Key={
            'RoomName': name
        },
        UpdateExpression="SET Players = list_append(Players, :p)",
        ExpressionAttributeValues={
            ':p': [player_info]
        }
    )

    response = table.get_item(
        Key={
            'RoomName': name
        }
    )
    room = response['Item']
    return jsonify(room['Host'])
    

def lambda_handler(event, context):
  return awsgi.response(app, event, context)

def get_words():
    with open('words.txt') as f:
        content = f.readlines()
        content = [x.strip() for x in content]
        return content

def get_closed_rooms(table):
    response = table.scan(
        ProjectionExpression = "RoomName"
    )
    data = response['Items']    
    while 'LastEvaluatedKey' in response:
        response = table.scan(
            ExclusiveStartKey=response['LastEvaluatedKey'],
            ProjectionExpression="RoomName"
        )
        data.extend(response['Items'])
    return list(map(lambda x:x['RoomName'], data))

def get_open_room(table):
    words = get_words()    
    closed_rooms = get_closed_rooms(table)
    available = list(set(words) - set(closed_rooms))
    return random.choice(available)

if __name__ == "__main__":
    app.run()