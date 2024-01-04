from flask import request, Blueprint
from flaskr.models.Plant import _plantColl
from flaskr.models.Predict import _predictColl
from flaskr.errors.bad_request import BadRequestError
from flaskr.errors.not_found import NotFoundError
from flaskr.utils.predict_helper import Predicter
from flaskr.middlewares.auth import access_token_required
from bson import ObjectId
from datetime import datetime
from pymongo import ASCENDING

predictBP = Blueprint("predicts", __name__, url_prefix="/api/v1/predicts")


@predictBP.post("")
@access_token_required
def predictPlant(requestUserId):
    data = request.json

    image_url = data.get("img_url")

    if not image_url:
        raise BadRequestError("No image was sent")

    predictResults = Predicter.get_instance().predict(image_url)

    _predictColl.insert_one(
        {
            "user_id": requestUserId,
            "plant_id": int(predictResults[0]),
            "organ": "leaf",
            "img_url": image_url,
            "thumb_img_url": data.get("thumb_img_url"),
            "status": "private",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
    )

    predictResults.sort()
    indices = [int(i) for i in predictResults]
    confidences = [round((i - int(i)) * 100.0, 2) for i in predictResults]
    plantInfos = _plantColl.find(
        {"_id": {"$in": indices}},
        {
            "common_name": 1,
            "binomial_name": 1,
            "thumb_img_url": 1,
        },
    ).sort("_id", ASCENDING)

    plantInfos = list(plantInfos)
    for i in range(5):
        plantInfos[i]["confidence"] = confidences[i]

    plantInfos.sort(key=lambda x: x["confidence"], reverse=True)

    return {
        "predict_list": plantInfos,
    }


@predictBP.get("")
@access_token_required
def getHistory(requestUserId):
    data = request.args

    # limit = int(data.get("limit") or 10)
    # offset = int(data.get("offset") or 0)

    # if limit < 1 or limit > 10:
    #     limit = 10
    # if offset < 0:
    #     offset = 0

    total = _predictColl.count_documents({"user_id": requestUserId})
    num_per_page = 10
    num_pages = total // num_per_page
    if num_pages * num_per_page < total:
        num_pages += 1

    page = int(data.get("page") or 1)
    if page > num_pages:
        page = num_pages

    pipeline = [
        {
            "$match": {
                "user_id": requestUserId,
            },
        },
        {
            "$sort": {
                "updated_at": -1,
            }
        },
        {
            "$skip": (page - 1) * num_per_page,
        },
        {
            "$limit": num_per_page,
        },
        {
            "$lookup": {
                "from": "plants",
                "localField": "plant_id",
                "foreignField": "_id",
                "as": "plant",
            },
        },
        {
            "$unwind": "$plant",
        },
        {
            "$project": {
                "_id": 1,
                "plant_id": "$plant._id",
                "common_name": "$plant.common_name",
                "binomial_name": "$plant.binomial_name",
                # "organ": 1,
                "thumb_img_url": 1,
                "status": 1,
                # "created_at": 1,
                "updated_at": 1,
            },
        },
    ]
    predicts = _predictColl.aggregate(pipeline)
    return {
        "predicts": list(predicts),
        "total_pages": num_pages,
    }


@predictBP.delete("/<predict_id>")
@access_token_required
def deletePredict(requestUserId, predict_id):
    deleted = (
        _predictColl.delete_one(
            {
                "_id": ObjectId(predict_id),
                "user_id": requestUserId,
            }
        ).deleted_count
        == 1
    )

    if not deleted:
        raise NotFoundError("No predict found")
    return {
        "message": "deleted successfully",
    }


@predictBP.patch("/<predict_id>")
@access_token_required
def updatePredict(requestUserId, predict_id):
    data = request.json

    plant_id = data.get("plant_id")
    organ = data.get("organ")
    organs = ["leaf", "flower", "fruit", "bark", "habit"]

    if not plant_id or organ not in organs:
        raise BadRequestError("Invalid data")

    plant = _plantColl.find_one({"_id": plant_id}, {"_id": 1})
    if not plant:
        raise NotFoundError("Invalid plant id")
    plant_id = plant["_id"]

    updated = (
        _predictColl.update_one(
            {
                "_id": ObjectId(predict_id),
                "user_id": requestUserId,
            },
            {
                "plant_id": plant_id,
                "organ": organ,
            },
        ).modified_count
        == 1
    )

    if not updated:
        raise NotFoundError("No predict found")
    return {
        "message": "updated successfully",
    }

@predictBP.post("/rasp")
def predictPlantForRasp():
    data = request.json

    image_url = data.get("img_url")

    if not image_url:
        raise BadRequestError("No image was sent")

    predictResults = Predicter.get_instance().predict(image_url)

    predictResults.sort()
    indices = [int(i) for i in predictResults]
    confidences = [round((i - int(i)) * 100.0, 2) for i in predictResults]
    plantInfos = _plantColl.find(
        {"_id": {"$in": indices}},
        {
            "common_name": 1,
            "binomial_name": 1,
            "thumb_img_url": 1,
        },
    ).sort("_id", ASCENDING)

    plantInfos = list(plantInfos)
    for i in range(5):
        plantInfos[i]["confidence"] = confidences[i]

    plantInfos.sort(key=lambda x: x["confidence"], reverse=True)

    bestPlant = _plantColl.find_one({"_id": plantInfos[0]["_id"]}, {
        "another_name": 1,
        "family": 1,
        "usable_part": 1,
        "function": 1,
        "usage": 1,
    })

    return {
        "predict_list": plantInfos,
        "best_plant": bestPlant,
    }

