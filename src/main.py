import awsgi
from flask import (
    Flask,
    jsonify
)
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)

@app.route('/')
@cross_origin()
def index():
    return jsonify(status=200, message='OK') 

def lambda_handler(event, context):
  return awsgi.response(app, event, context)