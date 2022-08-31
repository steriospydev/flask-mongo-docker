"""
Similarity Check

"""
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import spacy
from bson.json_util import dumps

from messages import *
app = Flask(__name__)
api = Api(app)

# Connect to db
client = MongoClient("mongodb://db:27017")
db = client.SimilarityDB
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


# Resources
class Allusers(Resource):
    def get(self):
        allusers = users.find({})
        retMap = []
        for user in allusers:
           retMap.append({'username':user['Username'], "tokens":user["Tokens"]})
        return jsonify(retMap)

class Register(Resource):
    def post(self):
        data = request.get_json()
        username = data['username']
        password = data['password']

        if user_exist(username):
            return jsonify(user_exist_info())
        else:
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            users.insert_one({
                "Username": username,
                "Password": hashed_pw,
                "Tokens" : 6
            })
            return jsonify(user_sign_info())

class Detect(Resource):
    def post(self):
        data = request.get_json()
        username = data['username']
        password = data['password']
        text1 = data['text1']
        text2 = data['text2']
        # Check if user exist
        if not user_exist(username):
            return jsonify(user_exist_info())

        # Check password validity
        correct_pw = verifyPW(username, password)
        if not correct_pw:
            return jsonify(incorrect_password_info())

        # Check if user did not run out of tokens
        num_of_tokens = getTokens(username)
        if num_of_tokens <= 0:
            return jsonify(out_of_tokens_info())

        # Calculate similarity
        nlp = spacy.load('en_core_web_sm')
        text1 = nlp(text1)
        text2 = nlp(text2)
        ratio = text1.similarity(text2) * 100



        current_tokens = getTokens(username)
        users.update_one({
            "Username":username
            },{
                "$set":{
                    'Tokens': current_tokens - 1
                }
            }
            )
        return jsonify(similarity_use_info(ratio))

class Refill(Resource):
    def post(self):
        data = request.get_json()
        username = data['username']
        password = data["admin_password"]
        refill_amount = data["refill"]

        # Check if user exist
        if not user_exist(username):
            return jsonify(user_exist_info())

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
api.add_resource(Detect, '/detect')
api.add_resource(Refill, '/refill')

api.add_resource(Allusers,'/all')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
