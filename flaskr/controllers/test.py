import csv
from pymongo import MongoClient

client = MongoClient(
    "mongodb+srv://ino_ermes:s2LkQTuM34FXIGpK@inoermes.4ly1mzn.mongodb.net/?retryWrites=true&w=majority"
)
medical_plant = client.medical_plant
# plantColl = medical_plant.get_collection("plants")
predictColl = medical_plant.create_collection("predicts")

# with open("plants2.txt", "r") as file:
#     reader = csv.reader(file, delimiter="?")

#     index = 0
#     for row in reader:
#         plantColl.insert_one(
#             {
#                 "_id": index,
#                 "common_name": row[0],
#                 "another_name": row[1],
#                 "binomial_name": row[2],
#                 "family": row[3],
#                 "usable_part": row[4],
#                 "function": row[5],
#                 "usage": row[6],
#             }
#         )
#         print(index)
#         index += 1
# client.close()

import os

root_dir = "C:/Users/Mio/Downloads/new/new"
plant_dirs = os.listdir(root_dir)
plant_dirs.sort()

import random
from datetime import datetime
from bson import ObjectId

def read_urls_from_file(file_path, max_url_count):
    with open(file_path, "r") as file:
        total_ulrs = [
            {
                "img_url": line.strip().replace("/s/", "/m/", 1),
                "thumb_img_url": line.strip(),
            }
            for line in file
            if line.strip()
        ]
        if len(total_ulrs) > max_url_count:
            total_ulrs = random.sample(total_ulrs, max_url_count)
        return total_ulrs


# with open("plants2.txt", "r") as file:
#     reader = csv.reader(file, delimiter="?")
#     plants_infos = [row for row in reader]
    
plant_id = 0
for plant in plant_dirs:
    full_plant_path = os.path.join(root_dir, plant)

    # insertedAvt = False
    for txt_file in ("leaf.txt", "flower.txt", "fruit.txt", "bark.txt", "habit.txt"):
        txt_path = os.path.join(full_plant_path, txt_file)
        if not os.path.exists(txt_path):
            continue
        image_urls = read_urls_from_file(txt_path, 50)
        
        for url in image_urls:
            
            # if not insertedAvt and txt_file == "leaf.txt":                
            #     plantColl.insert_one(
            #         {
            #             "_id": plant_id,
            #             "common_name": plants_infos[plant_id][0],
            #             "another_name": plants_infos[plant_id][1],
            #             "binomial_name": plants_infos[plant_id][2],
            #             "family": plants_infos[plant_id][3],
            #             "usable_part": plants_infos[plant_id][4],
            #             "function": plants_infos[plant_id][5],
            #             "usage": plants_infos[plant_id][6],
            #             "img_url": url.get("img_url"),
            #             "thumb_img_url": url.get("thumb_img_url"),
            #         }
            #     )
            #     insertedAvt = True
            
            predictColl.insert_one({
                "user_id": ObjectId('6585e7e6c9c7cf2966ca38a4'),
                "plant_id": plant_id,
                "organ": txt_file.split(".")[0],
                "img_url": url.get("img_url"),
                "thumb_img_url": url.get("thumb_img_url"),
                "status": "sharing",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            })
    plant_id += 1

client.close()