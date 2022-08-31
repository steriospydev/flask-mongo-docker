from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
from . import messages

app = Flask(__name__)
api = Api(app)

# Connect to db
client = MongoClient("mongodb://db:27017")
db = client.BankAPI
users = db['Users']

def user_exist(username):
    if users.count_documents({'Username':username}) == 0:
        return False
    return True

def verifyPW(user,pwd):
    if not user_exist(user):
        return False
    hashed_pwd =users.find({"Username":user})[0]["Password"]
    password_match = bcrypt.hashpw(pwd.encode("utf-8"), hashed_pwd) == hashed_pwd
    if password_match:
        return True
    return False

def verifyCredentials(user, pwd):
    if not user_exist(user):
        return messages.user_not_exist_info(), True
    correct_pw = verifyPW(user,pwd)
    if not correct_pw:
        return messages.incorrect_password_info(), True
    return None, False

def updateAccount(user, balance):
    users.update({
        "Usename": user
    },{
        "$set":{
            "Own":balance
        }
    })

def updateDebt(user, balance):
    users.update({
        "Usename": user
    },{
        "$set":{
            "Debt":balance
        }
    })

def cashWithUser(user):
    return users.find({"Username":user})[0]['Own']

def debtWithUser(user):
    return users.find({"Usename":user})[0]["Debt"]

class Register(Resource):
    def post(self):
        data = request.get_json()
        username = data['username']
        password = data['password']

        if user_exist(username):
            return jsonify(messages.user_not_exist_info())
        else:
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            users.insert_one({
                "Username": username,
                "Password": hashed_pw,
                "Own" : 0,
                "Debt": 0
            })
            return jsonify(messages.user_create_success())

class Add(Resource):
    def post(self):
        data = request.get_json()
        username = data['username']
        password = data['password']
        money = data["amount"]

        retJson, error = verifyCredentials(username, password)
        if error:
            return jsonify(retJson)
        
        if money <= 0 :
            return jsonify(messages.negative_amount())
        
        cash = cashWithUser(username)
        money = money + cash - 1       #Bank fee
        bank_cash = cashWithUser("BANK") + 1

        updateAccount("BANK", bank_cash)

        updateAccount(username, money)

        return jsonify(messages.success_deposit())

class Transfer(Resource):
    def post(self):
        data = request.get_json()
        username = data['username']
        password = data['password']
        to = data['to']
        money = data["amount"]

        retJson, error = verifyCredentials(username, password)

        if error:
            return jsonify(retJson)
        
        if not user_exist(to):
            return jsonify(messages.user_not_exist_info())

        cash = cashWithUser(username)

        if money <= 0 :
            return jsonify(messages.negative_amount())
        
        cash_from = cashWithUser(username)
        cash_to = cashWithUser(to)      #Bank fee
        bank_cash = cashWithUser("BANK") + 1
        if cash_from < money:
            return jsonify(messages.low_funds())
        
        updateAccount("BANK", bank_cash)
        updateAccount(to, cash_to + money - 1 )
        updateAccount(username, cash_from-money)

        return jsonify(messages.success_transaction(money))

class Balance(Resource):
    def post(self):
        data = request.get_json()
        username = data['username']
        password = data['password']

        retJson, error = verifyCredentials(username, password)
        if error:
            return jsonify(retJson)
        
        retJson = users.find({
            "Username":username
        },{
            "Password":0,
            "_id":0
        })[0]

        return jsonify(retJson)

class TakeLoan(Resource):
    def post(self):
        data = request.get_json()
        username = data['username']
        password = data['password']
        money = data["amount"]

        retJson, error = verifyCredentials(username, password)
        if error:
            return jsonify(retJson)
        
        if money <= 0 :
            return jsonify(messages.negative_amount())
        
        cash = cashWithUser(username)
        debt = debtWithUser(username)
        updateAccount(username, cash + money)
        updateDebt(username, debt + money)

        return jsonify(messages.success_loan())

class PayLoan(Resource):
    def post(self):
        data = request.get_json()
        username = data['username']
        password = data['password']
        money = data["amount"]

        retJson, error = verifyCredentials(username, password)

        if error:
            return jsonify(retJson)        
        if money <= 0 :
            return jsonify(messages.negative_amount())        
        own = cashWithUser(username)        
        if own < money:
            return jsonify(messages.not_enough_money())

        debt = debtWithUser(username)
        new_debt = debt - money 
        returned_debt = 0 if new_debt < 0 else new_debt
        updateAccount(username, own - money)
        updateDebt(username, returned_debt)
        
        return jsonify(messages.success_payment(money))



api.add_resource(Register,'/register')
api.add_resource(Add,'/add')
api.add_resource(Transfer,'/transfer')
api.add_resource(Balance,'/balance')
api.add_resource(TakeLoan,'/takeloan')
api.add_resource(PayLoan,'/payloan')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)