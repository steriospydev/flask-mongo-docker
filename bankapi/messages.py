# Return Messages
# 200 messages
def user_create_success():
    return {
            "status": 200,
            "message": "You have done it! You have signed in API."
            }

def success_deposit():
    return {
        "status":200,
        "message": "Amount deposit successfully to yout account."
    }

def success_loan(amount):
    return {
        "status":200,
        "message": f'You have succesfully took {amount} as loan.'
    }

def success_payment(amount):
    return {
        "status":200,
        "message": f'You have succesfully paid {amount}$ of your debt.'
    }



def success_transaction(amount):
    return {
        "status":200,
        "message": f"You have successfully transfered {amount} $."
    }

# 300 responses

def user_not_exist_info():
    return {
            "status": 301,
            "message": "User with that username does not exist."
            }

def incorrect_password_info():
    return {
            "status": 302,
            "message": "Password did not match the account"
            }

def not_enough_money():
    return {
        "status":303,
        "message":"Not enough money."
    }

def negative_amount():
    return {
        "status":304,
        "message":"Incorrect amount of money. Amount must be greater than 0."
    }

def low_funds():
    return {
        "status":304,
        "message": 'Not enough money into account to complete transaction. Please deposit and try again.'
    }
