# Return Messages
def incorrect_password_info():
    return {
            "status": 302,
            "message": "Password did not match the account"
            }

def user_not_exist_info():
    return {
            "status": 301,
            "message": "User with that username does not exist."
            }

def user_create_success():
    return {
            "status": 200,
            "message": "You have done it! You have signed in API."
            }

def out_of_tokens_info(amount):
    return {
        "status":303,
        "message": "Not enough tokens to complete action."
    }


def incorrect_adminPW_info(amount):
    return {
        "status":302,
        "message": "Incorrect admin password"
    }

def refill_success_info():
    return {
        "status":200,
        "message": f'You have succesfully refill your tokens.'
    }