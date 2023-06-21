from flask import request

def authorize_user():
    return request.headers.get('Authorization')
