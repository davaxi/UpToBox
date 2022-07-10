import os
import re
import jwt
from datetime import datetime, timezone, timedelta


def get_token(authorization):
    if not authorization:
        return None

    match = re.findall('Bearer (.*)', authorization)
    if not match:
        return None

    return match[0]


def jwt_encode(data):
    data['iss'] = "utb:app"
    data['nbf'] = datetime.now(tz=timezone.utc)
    data['exp'] = datetime.now(tz=timezone.utc) + timedelta(minutes=15)

    return jwt.encode(data, os.getenv('JWT_KEY'), algorithm='HS256')


def jwt_decode(token):
    if not token:
        return None

    try:
        return jwt.decode(token, os.getenv('JWT_KEY'), leeway=10, algorithms=['HS256'], issuer="utb:app")
    except jwt.PyJWTError:
        return None
