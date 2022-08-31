# Return Messages
def incorrect_password_info():
    return {
            "status": 302,
            "message": "Password did not match the account"
            }

def user_exist_info():
    return {
            "status": 301,
            "message": "Invalid username"
            }

def user_sign_info():
    return {
            "status": 200,
            "message": "You have done it! You have signed in API."
            }

def out_of_tokens_info():
    return {
            "status": 303,
            "message": "You are out of tokens. Please refill"
            }

def incorrect_adminPW_info():
    return {
            "status": 304,
            "message": "Incorrect admin password"
            }

def refill_success_info(username,tokens):
    return {
        "status": 200,
        "total_tokens":tokens,
        "msg": "You have successfully refill the tokens for User: "+ username
    }

def similarity_use_info(ratio):
    return {
        "status":200,
        "ratio":ratio
    }