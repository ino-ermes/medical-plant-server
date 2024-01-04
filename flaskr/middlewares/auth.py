from functools import wraps
import jwt
from flask import request
import os
from bson import ObjectId
from flaskr.errors.unauthenicated import UnauthenticatedError
from flaskr.models.User import _userColl


def access_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        data = None
        if "Authorization" in request.headers:
            try:
                token = request.headers["Authorization"].split(" ")[1]
                data = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
            except:
                raise UnauthenticatedError("Invalid Authentication Header!")
        if not data:
            raise UnauthenticatedError("Authentication Token is missing!")

        if "user_id" not in data:
            raise UnauthenticatedError("Invalid Authentication token!")

        return f(ObjectId(data["user_id"]), *args, **kwargs)

    return decorated
