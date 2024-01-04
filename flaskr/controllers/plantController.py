from flask import request, Blueprint
from flaskr.models.Plant import _plantColl
from flaskr.models.Predict import _predictColl
from flaskr.errors.bad_request import BadRequestError
from flaskr.errors.not_found import NotFoundError

plantBP = Blueprint("plants", __name__, url_prefix="/api/v1/plants")


@plantBP.get("")
def getAllplants():
    search = request.args.get("search")
    if search:
        plants = _plantColl.find(
            {
                "$text": {"$search": search},
            },
            {
                "_id": 1,
                "thumb_img_url": 1,
                "common_name": 1,
                "binomial_name": 1,
            },
        )
    else:
        plants = _plantColl.find(
            {},
            {
                "_id": 1,
                "thumb_img_url": 1,
                "common_name": 1,
                "binomial_name": 1,
            },
        )
    return {"plants": list(plants)}


@plantBP.get("/<int:plant_id>")
def getPlant(plant_id):
    plant = _plantColl.find_one({"_id": plant_id}, {"thumb_img_url": 0})

    if not plant:
        raise NotFoundError("Plant id does not exist")

    organPipeline = [
        {
            "$match": {
                "plant_id": plant_id,
                "status": "sharing",
            },
        },
        {
            "$group": {
                "_id": "$organ",
                "count": {"$sum": 1},
                "thumb_img_url": {"$first": "$thumb_img_url"},
            },
        },
        {
            "$project": {
                "_id": 0,
                "organ": "$_id",
                "count": 1,
                "thumb_img_url": 1,
            }
        },
    ]
    organs = list(_predictColl.aggregate(organPipeline))

    return {
        "plant": plant,
        "organs": organs,
    }


@plantBP.get("/<int:plant_id>/image")
def getPlantImages(plant_id):
    data = request.args

    organ = data.get("organ") or "all"
    # limit = int(data.get("limit") or 10)
    # offset = int(data.get("offset") or 0)

    organs = ["leaf", "flower", "fruit", "bark", "habit"]

    if organ != "all" and organ not in organs:
        raise BadRequestError(f"Organ must be one of {organs} or all")
    # if limit < 1 or limit > 10:
    #     limit = 10
    # if offset < 0:
    #     offset = 0

    if organ == "all":
        urls = _predictColl.find(
            {
                "plant_id": plant_id,
                "status": "sharing",
            },
            {
                "_id": 0,
                "organ": 1,
                "img_url": 1,
                "thumb_img_url": 1,
            },
        )
        total = _predictColl.count_documents(
            {
                "plant_id": plant_id,
                "status": "sharing",
            }
        )
    else:
        urls = _predictColl.find(
            {
                "plant_id": plant_id,
                "organ": organ,
                "status": "sharing",
            },
            {
                "_id": 0,
                "img_url": 1,
                "thumb_img_url": 1,
            },
        )
        total = _predictColl.count_documents(
            {
                "plant_id": plant_id,
                "organ": organ,
                "status": "sharing",
            }
        )

    img_per_page = 10
    num_pages = total // img_per_page
    if num_pages * img_per_page < total:
        num_pages += 1

    page = int(request.args.get("page") or 1)
    if page > num_pages:
        page = num_pages
    
    return {
        "plant_imgs": list(urls.skip((page - 1) * img_per_page).limit(img_per_page)),
        "total_pages": num_pages,
    }
