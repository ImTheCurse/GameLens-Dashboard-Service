CREATE TABLE "developer" (
  "developer_id" varchar PRIMARY KEY,
  "email" varchar UNIQUE NOT NULL,
  "display_name" varchar,
  "created_at" timestampz NOT NULL,
  "status" varchar NOT NULL,
  "auth_ref" varchar,
  "metadata" json
);

CREATE TABLE "game" (
  "game_id" varchar PRIMARY KEY,
  "name" varchar NOT NULL,
  "created_at" timestampz NOT NULL,
  "plugin_metadata" json,
  "game_metadata" json
);

CREATE TABLE "developer_game" (
  "developer_id" varchar NOT NULL,
  "game_id" varchar NOT NULL,
  "role" varchar NOT NULL,
  "granted_at" timestampz NOT NULL,
  PRIMARY KEY ("developer_id", "game_id")
);

CREATE TABLE "session" (
  "session_id" varchar PRIMARY KEY,
  "game_id" varchar NOT NULL,
  "started_at" timestampz NOT NULL,
  "ended_at" timestampz,
  "client_info" json
);

CREATE TABLE "run" (
  "run_id" varchar PRIMARY KEY,
  "game_id" varchar NOT NULL,
  "session_id" varchar NOT NULL,
  "started_at" timestampz NOT NULL,
  "ended_at" timestampz,
  "end_reason" varchar,
  "game_version" varchar,
  "run_meta" json
);

CREATE TABLE "raw_capture" (
  "capture_id" varchar PRIMARY KEY,
  "game_id" varchar NOT NULL,
  "session_id" varchar NOT NULL,
  "run_id" varchar,
  "captured_at" timestampz NOT NULL,
  "received_at" timestampz NOT NULL,
  "capture_kind" varchar NOT NULL,
  "input_device" varchar NOT NULL,
  "input_code" varchar,
  "mouse_x" int,
  "mouse_y" int,
  "screenshot_ref" varchar NOT NULL,
  "screenshot_hash" varchar,
  "image_width" int,
  "image_height" int,
  "status" varchar NOT NULL,
  "process_attempts" int,
  "last_error" varchar,
  "game_version" varchar,
  "extra" json
);

CREATE TABLE "pipeline_job" (
  "job_id" varchar PRIMARY KEY,
  "game_id" varchar NOT NULL,
  "capture_id" varchar NOT NULL,
  "run_id" varchar,
  "status" varchar NOT NULL,
  "attempts" int NOT NULL,
  "locked_by" varchar,
  "locked_at" timestampz,
  "pipeline_version" varchar,
  "model_version" varchar
);

CREATE TABLE "event_type_dim" (
  "event_type_id" varchar PRIMARY KEY,
  "event_type" varchar UNIQUE NOT NULL,
  "category" varchar,
  "description" varchar,
  "is_core" boolean NOT NULL DEFAULT true,
  "created_at" timestampz NOT NULL,
  "metadata" json
);

CREATE TABLE "event" (
  "event_id" varchar PRIMARY KEY,
  "game_id" varchar NOT NULL,
  "run_id" varchar NOT NULL,
  "occurred_at" timestampz NOT NULL,
  "ingested_at" timestampz NOT NULL,
  "event_type_id" varchar NOT NULL,
  "source_capture_id" varchar,
  "confidence" float,
  "pipeline_version" varchar,
  "model_version" varchar,
  "details" json NOT NULL
);

CREATE TABLE "boss" (
  "boss_id" varchar PRIMARY KEY,
  "game_id" varchar NOT NULL,
  "name_norm" varchar NOT NULL,
  "canonical_name" varchar,
  "first_seen_at" timestampz NOT NULL,
  "last_seen_at" timestampz NOT NULL,
  "encounter_count" int,
  "defeat_count" int,
  "metadata" json
);

CREATE TABLE "stage" (
  "stage_id" varchar PRIMARY KEY,
  "game_id" varchar NOT NULL,
  "stage_index" int,
  "name_norm" varchar NOT NULL,
  "canonical_name" varchar,
  "first_seen_at" timestampz NOT NULL,
  "last_seen_at" timestampz NOT NULL,
  "metadata" json
);

CREATE TABLE "upgrade" (
  "upgrade_id" varchar PRIMARY KEY,
  "game_id" varchar NOT NULL,
  "name_norm" varchar NOT NULL,
  "canonical_name" varchar,
  "first_seen_at" timestampz NOT NULL,
  "last_seen_at" timestampz NOT NULL,
  "picked_count" int NOT NULL,
  "passed_count" int NOT NULL,
  "runs_won_with" int NOT NULL,
  "runs_lost_with" int NOT NULL,
  "metadata" json
);

