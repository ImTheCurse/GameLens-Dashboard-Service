from flask import Blueprint, jsonify

Rooms = Blueprint("rooms", __name__)


@Rooms.route("/rooms", methods=["GET"])
def get_rooms():
    return jsonify({"message": "Get rooms"})
