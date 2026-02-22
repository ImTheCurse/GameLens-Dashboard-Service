from flasgger import swag_from
from flask import Blueprint, jsonify, request
from psycopg.types.json import Json

from src.db import DatabaseConnection
from src.util import validate_data

Events = Blueprint("events", __name__)


@Events.route("/insert", methods=["POST"])
@swag_from("docs/insert_events.yml")
def insert_event():
    data = request.get_json() or {}

    # Required Params
    game_id = data.get("game_id")
    run_id = data.get("run_id")
    occurred_at = data.get("occurred_at")
    ingested_at = data.get("ingested_at")
    event_type_id = data.get("event_type_id")
    details = data.get("details")

    validate_data(
        [
            "game_id",
            "run_id",
            "occurred_at",
            "ingested_at",
            "event_type_id",
            "details",
        ],
        data,
    )

    # Optional Params
    source_capture_id = data.get("source_capture_id")
    confidence = data.get("confidence")
    pipeline_version = data.get("pipeline_version")
    model_version = data.get("model_version")

    try:
        with DatabaseConnection.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO event
                    (
                        game_id,
                        run_id,
                        occurred_at,
                        ingested_at,
                        event_type_id,
                        source_capture_id,
                        confidence,
                        pipeline_version,
                        model_version,
                        details
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
                        %s
                    )
                    RETURNING event_id;
                    """,
                    (
                        game_id,
                        run_id,
                        occurred_at,
                        ingested_at,
                        event_type_id,
                        source_capture_id,
                        confidence,
                        pipeline_version,
                        model_version,
                        Json(details),
                    ),
                )
                event_id = int(cur.fetchone()[0])
                conn.commit()
    except Exception as e:
        return jsonify(
            {"error": "Client Side Error", "message": str(e), "type": type(e).__name__}
        ), 400

    return jsonify({"message": "Event inserted successfully", "event_id": event_id})
