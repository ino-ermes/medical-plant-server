from http import HTTPStatus

def pymongo_handler(e):
    print(e)
    return {"message": e.details["errmsg"], "status coe": HTTPStatus.BAD_REQUEST}, HTTPStatus.BAD_REQUEST
