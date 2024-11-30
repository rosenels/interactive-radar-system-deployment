import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from models import *

load_dotenv("database.env")

engine = create_engine(f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@localhost:5432/{os.getenv('POSTGRES_DB')}")

Base.metadata.create_all(engine)

MAX_FLIGHT_UPDATE_INTERVAL_IN_SECONDS = 10

INPUT_MODE = "sbs" # "raw-in" or "sbs"

REMOTE_HOST = "localhost"
PORT = 0 # 0 means the default port for the selected input mode
RAW_IN_DEFAULT_PORT = 30002
SBS_DEFAULT_PORT = 30003