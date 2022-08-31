"""
Registration of a user                          :   0 token
Each user gets 10 tokens                        : +10 token
Store a sentence on our database                :  -1 token
Retrieve his stored sentence from db        s    :  -1 token

"""
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt


app = Flask(__name__)
api = Api(app)

# Connect to db
client = MongoClient("mongodb://db:27017")
db = client.SentencesDatabase
users = db['Users']

def verifyPW(user,pwd):
    hashed_pwd =users.find({"Username":user})[0]["Password"]
    if bcrypt.hashpw(pwd.encode("utf-8"), hashed_pwd) == hashed_pwd:
        return True
    else:
        return False

def getTokens(user):
    return users.find({"Username":user})[0]['Tokens']


class Register(Resource):
    def post(self):
        # get user dataP
        data = request.get_json()
        
        username = data['username']
        password = data['password']

        if users.find_one({"Username":username}):
            retMap = {
            "status": 301,
            "message": "Username already exists"
            }
            return jsonify(retMap)
        else:
            # hash(password + salt)
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # store username and password
            users.insert_one({
                "Username": username,
                "Password": hashed_pw,
                "Sentence": "",
                "Tokens" : 10
            })

            # Return
            retMap = {
                "status": 200,
                "message": "You successfully registered"
            }
            return jsonify(retMap)

class Store(Resource):
    def post(self):
        # Get the posted data
        data = request.get_json()
        # Read data
        username = data['username']
        password = data['password']
        sentence = data['sentence']

        
        # authenticate
        correct_pw = verifyPW(username, password)
        if not correct_pw:
            retMap = {
                "status":302,
                "message": "Password did not match the account."
            }
            return jsonify(retMap)
        # verify enough tokens
        num_tokens = getTokens(username)
        if num_tokens <= 0:
            retMap = {
                "status":301,
                "message": "YOu are out of tokens."
            }
            return jsonify(retMap)

        users.update_one({
            "Username": username
            }, {
                "$set":{
                    "Sentence":sentence,
                    "Tokens":num_tokens -1
                    }
            })

        retMap = {
            "status":200,
            "message": "Sentence was stored succesfully.",
            "sentence": sentence,
            "Tokens": num_tokens
        }
        return jsonify(retMap)

class Get(Resource):
    def post(self):
        data = request.get_json()

        username = data["username"]
        password = data["password"]

        correct_pw = verifyPW(username, password)
        if not correct_pw:
            retMap = {
                "status":302,
                "message": "Password did not match the account."
            }
            return jsonify(retMap)
        num_tokens = getTokens(username)
        if num_tokens <= 0:
            retMap = {
                "status":301,
                "message":"Out of tokens."
            }
            return jsonify(retMap)

        users.update_one({
            "Username": username
            }, {
                "$set":{
                    "Tokens":num_tokens - 1
                    }
            })
        sentence = users.find({"Username": username})[0]["Sentence"]
        retMap = {
            'status':200,
            "sentence": sentence,
            "Tokens":num_tokens
        }
        return jsonify(retMap)


api.add_resource(Register,'/register')
api.add_resource(Store,'/store')
api.add_resource(Get,'/get')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)