from flask import request, Blueprint
from flaskr.models.User import _userColl
from flaskr.errors.bad_request import BadRequestError
from flaskr.errors.not_found import NotFoundError
from flaskr.errors.forbidden import ForbiddenError
from flaskr.middlewares.auth import access_token_required
from bson import ObjectId
from cloudinary.uploader import upload

userBP = Blueprint("users", __name__, url_prefix="/api/v1/users")


@userBP.get("/<user_id>")
@access_token_required
def getUser(requestUserId, user_id):
    if str(requestUserId) != user_id:
        raise ForbiddenError("Permission denied!")

    user = _userColl.find_one(
        {"_id": ObjectId(user_id)}, {"hash_password": 0, "created_at": 0}
    )

    if not user:
        raise NotFoundError("Incorrect user id!")

    return {
        "user": user,
    }


@userBP.get("/my-info")
@access_token_required
def getUserInfo(requestUserId):
    user = _userColl.find_one(
        {"_id": requestUserId}, {"hash_password": 0, "created_at": 0}
    )

    if not user:
        raise NotFoundError("Incorrect user id!")

    return {
        "user": {
            "id":  user["_id"],
            "email": user["email"],
            "role": user["role"],
            "name": user["name"],
            "img_url": user["img_url"],
        }
    }


@userBP.patch("/<user_id>")
@access_token_required
def updateUser(requestUserId, user_id):
    if str(requestUserId) != user_id:
        raise ForbiddenError("Permission denied!")
    data = request.json
    if not data:
        raise BadRequestError("Data is not provided!")
    
    requestData = {
        "name": data.get("name"),
    }

    updateData = {k: v for k, v in requestData.items() if v is not None}
    if len(updateData.items()) == 0:
        raise BadRequestError("Data is not provided!")

    updatedUser = _userColl.find_one_and_update(
        {"_id": requestUserId},
        {"$set": updateData},
        return_document=True,
        projection={"hash_password": 0, "created_at": 0},
    )

    return {
        "user": {
            "id":  updatedUser["_id"],
            "email": updatedUser["email"],
            "role": updatedUser["role"],
            "name": updatedUser["name"],
            "img_url": updatedUser["img_url"],
        }
    }

@userBP.post("/<user_id>/avatar")
@access_token_required
def updataAvatar(requestUserId, user_id):
    if str(requestUserId) != user_id:
        raise ForbiddenError("Permission denied!")
    
    if "image" not in request.files or not request.files["image"].filename:
        raise BadRequestError("Missing image")
    if not request.files["image"].filename.endswith(("png", "jpg", "jpeg")):
        raise BadRequestError("Unsupported image type")

    upload_result = upload(request.files["image"], resource_type="image")
    img_url = upload_result["secure_url"]

    updatedUser = _userColl.find_one_and_update(
        {"_id": requestUserId},
        {"$set": {"img_url": img_url}},
        return_document=True,
        projection={"hash_password": 0, "created_at": 0},
    )

    return {
        "user": {
            "id":  updatedUser["_id"],
            "email": updatedUser["email"],
            "role": updatedUser["role"],
            "name": updatedUser["name"],
            "img_url": updatedUser["img_url"],
        }
    }