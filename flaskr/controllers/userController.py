from flask import request, Blueprint
from flaskr.models.User import _userColl
from flaskr.errors.bad_request import BadRequestError
from flaskr.errors.not_found import NotFoundError
from flaskr.errors.forbidden import ForbiddenError
from flaskr.middlewares.auth import access_token_required
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

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
        "user": user,
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
        "img_url": data.get("img_url"),
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

    return {"user": updatedUser}
