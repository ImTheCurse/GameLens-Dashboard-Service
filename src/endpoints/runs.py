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

    if not game_id or not run_id or not result or not started_at:
        return jsonify(
            {
                "error": "Client Side Error",
                "message": "missing game_id or run_id or result or started_at.",
            }
        )

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

    if not game_id or not session_id or not started_at:
        return jsonify(
            {
                "error": "Client Side Error",
                "message": "missing game_id or session_id or started_at.",
            }
        )

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


@Runs.route("/overview", methods=["GET"])
@swag_from("docs/get_runs_overview.yml")
def get_run_overview():
    args = request.args

    # Required Params
    game_id = args.get("game_id")
    game_version = args.get("game_version")

    if not game_id or not game_version:
        return jsonify(
            {
                "error": "Client Side Error",
                "message": "game_id or game_version is required.",
                "type": "ValidationError",
            }
        ), 400

    try:
        with DatabaseConnection.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                       SELECT
                       *
                       FROM run
                       WHERE
                       game_id = %s AND game_version = %s
                       ;
                       """,
                    (game_id, game_version),
                )
                rows = cur.fetchall()
                result = [
                    {
                        "run_id": row[0],
                        "game_id": row[1],
                        "session_id": row[2],
                        "started_at": row[3],
                        "ended_at": row[4],
                        "end_reason": row[5],
                        "game_version": row[6],
                        "run_meta": row[7],
                    }
                    for row in rows
                ]

                total_runs = len(result)
                completions = sum(1 for r in result if r.get("end_reason") == "win")
                deaths = sum(1 for r in result if r.get("end_reason") == "loss")
                quits = total_runs - completions - deaths

                duration_values = [
                    (r["ended_at"] - r["started_at"]).total_seconds() * 1000
                    for r in result
                    if r.get("started_at") and r.get("ended_at")
                ]
                avg_duration_ms = (
                    sum(duration_values) / len(duration_values)
                    if duration_values
                    else None
                )

                response = {
                    "total_runs": total_runs,
                    "completions": completions,
                    "deaths": deaths,
                    "quits": quits,
                    "avg_duration_ms": avg_duration_ms,
                }

    except Exception as e:
        return jsonify(
            {"error": "Client Side Error", "message": str(e), "type": type(e).__name__}
        ), 400

    return jsonify(response)
