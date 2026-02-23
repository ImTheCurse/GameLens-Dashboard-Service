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


@Events.route("/choices/insert", methods=["POST"])
@swag_from("docs/insert_choice.yml")
def insert_choice():
    data = request.get_json() or {}

    # Required Params
    game_id = data.get("game_id")
    event_id = data.get("event_id")
    run_id = data.get("run_id")
    occurred_at = data.get("occurred_at")
    selected_upgrade_id = data.get("selected_upgrade_id")
    updated_at = data.get("updated_at")

    validate_data(
        [
            "game_id",
            "event_id",
            "run_id",
            "occurred_at",
            "selected_upgrade_id",
            "updated_at",
        ],
        data,
    )
    # Optional Params
    stage_index = data.get("stage_index")
    stage_id = data.get("stage_id")
    room_index = data.get("room_index")
    choice_context = data.get("choice_context")
    options_present = data.get("options_present")

    try:
        with DatabaseConnection.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO choice_fact
                    (
                        game_id,
                        run_id,
                        event_id,
                        occurred_at,
                        stage_index,
                        stage_id,
                        room_index,
                        choice_context,
                        selected_upgrade_id,
                        options_present,
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
                        %s
                    )
                    RETURNING choice_fact_id;
                    ;
                    """,
                    (
                        game_id,
                        run_id,
                        event_id,
                        occurred_at,
                        stage_index,
                        stage_id,
                        room_index,
                        choice_context,
                        selected_upgrade_id,
                        Json(options_present),
                        updated_at,
                    ),
                )
                choice_fact_id = int(cur.fetchone()[0])
                conn.commit()
    except Exception as e:
        return jsonify(
            {"error": "Client Side Error", "message": str(e), "type": type(e).__name__}
        ), 400

    return jsonify(
        {"message": "Choice inserted successfully", "choice_fact_id": choice_fact_id}
    )


@Events.route("/choices", methods=["GET"])
@swag_from("docs/get_choices.yml")
def get_choices_stats():
    args = request.args
    # Required Params
    game_id = args.get("game_id")
    game_version = args.get("game_version")
    validate_data(["game_id", "game_version"], args)
    try:
        with DatabaseConnection.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        cf.selected_upgrade_id as choice_name,
                        cf.options_present::jsonb AS items,
                        COUNT(*) AS total_picks,
                        SUM(CASE WHEN r.end_reason = 'win' THEN 1 ELSE 0 END) AS total_wins,
                        ROUND(
                            SUM(CASE WHEN r.end_reason = 'win' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
                            2
                        ) AS win_rate_percentage,
                        ROUND(
                            AVG(EXTRACT(EPOCH FROM (r.ended_at - r.started_at)))::numeric,
                            2
                        ) AS avg_duration_sec
                    FROM
                        choice_fact cf
                    JOIN
                        run r
                    ON
                        cf.game_id = r.game_id AND r.run_id = cf.run_id
                    WHERE
                        r.game_id = %s AND r.game_version = %s
                    GROUP BY
                        cf.selected_upgrade_id,
                        cf.options_present::jsonb
                    ORDER BY
                        cf.selected_upgrade_id,
                        total_picks DESC;
                    """,
                    (game_id, game_version),
                )
                rows = cur.fetchall()
                choices_stats = [
                    {
                        "choice_name": row[0],
                        "items": row[1],
                        "total_picks": int(row[2]),
                        "total_wins": int(row[3]),
                        "win_rate_percentage": float(row[4]),
                        "avg_duration_sec": float(row[5]),
                    }
                    for row in rows
                ]

    except Exception as e:
        return jsonify(
            {"error": "Client Side Error", "message": str(e), "type": type(e).__name__}
        ), 400

    return jsonify({"choices_stats": choices_stats}), 200


@Events.route("/boss/insert", methods=["POST"])
@swag_from("docs/insert_boss.yml")
def insert_boss():
    data = request.get_json()

    # Required params
    boss_name = data.get("boss_name")
    game_id = data.get("game_id")

    # Optional param
    metadata = data.get("metadata")

    validate_data(["boss_name", "game_id"], data)

    try:
        with DatabaseConnection.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO boss
                    (boss_name,game_id,metadata)
                    VALUES
                    (%s,%s,%s);
                    """,
                    (boss_name, game_id, Json(metadata)),
                )
                conn.commit()

    except Exception as e:
        return jsonify(
            {"error": "Client Side Error", "message": str(e), "type": type(e).__name__}
        ), 400

    return jsonify({"message": "Boss inserted successfully"}), 200


@Events.route("/boss/summary/insert", methods=["POST"])
@swag_from("docs/insert_boss_summary.yml")
def insert_boss_summary():
    data = request.get_json() or {}

    # Required params
    game_id = data.get("game_id")
    run_id = data.get("run_id")
    boss_seq = data.get("boss_seq")
    boss_name = data.get("boss_name")
    entered_at = data.get("entered_at")
    updated_at = data.get("updated_at")

    # Optional params
    stage_index = data.get("stage_index")
    stage_id = data.get("stage_id")
    defeated_at = data.get("defeated_at")
    duration_ms = data.get("duration_ms")
    defeated = data.get("defeated")
    damage_taken_in_boss = data.get("damage_taken_in_boss")

    validate_data(
        ["game_id", "run_id", "boss_seq", "boss_name", "entered_at", "updated_at"],
        data,
    )

    try:
        with DatabaseConnection.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO boss_summary
                    (
                        game_id,
                        run_id,
                        boss_seq,
                        stage_index,
                        stage_id,
                        boss_name,
                        entered_at,
                        defeated_at,
                        duration_ms,
                        defeated,
                        damage_taken_in_boss,
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
                        boss_seq,
                        stage_index,
                        stage_id,
                        boss_name,
                        entered_at,
                        defeated_at,
                        duration_ms,
                        defeated,
                        damage_taken_in_boss,
                        updated_at,
                    ),
                )
                conn.commit()
    except Exception as e:
        return jsonify(
            {"error": "Client Side Error", "message": str(e), "type": type(e).__name__}
        ), 400

    return jsonify({"message": "Boss summary inserted successfully"}), 200
