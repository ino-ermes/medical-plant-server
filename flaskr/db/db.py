from pymongo import MongoClient
import os

__medical_plant = None
__client = None


def getDB():
    return __medical_plant


def connectDB():
    global __medical_plant
    global __client

    if __client:
        __client.close()
    DATABASE_URL = os.getenv("MONGO_URL")
    client = MongoClient(DATABASE_URL)
    __medical_plant = client.medical_plant