CREATE TABLE "run_summary" (
  "game_id" varchar NOT NULL,
  "run_id" varchar NOT NULL,
  "started_at" timestampz NOT NULL,
  "ended_at" timestampz,
  "duration_ms" int,
  "result" varchar,
  "final_stage_id" varchar,
  "final_stage_index" int,
  "final_room_index" int,
  "total_damage_taken" int,
  "choice_count" int,
  "updated_at" timestampz NOT NULL
);

CREATE TABLE "room_summary" (
  "game_id" varchar NOT NULL,
  "run_id" varchar NOT NULL,
  "room_seq" int NOT NULL,
  "stage_index" int,
  "stage_id" varchar,
  "room_index" int,
  "room_name_norm" varchar,
  "entered_at" timestampz NOT NULL,
  "exited_at" timestampz,
  "completion_ms" int,
  "damage_taken_in_room" int,
  "updated_at" timestampz NOT NULL
);

CREATE TABLE "boss_summary" (
  "game_id" varchar NOT NULL,
  "run_id" varchar NOT NULL,
  "boss_seq" int NOT NULL,
  "stage_index" int,
  "stage_id" varchar,
  "boss_id" varchar NOT NULL,
  "entered_at" timestampz NOT NULL,
  "defeated_at" timestampz,
  "duration_ms" int,
  "defeated" boolean,
  "damage_taken_in_boss" int,
  "updated_at" timestampz NOT NULL
);

CREATE TABLE "choice_fact" (
  "choice_fact_id" varchar PRIMARY KEY,
  "game_id" varchar NOT NULL,
  "run_id" varchar NOT NULL,
  "occurred_at" timestampz NOT NULL,
  "stage_index" int,
  "stage_id" varchar,
  "room_index" int,
  "choice_context" varchar,
  "selected_upgrade_id" varchar NOT NULL,
  "options_present" json,
  "updated_at" timestampz NOT NULL
);

CREATE TABLE "death_fact" (
  "death_fact_id" varchar PRIMARY KEY,
  "game_id" varchar NOT NULL,
  "run_id" varchar NOT NULL,
  "occurred_at" timestampz NOT NULL,
  "stage_index" int,
  "stage_id" varchar,
  "room_index" int,
  "hp" int,
  "max_hp" int,
  "upgrades_snapshot" json,
  "updated_at" timestampz NOT NULL
);

CREATE INDEX ON "developer_game" ("game_id");

CREATE INDEX ON "session" ("game_id", "started_at");

CREATE INDEX ON "run" ("game_id", "started_at");

CREATE INDEX ON "run" ("session_id", "started_at");

CREATE INDEX ON "raw_capture" ("status", "received_at");

CREATE INDEX ON "raw_capture" ("game_id", "session_id", "captured_at");

CREATE INDEX ON "raw_capture" ("run_id", "captured_at");

CREATE INDEX ON "pipeline_job" ("status");

CREATE INDEX ON "pipeline_job" ("game_id");

CREATE UNIQUE INDEX ON "pipeline_job" ("capture_id");

CREATE INDEX ON "pipeline_job" ("run_id");

CREATE UNIQUE INDEX ON "event_type_dim" ("event_type");

CREATE INDEX ON "event_type_dim" ("category");

CREATE INDEX ON "event" ("game_id", "occurred_at");

CREATE INDEX ON "event" ("run_id", "occurred_at");

CREATE INDEX ON "event" ("event_type_id", "occurred_at");

CREATE UNIQUE INDEX ON "boss" ("game_id", "name_norm");

CREATE UNIQUE INDEX ON "stage" ("game_id", "name_norm");

CREATE INDEX ON "stage" ("game_id", "stage_index");

CREATE UNIQUE INDEX ON "upgrade" ("game_id", "name_norm");

CREATE INDEX ON "run_summary" ("game_id", "started_at");

CREATE INDEX ON "room_summary" ("game_id", "run_id");

CREATE INDEX ON "room_summary" ("game_id", "stage_index");

CREATE INDEX ON "room_summary" ("stage_id");

CREATE INDEX ON "boss_summary" ("game_id", "run_id");

CREATE INDEX ON "boss_summary" ("game_id", "boss_id");

CREATE INDEX ON "boss_summary" ("stage_id");

