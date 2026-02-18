import uuid

from flasgger import swag_from
from flask import Blueprint, jsonify, request
from psycopg.types.json import Json

from ..db import DatabaseConnection

Runs = Blueprint("runs", __name__)


@Runs.route("/overview/insert", methods=["POST"])
@swag_from("docs/insert_runs.yml")
def insert_runs_summary():
    data = request.get_json()
    # Required Params
    game_id = data.get("game_id")
    run_id = data.get("run_id")
    started_at = data.get("started_at")
    result = data.get("result")

    # Optional Params
    ended_at = data.get("ended_at")
    duration_ms = data.get("duration_ms")
    final_stage_id = data.get("final_stage_id")
    final_stage_index = data.get("final_stage_index")
    final_room_index = data.get("final_room_index")
    total_damage_taken = data.get("total_damage_taken")
    choice_count = data.get("choice_count")

    try:
        with DatabaseConnection.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                       INSERT INTO run_summary
                       (
                       game_id,
                       run_id,
                       updated_at,
                       started_at,
                       ended_at,
                       duration_ms,
                       result,
                       final_stage_id,
                       final_stage_index,
                       final_room_index,
                       total_damage_taken,
                       choice_count
                       )
                       VALUES
                       (
                       %s,
                       %s,
                       NOW(),
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
                        started_at,
                        ended_at,
                        duration_ms,
                        result,
                        final_stage_id,
                        final_stage_index,
                        final_room_index,
                        total_damage_taken,
                        choice_count,
                    ),
                )
                conn.commit()
    except Exception as e:
        return jsonify(
            {"error": "Client Side Error", "message": str(e), "type": type(e).__name__}
        ), 400

    return jsonify({"message": "Runs inserted successfully"})


@Runs.route("/insert", methods=["POST"])
@swag_from("docs/insert_runs_raw.yml")
def insert_runs():
    data = request.get_json()
    # Required Params
    run_id = str(uuid.uuid4())
    game_id = data.get("game_id")
    session_id = data.get("session_id")
    started_at = data.get("started_at")

    # Optional Params
    ended_at = data.get("ended_at")
    end_reason = data.get("end_reason")
    game_version = data.get("game_version")
    run_meta = data.get("run_meta")

    try:
        with DatabaseConnection.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                       INSERT INTO run
                       (
                       run_id,
                       game_id,
                       session_id,
                       started_at,
                       ended_at,
                       end_reason,
                       game_version,
                       run_meta
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
                       %s
                       );
                       """,
                    (
                        run_id,
                        game_id,
                        session_id,
                        started_at,
                        ended_at,
                        end_reason,
                        game_version,
                        Json(run_meta),
                    ),
                )
                conn.commit()
    except Exception as e:
        return jsonify(
            {"error": "Client Side Error", "message": str(e), "type": type(e).__name__}
        ), 400

    return jsonify({"message": "Runs inserted successfully", "run_id": run_id})
