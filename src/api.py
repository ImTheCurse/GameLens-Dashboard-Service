import os

from dotenv import load_dotenv

load_dotenv()

from flasgger import Swagger
from flask import Flask

from src.db import DatabaseConnection
from src.endpoints.runs import Runs

app = Flask(__name__)
swagger = Swagger(app)
app.register_blueprint(Runs, url_prefix="/api/v1/dashboard/runs")
conn_str = os.environ.get("PGSQL_CONN")
if not conn_str:
    raise ValueError("PGSQL_CONN environment variable is not set")

DatabaseConnection.initialize(conn_str)