CREATE INDEX ON "choice_fact" ("game_id", "selected_upgrade_id");

CREATE INDEX ON "choice_fact" ("run_id", "occurred_at");

CREATE INDEX ON "choice_fact" ("stage_id");

CREATE INDEX ON "death_fact" ("run_id", "occurred_at");

CREATE INDEX ON "death_fact" ("game_id", "occurred_at");

CREATE INDEX ON "death_fact" ("stage_id");

COMMENT ON COLUMN "developer"."developer_id" IS 'uuid/string';

COMMENT ON COLUMN "developer"."status" IS 'active|suspended|deleted';

COMMENT ON COLUMN "game"."game_id" IS 'uuid/string';

COMMENT ON COLUMN "developer_game"."role" IS 'owner|admin|analyst|viewer';

COMMENT ON COLUMN "session"."session_id" IS 'client-generated uuid/string';

COMMENT ON COLUMN "run"."run_id" IS 'client-generated uuid/string';

COMMENT ON COLUMN "run"."end_reason" IS 'win|loss|quit|unknown';

COMMENT ON COLUMN "run"."game_version" IS 'client game/app version (e.g., 1.2.3 / build-1842)';

COMMENT ON COLUMN "raw_capture"."capture_id" IS 'monotonic id or uuid/string';

COMMENT ON COLUMN "raw_capture"."captured_at" IS 'client timestamp';

COMMENT ON COLUMN "raw_capture"."received_at" IS 'server timestamp';

COMMENT ON COLUMN "raw_capture"."capture_kind" IS 'signal|click|timer|t-1|...';

COMMENT ON COLUMN "raw_capture"."input_device" IS 'mouse|keyboard|gamepad|system|unknown';

COMMENT ON COLUMN "raw_capture"."screenshot_ref" IS 'blob/object reference';

COMMENT ON COLUMN "raw_capture"."status" IS 'pending|processing|processed|delete_marked|failed';

COMMENT ON COLUMN "raw_capture"."game_version" IS 'capture-time version; default to run.game_version if unchanged';

COMMENT ON TABLE "pipeline_job" IS 'capture_id unique to avoid duplicate jobs for same capture; if you want multiple pipeline stages per capture, remove unique and add stage column.';

COMMENT ON COLUMN "pipeline_job"."job_id" IS 'monotonic id or uuid/string';

COMMENT ON COLUMN "pipeline_job"."capture_id" IS 'raw_capture.capture_id';

COMMENT ON COLUMN "pipeline_job"."status" IS 'queued|running|done|done_with_warnings|failed|canceled';

COMMENT ON COLUMN "event_type_dim"."event_type_id" IS 'stable id or slug; e.g., ''start_run''';

COMMENT ON COLUMN "event_type_dim"."event_type" IS 'canonical name; e.g., ''StartRun''';

COMMENT ON COLUMN "event_type_dim"."category" IS 'lifecycle|navigation|combat|choice|boss|system|unknown';

COMMENT ON COLUMN "event"."event_type_id" IS 'FK -> event_type_dim.event_type_id';

COMMENT ON COLUMN "boss"."name_norm" IS 'normalized OCR boss name (grouping key)';

COMMENT ON COLUMN "stage"."name_norm" IS 'normalized OCR stage/level name (grouping key)';

COMMENT ON TABLE "upgrade" IS 'passed_count requires choice_fact.options_present or explicit offer tracking; otherwise keep 0 or compute partially.';

COMMENT ON COLUMN "upgrade"."name_norm" IS 'normalized OCR upgrade name (grouping key)';

COMMENT ON TABLE "run_summary" IS 'PK is composite (game_id, run_id).';

COMMENT ON COLUMN "run_summary"."result" IS 'win|loss|quit|unknown';

COMMENT ON TABLE "room_summary" IS 'PK is composite (game_id, run_id, room_seq).';

COMMENT ON COLUMN "room_summary"."room_seq" IS 'visit order within the run';

COMMENT ON COLUMN "room_summary"."room_name_norm" IS 'optional if you want room labels without a room table';

COMMENT ON TABLE "boss_summary" IS 'PK is composite (game_id, run_id, boss_seq).';

COMMENT ON COLUMN "boss_summary"."boss_seq" IS 'encounter order within the run';

COMMENT ON COLUMN "choice_fact"."choice_fact_id" IS 'or use composite key';

COMMENT ON COLUMN "choice_fact"."choice_context" IS 'upgrade|reward|shop|event|unknown';

