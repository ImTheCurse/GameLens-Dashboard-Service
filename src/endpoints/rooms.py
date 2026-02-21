from flasgger import swag_from
from flask import Blueprint, jsonify, request

from src.util import validate_data

from ..db import DatabaseConnection

Rooms = Blueprint("rooms", __name__)


@Rooms.route("/insert", methods=["POST"])
@swag_from("docs/insert_rooms.yml")
def insert_rooms():
    data = request.get_json()

    # Required Params
    game_id = data.get("game_id")
    run_id = data.get("run_id")
    room_seq = data.get("room_seq")
    entered_at = data.get("entered_at")
    updated_at = data.get("updated_at")

    validate_data(["game_id", "run_id", "room_seq", "entered_at", "updated_at"], data)

    # Optional Params
    stage_index = data.get("stage_index")
    stage_id = data.get("stage_id")
    room_index = data.get("room_index")
    room_name_norm = data.get("room_name_norm")
    exited_at = data.get("exited_at")
    completion_ms = data.get("completion_ms")
    damage_taken_in_room = data.get("damage_taken_in_room")

    try:
        with DatabaseConnection.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO room_summary
                    (
                        game_id,
                        run_id,
                        room_seq,
                        stage_index,
                        stage_id,
                        room_index,
                        room_name_norm,
                        entered_at,
                        exited_at,
                        completion_ms,
                        damage_taken_in_room,
                        updated_at
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    );
                    """,
                    (
                        game_id,
                        run_id,
                        room_seq,
                        stage_index,
                        stage_id,
                        room_index,
                        room_name_norm,
                        entered_at,
                        exited_at,
                        completion_ms,
                        damage_taken_in_room,
                        updated_at,
                    ),
                )
                conn.commit()

    except Exception as e:
        return jsonify(
            {"error": "Client Side Error", "message": str(e), "type": type(e).__name__}
        ), 400

    return jsonify({"message": "Rooms inserted successfully"})


# @Rooms.route("/rooms/progression", methods=["GET"])
# def get_rooms():
#     pass
