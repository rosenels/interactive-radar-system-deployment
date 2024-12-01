import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from models import *

RADAR_FLIGHTS_UPDATE_TIME_IN_SECONDS = 5

MAX_FLIGHT_UPDATE_INTERVAL_IN_SECONDS = 10

INPUT_MODE = "sbs" # "raw-in" or "sbs"

REMOTE_HOST = "localhost"
PORT = 0 # 0 means the default port for the selected input mode

RAW_IN_DEFAULT_PORT = 30002
SBS_DEFAULT_PORT = 30003

load_dotenv("database.env")

db_engine = create_engine(f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@localhost:5432/{os.getenv('POSTGRES_DB')}")

Base.metadata.create_all(db_engine) # Creates all tables that don't exist in the database

def load_settings():
    global RADAR_FLIGHTS_UPDATE_TIME_IN_SECONDS, MAX_FLIGHT_UPDATE_INTERVAL_IN_SECONDS, INPUT_MODE, REMOTE_HOST, PORT

    with Session(db_engine) as session:
        saved_settings = list(session.scalars(select(Configuration)))

        all_keys = [element.key for element in saved_settings]
        all_values = [element.value for element in saved_settings]

        if "RADAR_FLIGHTS_UPDATE_TIME_IN_SECONDS" in all_keys:
            RADAR_FLIGHTS_UPDATE_TIME_IN_SECONDS = all_values[all_keys.index("RADAR_FLIGHTS_UPDATE_TIME_IN_SECONDS")]
        else:
            session.add(Configuration("RADAR_FLIGHTS_UPDATE_TIME_IN_SECONDS", RADAR_FLIGHTS_UPDATE_TIME_IN_SECONDS))

        if "MAX_FLIGHT_UPDATE_INTERVAL_IN_SECONDS" in all_keys:
            MAX_FLIGHT_UPDATE_INTERVAL_IN_SECONDS = float(all_values[all_keys.index("MAX_FLIGHT_UPDATE_INTERVAL_IN_SECONDS")])
        else:
            session.add(Configuration("MAX_FLIGHT_UPDATE_INTERVAL_IN_SECONDS", MAX_FLIGHT_UPDATE_INTERVAL_IN_SECONDS))

        if "INPUT_MODE" in all_keys:
            INPUT_MODE = all_values[all_keys.index("INPUT_MODE")]
        else:
            session.add(Configuration("INPUT_MODE", INPUT_MODE))

        if "REMOTE_HOST" in all_keys:
            REMOTE_HOST = all_values[all_keys.index("REMOTE_HOST")]
        else:
            session.add(Configuration("REMOTE_HOST", REMOTE_HOST))

        if "PORT" in all_keys:
            PORT = int(all_values[all_keys.index("PORT")])
        else:
            session.add(Configuration("PORT", PORT))

        session.commit()

load_settings()