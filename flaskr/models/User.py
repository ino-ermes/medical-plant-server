from flaskr.db import db
from pymongo import ASCENDING

database = db.getDB()

_userColl = None

try:
    _userColl = database.create_collection("users")
except:
    _userColl = database.get_collection("users")

_userColl.create_index([("email", ASCENDING)], unique=True)

user_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "email",
            "name",
            "role",
            "created_at",
            "hash_password",
        ],
        "properties": {
            "email": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "role": {
                "enum": ["admin", "user"],
                "description": "can only be one of [admin] or [user] and is required",
            },
            "name": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "img_url": {
                "bsonType": "string",
                "description": "must be a string",
            },
            "created_at": {
                "bsonType": "date",
                "description": "must be a date and is required",
            },
            "hash_password": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "pwr_token": {
                "bsonType": "string",
                "description": "must be a string",
            },
            "pwr_expire": {
                "bsonType": "date",
                "description": "must be a string",
            },
        },
    }
}

database.command("collMod", "users", validator=user_validator)
