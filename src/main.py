import random
import boto3
import awsgi
import json
import uuid

from datetime import datetime
from flask import (
    Flask,
    jsonify,
    request,
    Response
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
    dynamodb = boto3.resource('dynamodb', region_name=Config.AWS_REGION)
    table = dynamodb.Table(Config.ROOM_TABLE)
    room = get_open_room(table)
    response = table.put_item(
        Item={
            'roomName': room,
            'created': datetime.now().isoformat(),
            'offers': []
        }
    )
    iot = boto3.client('iot-data')
    response = iot.publish(
        topic='rooms/' + room,
        qos=1,
        payload='roomCreated'
    )
    print(jsonify(response))
    return jsonify(room)


@app.route('/rooms/<name>', methods=['DELETE'])
@cross_origin()
def delete_room(name):
    dynamodb = boto3.resource('dynamodb', region_name=Config.AWS_REGION)
    table = dynamodb.Table(Config.ROOM_TABLE)
    table.delete_item(
        Key={
            'roomName': name
        }
    )
    return jsonify(success=True)


@app.route('/rooms/<name>', methods=['GET'])
@cross_origin()
def get_room(name):
    dynamodb = boto3.resource('dynamodb', region_name=Config.AWS_REGION)
    table = dynamodb.Table(Config.ROOM_TABLE)
    room = table.get_item(
        Key={
            'roomName': name
        }
    )
    if 'Item' in room:
        return jsonify(success=True)
    else:
        return jsonify(message='Room not found!'), 404


@app.route('/rooms/<roomname>/join', methods=['POST'])
@cross_origin()
def join_room(roomname):
    player_info = request.get_json()
    player_name = player_info['player']
    dynamodb = boto3.resource('dynamodb', region_name=Config.AWS_REGION)
    table = dynamodb.Table(Config.ROOM_TABLE)
    if is_name_taken(table, roomname, player_name):
        return jsonify({'message': 'Username is taken.'}), 400
    updateResponse = table.update_item(
        Key={
            'roomName': roomname
        },
        UpdateExpression="SET offers = list_append(offers, :player)",
        ExpressionAttributeValues={
            ':player':  [player_name]
        }
    )
    player_id = str(uuid.uuid4())
    iot = boto3.client('iot-data')
    response = iot.publish(
        topic='rooms/' + roomname + '/' + player_id,
        qos=1,
        payload=json.dumps(
            {
                'name': player_name,
                'offer': player_info['offer'],
                'type': 'offer',
                'room': roomname
            })
    )
    return jsonify({'roomTopic': 'rooms/'+roomname+'/'+player_id})


@app.route('/rooms/<roomname>/accept', methods=['POST'])
@cross_origin()
def allow_guest(roomname):
    request_body = request.get_json()
    iot = boto3.client('iot-data')
    response = iot.publish(
        topic='rooms/' + roomname + '/' + request_body['playerId'],
        qos=1,
        payload=json.dumps(
            {'answer': request_body['answer'], 'type': 'answer'})
    )
    return jsonify({'success': True}), 204


def lambda_handler(event, context):
    return awsgi.response(app, event, context)


def get_words():
    with open('words.txt') as f:
        content = f.readlines()
        content = [x.strip() for x in content]
        return content


def get_closed_rooms(table):
    response = table.scan(
        ProjectionExpression="roomName"
    )
    data = response['Items']
    while 'LastEvaluatedKey' in response:
        response = table.scan(
            ExclusiveStartKey=response['LastEvaluatedKey'],
            ProjectionExpression="roomName"
        )
        data.extend(response['Items'])
    return list(map(lambda x: x['roomName'], data))


def get_open_room(table):
    words = get_words()
    closed_rooms = get_closed_rooms(table)
    available = list(set(words) - set(closed_rooms))
    return random.choice(available)


def is_name_taken(table, room_name, player_name):
    response = table.get_item(
        Key={
            'roomName': room_name
        }
    )
    return player_name in response['Item']['offers']


if __name__ == "__main__":
    app.run()
