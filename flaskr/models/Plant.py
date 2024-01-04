from flaskr.db import db

database = db.getDB()

_plantColl = None

try:
    _plantColl = database.create_collection("plants")
except:
    _plantColl = database.get_collection("plants")

plant_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "common_name",
            "another_name",
            "binomial_name",
            "family",
            "usable_part",
            "function",
            "usage",
            "img_url",
            "thumb_img_url",
        ],
        "properties": {
            "common_name": {
                "bsonType": "string",
                "description": "must be an string and is required",
            },
            "another_name": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "binomial_name": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "family": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "usable_part": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "function": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "usage": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "img_url": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "thumb_img_url": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
        },
    }
}

database.command("collMod", "plants", validator=plant_validator)

_plantColl.create_index([
    ('common_name', 'text'),
    ('another_name', 'text'),
    ('binomial_name', 'text'),
    ('family', 'text'),
])
