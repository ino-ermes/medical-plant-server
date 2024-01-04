from flaskr.db import db

database = db.getDB()

_predictColl = None

try:
    _predictColl = database.create_collection("predicts")
except:
    _predictColl = database.get_collection("predicts")

predict_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "user_id",
            "plant_id",
            "organ",
            "img_url",
            "thumb_img_url",
            "status",
            "created_at",
            "updated_at",
        ],
        "properties": {
            "user_id": {
                "bsonType": "objectId",
                "description": "must be an objectId and is required",
            },
            "plant_id": {
                "bsonType": "int",
                "description": "must be an int and is required",
            },
            "organ": {
                "enum": ["leaf", "flower", "fruit", "bark", "habit"],
                "description": "is required and can only be one of ['leaf', 'flower', 'fruit', 'bark', 'habit']",
            },
            "img_url": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "thumb_img_url": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "status": {
                "enum": ["private", "sharing"],
                "description": "is required and can only be one of ['private', 'sharing']",
            },
            "created_at": {
                "bsonType": "date",
                "description": "must be a date and is required",
            },
            "updated_at": {
                "bsonType": "date",
                "description": "must be a date and is required",
            },
        },
    }
}

database.command("collMod", "predicts", validator=predict_validator)
