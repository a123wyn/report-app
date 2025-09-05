from functools import wraps
from flask import request, Response
import os

def check_auth(username, password):
    """检查用户名密码"""
    return (username == os.environ.get('AUTH_USERNAME', 'admin') and 
            password == os.environ.get('AUTH_PASSWORD', 'password'))

def authenticate():
    """发送 401 响应"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
