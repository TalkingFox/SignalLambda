import random
import boto3
import awsgi
import json

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


@app.route('/rooms/<roomname>/offers', methods=['POST'])
@cross_origin()
def join_room(roomname):
    player_info = request.get_json()
    player_name = player_info['name']
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
            ':player': [{
                'offer': player_info['offer'],
                'name': player_name
            }]
        }
    )
    return jsonify({'message': 'Ok'}), 204


@app.route('/rooms/<name>/offers', methods=['GET'])
@cross_origin()
def read_offers(name):
    dynamodb = boto3.resource('dynamodb', region_name=Config.AWS_REGION)
    table = dynamodb.Table(Config.ROOM_TABLE)
    response = table.get_item(
        Key={
            'roomName': name
        }
    )
    all_offers = response['Item']['offers']
    new_offers = list(filter(lambda x: 'answer' not in x, all_offers))
    return jsonify(new_offers)


@app.route('/rooms/<name>/offers/<player>', methods=['GET'])
@cross_origin()
def read_my_offer(name, player):
    dynamodb = boto3.resource('dynamodb', region_name=Config.AWS_REGION)
    table = dynamodb.Table(Config.ROOM_TABLE)
    response = table.get_item(
        Key={
            'roomName': name
        }
    )
    player_offer = next(offer for offer in response['Item']['offers'] if offer['name']==player)
    return jsonify(player_offer)


@app.route('/rooms/<roomname>/offers/<player>', methods=['PUT'])
@cross_origin()
def respond_to_offer(roomname, player):
    answer = request.get_json()['answer']
    dynamodb = boto3.resource('dynamodb', region_name=Config.AWS_REGION)
    table = dynamodb.Table(Config.ROOM_TABLE)
    document = table.get_item(
        Key={
            'roomName': roomname
        }
    )['Item']
    player_offer = next(offer for offer in document['offers'] if offer['name']==player)
    player_offer['answer'] = answer
    print(document)
    updateResponse = table.put_item(Item=document)
    return jsonify('ok'), 204


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
