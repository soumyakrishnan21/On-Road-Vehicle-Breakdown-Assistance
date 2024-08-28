import jwt
from datetime import datetime, timedelta
from django.conf import settings

def generate_token(user_id, user_type):
    payload = {
        'user_id': user_id,
        'user_type': user_type,
        'exp': datetime.utcnow() + timedelta(hours=24)  # Token expiry time
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token
