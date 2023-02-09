from . import app
import os
import json
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401
from pymongo import MongoClient
from bson import json_util
from pymongo.results import InsertOneResult
from bson.objectid import ObjectId

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "songs.json")
songs_list: list = json.load(open(json_url))

client = MongoClient(
    f"mongodb://{app.config['MONGO_USERNAME']}:{app.config['MONGO_PASSWORD']}@localhost")
db = client.songs
db.songs.delete_many({})
db.songs.insert_many(songs_list)


def parse_json(data):
    return json.loads(json_util.dumps(data))

######################################################################
# RETURN HEALTH OF THE APP
######################################################################


@app.route("/health")
def healthz():
    return jsonify(dict(status="OK")), 200


######################################################################
# COUNT THE NUMBER OF SONGS
######################################################################
@app.route("/count")
def count():
    """return length of data"""
    count = db.songs.count_documents({})

    return {"count": count}, 200


######################################################################
# GET ALL SONGS
######################################################################
@app.route("/song", methods=["GET"])
def songs():
    # docker run -d --name mongodb-test -e MONGO_INITDB_ROOT_USERNAME=user
    # -e MONGO_INITDB_ROOT_PASSWORD=password -e MONGO_INITDB_DATABASE=collection mongo
    results = list(db.songs.find({}))
    print(results[0])
    return {"songs": parse_json(results)}, 200


######################################################################
# GET A SONG
######################################################################
@app.route("/song/<int:id>", methods=["GET"])
def get_song_by_id(id):
    song = db.songs.find_one({"id": id})
    if not song:
        return {"message": f"song with id {id} not found"}, 404
    return parse_json(song), 200

######################################################################
# CREATE A SONG
######################################################################


@app.route("/song", methods=["POST"])
def create_song():
    # get data from the json body
    song_in = request.json

    print(song_in["id"])

    # if the id is already there, return 303 with the URL for the resource
    song = db.songs.find_one({"id": song_in["id"]})
    if song:
        return {
            "Message": f"song with id {song_in['id']} already present"
        }, 302

    insert_id: InsertOneResult = db.songs.insert_one(song_in)

    return {"inserted id": parse_json(insert_id.inserted_id)}, 201


######################################################################
# UPDATE A SONG
######################################################################
@app.route("/song/<int:id>", methods=["PUT"])
def update_song(id):

    # get data from the json body
    song_in = request.json

    song = db.songs.find_one({"id": id})

    if song == None:
        return {"message": "song not found"}, 404

    updated_data = {"$set": song_in}

    result = db.songs.update_one({"id": id}, updated_data)

    if result.modified_count == 0:
        return {"message": "song found, but nothing updated"}, 200
    else:
        return parse_json(db.songs.find_one({"id": id})), 201

######################################################################
# DELETE A SONG
######################################################################


@app.route("/song/<int:id>", methods=["DELETE"])
def delete_song(id):

    result = db.songs.delete_one({"id": id})
    if result.deleted_count == 0:
        return {"message": "song not found"}, 404
    else:
        return "", 204
