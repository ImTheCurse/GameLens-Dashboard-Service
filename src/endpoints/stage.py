from flasgger import swag_from
from flask import Blueprint, jsonify, request
from psycopg.types.json import Json

from src.util import validate_data

from ..db import DatabaseConnection

Stage = Blueprint("stage", __name__)


@Stage.route("/insert", methods=["POST"])
@swag_from("docs/insert_stage.yml")
def insert_stage():
    data = request.get_json()

    # Required Params
    stage_id = data.get("stage_id")
    game_id = data.get("game_id")
    name_norm = data.get("name_norm")
    first_seen_at = data.get("first_seen_at")
    last_seen_at = data.get("last_seen_at")

    validate_data(
        ["stage_id", "game_id", "name_norm", "first_seen_at", "last_seen_at"], data
    )

    # Optional Params
    stage_index = data.get("stage_index")
    canonical_name = data.get("canonical_name")
    metadata = data.get("metadata")

    try:
        with DatabaseConnection.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO stage
                    (
                        stage_id,
                        game_id,
                        stage_index,
                        name_norm,
                        canonical_name,
                        first_seen_at,
                        last_seen_at,
                        metadata
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
                        stage_id,
                        game_id,
                        stage_index,
                        name_norm,
                        canonical_name,
                        first_seen_at,
                        last_seen_at,
                        Json(metadata),
                    ),
                )
                conn.commit()
    except Exception as e:
        return jsonify(
            {"error": "Client Side Error", "message": str(e), "type": type(e).__name__}
        ), 400

    return jsonify({"message": "Stage inserted successfully"})
