"""
Image classification
"""
# built-in imports
import re
import os

# Flask and db imports
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import requests

# Messages to be displayed[301,302,303, etc...]
from messages import *
import classify

app = Flask(__name__)
api = Api(app)

# Connect to db
client = MongoClient("mongodb://db:27017")
db = client.ImageRecognition
users = db['Users']

# Helper Functions
def user_exist(username):
    if users.count_documents({'Username':username}) == 0:
        return False
    return True

def verifyPW(user,pwd):
    hashed_pwd =users.find({"Username":user})[0]["Password"]
    if bcrypt.hashpw(pwd.encode("utf-8"), hashed_pwd) == hashed_pwd:
        return True
    return False

def getTokens(user):
    return users.find({"Username":user})[0]['Tokens']

def verifyCredentials(username, password):
    if not user_exist(username):
        return user_not_exist_info(), True
    correct_pw = verifyPW(username,password)
    if not correct_pw:
        return incorrect_password_info(), True
    return None, False

# API endpoints
class Register(Resource):
    def post(self):
    	# Read data from request
        data = request.get_json()
        username = data['username']
        password = data['password']
	
	# Check if user exist and if not create one
        if user_exist(username):
            return jsonify(user_not_exist_info())
        else:
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
		
            users.insert_one({
                "Username": username,
                "Password": hashed_pw,
                "Tokens" : 5
            })
            return jsonify(user_create_success())

# Image classify 
class Classify(Resource):
    def post(self):
        data = request.get_json()
        username = data['username']
        password = data["password"]
        url = data["url"]

        retMap, error = verifyCredentials(username, password)        
        if error:
            return jsonify(retMap)
        
        # CHeck if the user has enough tokens.
        tokens = getTokens(username)
        if tokens <= 0:
            return jsonify(out_of_tokens_info())

	# retrieve image andd store it in a temporary file
        r = requests.get(url)

        with open("temp.jpg", "wb") as f:
            f.write(r.content)

	# refer to classify.py
        image_path = os.path.join(os.getcwd(), 'temp.jpg')
        image_pred = classify.get_image_predictions(image_path)
	
	# reduce tokens
        users.update_one({
            "Username":username
        },{
            "$set":{
                "Tokens": tokens - 1
            }
        })

        return jsonify(image_pred)

class Refill(Resource):
    def post(self):
        data = request.get_json()
        username = data['username']
        password = data["admin_password"]
        refill_amount = data["refill"]

        # Check if user exist
        if not user_exist(username):
            return jsonify(user_not_exist_info())

        # Check password validity
        # FOR EXAMPLES SAKE HARDCVODE ADMIN_pw
        correct_pw = '123456'
        if not password == correct_pw:
            return jsonify(incorrect_adminPW_info())

        # Check if user did not run out of tokens
        num_of_tokens = getTokens(username) + refill_amount

        users.update_one({
            "Username":username
            },{
                "$set":{
                    'Tokens': num_of_tokens
                }
            }
            )
        return jsonify(refill_success_info(username,num_of_tokens))

api.add_resource(Register,'/register')
api.add_resource(Classify,'/classify')
api.add_resource(Refill, '/refill')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
