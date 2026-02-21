import os

from dotenv import load_dotenv

load_dotenv()

from flasgger import Swagger
from flask import Flask

from src.db import DatabaseConnection
from src.endpoints.rooms import Rooms
from src.endpoints.runs import Runs
from src.endpoints.stage import Stage

app = Flask(__name__)
swagger = Swagger(app)
app.register_blueprint(Runs, url_prefix="/api/v1/dashboard/runs")
app.register_blueprint(Rooms, url_prefix="/api/v1/dashboard/rooms")
app.register_blueprint(Stage, url_prefix="/api/v1/dashboard/stage")
conn_str = os.environ.get("PGSQL_CONN")
if not conn_str:
    raise ValueError("PGSQL_CONN environment variable is not set")

DatabaseConnection.initialize(conn_str)