COMMENT ON COLUMN "choice_fact"."options_present" IS 'optional list of upgrade_ids offered';

ALTER TABLE "developer_game" ADD FOREIGN KEY ("developer_id") REFERENCES "developer" ("developer_id");

ALTER TABLE "developer_game" ADD FOREIGN KEY ("game_id") REFERENCES "game" ("game_id");

ALTER TABLE "session" ADD FOREIGN KEY ("game_id") REFERENCES "game" ("game_id");

ALTER TABLE "run" ADD FOREIGN KEY ("game_id") REFERENCES "game" ("game_id");

ALTER TABLE "run" ADD FOREIGN KEY ("session_id") REFERENCES "session" ("session_id");

ALTER TABLE "raw_capture" ADD FOREIGN KEY ("game_id") REFERENCES "game" ("game_id");

ALTER TABLE "raw_capture" ADD FOREIGN KEY ("session_id") REFERENCES "session" ("session_id");

ALTER TABLE "raw_capture" ADD FOREIGN KEY ("run_id") REFERENCES "run" ("run_id");

ALTER TABLE "pipeline_job" ADD FOREIGN KEY ("game_id") REFERENCES "game" ("game_id");

ALTER TABLE "pipeline_job" ADD FOREIGN KEY ("capture_id") REFERENCES "raw_capture" ("capture_id");

ALTER TABLE "pipeline_job" ADD FOREIGN KEY ("run_id") REFERENCES "run" ("run_id");

ALTER TABLE "event" ADD FOREIGN KEY ("game_id") REFERENCES "game" ("game_id");

ALTER TABLE "event" ADD FOREIGN KEY ("run_id") REFERENCES "run" ("run_id");

ALTER TABLE "event" ADD FOREIGN KEY ("source_capture_id") REFERENCES "raw_capture" ("capture_id");

ALTER TABLE "event" ADD FOREIGN KEY ("event_type_id") REFERENCES "event_type_dim" ("event_type_id");

ALTER TABLE "boss" ADD FOREIGN KEY ("game_id") REFERENCES "game" ("game_id");

ALTER TABLE "stage" ADD FOREIGN KEY ("game_id") REFERENCES "game" ("game_id");

ALTER TABLE "upgrade" ADD FOREIGN KEY ("game_id") REFERENCES "game" ("game_id");

ALTER TABLE "run_summary" ADD FOREIGN KEY ("game_id") REFERENCES "game" ("game_id");

ALTER TABLE "run_summary" ADD FOREIGN KEY ("run_id") REFERENCES "run" ("run_id");

ALTER TABLE "run_summary" ADD FOREIGN KEY ("final_stage_id") REFERENCES "stage" ("stage_id");

ALTER TABLE "room_summary" ADD FOREIGN KEY ("game_id") REFERENCES "game" ("game_id");

ALTER TABLE "room_summary" ADD FOREIGN KEY ("run_id") REFERENCES "run" ("run_id");

ALTER TABLE "room_summary" ADD FOREIGN KEY ("stage_id") REFERENCES "stage" ("stage_id");

ALTER TABLE "boss_summary" ADD FOREIGN KEY ("game_id") REFERENCES "game" ("game_id");

ALTER TABLE "boss_summary" ADD FOREIGN KEY ("run_id") REFERENCES "run" ("run_id");

ALTER TABLE "boss_summary" ADD FOREIGN KEY ("boss_id") REFERENCES "boss" ("boss_id");

ALTER TABLE "boss_summary" ADD FOREIGN KEY ("stage_id") REFERENCES "stage" ("stage_id");

ALTER TABLE "choice_fact" ADD FOREIGN KEY ("game_id") REFERENCES "game" ("game_id");

ALTER TABLE "choice_fact" ADD FOREIGN KEY ("run_id") REFERENCES "run" ("run_id");

ALTER TABLE "choice_fact" ADD FOREIGN KEY ("stage_id") REFERENCES "stage" ("stage_id");

ALTER TABLE "choice_fact" ADD FOREIGN KEY ("selected_upgrade_id") REFERENCES "upgrade" ("upgrade_id");

ALTER TABLE "death_fact" ADD FOREIGN KEY ("game_id") REFERENCES "game" ("game_id");

ALTER TABLE "death_fact" ADD FOREIGN KEY ("run_id") REFERENCES "run" ("run_id");

ALTER TABLE "death_fact" ADD FOREIGN KEY ("stage_id") REFERENCES "stage" ("stage_id");
