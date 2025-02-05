import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from models import *

RADAR_FLIGHTS_UPDATE_TIME_IN_SECONDS = 5

MAX_FLIGHT_UPDATE_INTERVAL_BEFORE_CONSIDERED_AS_LOST_IN_SECONDS = 10

INSTRUCTION_VALIDITY_TIME_AFTER_FLIGHT_IS_LOST_IN_SECONDS = 1800 # 30 minutes

MINIMUM_DESCENT_ALTITUDE_IN_FEET = 3000

MAX_TIME_FOR_100_FT_ALTITUDE_CHANGE_IN_SECONDS = 30
ALTITUDE_TOLERANCE_IN_FEET = 50

MAX_TIME_FOR_10_KNOTS_GROUND_SPEED_CHANGE_IN_SECONDS = 20
GROUND_SPEED_TOLERANCE_IN_KNOTS = 5

MAX_TIME_FOR_10_DEGREES_TRACK_CHANGE_IN_SECONDS = 20
TRACK_TOLERANCE_IN_DEGREES = 2

WARNING_REMEMBER_INTERVAL_IN_SECONDS = 60

LOG_ALL_AIRCRAFT_MESSAGES = 0 # 0 means False, 1 means True

load_dotenv()

FLIGHT_DATA_INPUT_MODE = os.getenv("FLIGHT_DATA_INPUT_MODE") # "raw-in" or "sbs"
FLIGHT_DATA_HOST = os.getenv("FLIGHT_DATA_HOST")
FLIGHT_DATA_PORT = int(os.getenv("FLIGHT_DATA_PORT")) # 0 means the default port for the selected input mode

RAW_IN_DEFAULT_PORT = 30002
SBS_DEFAULT_PORT = 30003

db_engine = create_engine(f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_DB_HOST')}:{os.getenv('POSTGRES_DB_PORT')}/{os.getenv('POSTGRES_DB')}")

Base.metadata.create_all(db_engine) # Creates all tables that don't exist in the database

def load_settings():
    with Session(db_engine) as session:
        saved_settings = list(session.scalars(select(Configuration)))

        all_keys = [element.key for element in saved_settings]
        all_values = [element.value for element in saved_settings]

        global RADAR_FLIGHTS_UPDATE_TIME_IN_SECONDS
        if "RADAR_FLIGHTS_UPDATE_TIME_IN_SECONDS" in all_keys:
            RADAR_FLIGHTS_UPDATE_TIME_IN_SECONDS = float(all_values[all_keys.index("RADAR_FLIGHTS_UPDATE_TIME_IN_SECONDS")])
        else:
            session.add(Configuration("RADAR_FLIGHTS_UPDATE_TIME_IN_SECONDS", RADAR_FLIGHTS_UPDATE_TIME_IN_SECONDS))

        global MAX_FLIGHT_UPDATE_INTERVAL_BEFORE_CONSIDERED_AS_LOST_IN_SECONDS
        if "MAX_FLIGHT_UPDATE_INTERVAL_BEFORE_CONSIDERED_AS_LOST_IN_SECONDS" in all_keys:
            MAX_FLIGHT_UPDATE_INTERVAL_BEFORE_CONSIDERED_AS_LOST_IN_SECONDS = float(all_values[all_keys.index("MAX_FLIGHT_UPDATE_INTERVAL_BEFORE_CONSIDERED_AS_LOST_IN_SECONDS")])
        else:
            session.add(Configuration("MAX_FLIGHT_UPDATE_INTERVAL_BEFORE_CONSIDERED_AS_LOST_IN_SECONDS", MAX_FLIGHT_UPDATE_INTERVAL_BEFORE_CONSIDERED_AS_LOST_IN_SECONDS))

        global INSTRUCTION_VALIDITY_TIME_AFTER_FLIGHT_IS_LOST_IN_SECONDS
        if "INSTRUCTION_VALIDITY_TIME_AFTER_FLIGHT_IS_LOST_IN_SECONDS" in all_keys:
            INSTRUCTION_VALIDITY_TIME_AFTER_FLIGHT_IS_LOST_IN_SECONDS = float(all_values[all_keys.index("INSTRUCTION_VALIDITY_TIME_AFTER_FLIGHT_IS_LOST_IN_SECONDS")])
        else:
            session.add(Configuration("INSTRUCTION_VALIDITY_TIME_AFTER_FLIGHT_IS_LOST_IN_SECONDS", INSTRUCTION_VALIDITY_TIME_AFTER_FLIGHT_IS_LOST_IN_SECONDS))

        global MINIMUM_DESCENT_ALTITUDE_IN_FEET
        if "MINIMUM_DESCENT_ALTITUDE_IN_FEET" in all_keys:
            MINIMUM_DESCENT_ALTITUDE_IN_FEET = int(all_values[all_keys.index("MINIMUM_DESCENT_ALTITUDE_IN_FEET")])
        else:
            session.add(Configuration("MINIMUM_DESCENT_ALTITUDE_IN_FEET", MINIMUM_DESCENT_ALTITUDE_IN_FEET))

        global MAX_TIME_FOR_100_FT_ALTITUDE_CHANGE_IN_SECONDS
        if "MAX_TIME_FOR_100_FT_ALTITUDE_CHANGE_IN_SECONDS" in all_keys:
            MAX_TIME_FOR_100_FT_ALTITUDE_CHANGE_IN_SECONDS = float(all_values[all_keys.index("MAX_TIME_FOR_100_FT_ALTITUDE_CHANGE_IN_SECONDS")])
        else:
            session.add(Configuration("MAX_TIME_FOR_100_FT_ALTITUDE_CHANGE_IN_SECONDS", MAX_TIME_FOR_100_FT_ALTITUDE_CHANGE_IN_SECONDS))

        global ALTITUDE_TOLERANCE_IN_FEET
        if "ALTITUDE_TOLERANCE_IN_FEET" in all_keys:
            ALTITUDE_TOLERANCE_IN_FEET = int(all_values[all_keys.index("ALTITUDE_TOLERANCE_IN_FEET")])
        else:
            session.add(Configuration("ALTITUDE_TOLERANCE_IN_FEET", ALTITUDE_TOLERANCE_IN_FEET))

        global MAX_TIME_FOR_10_KNOTS_GROUND_SPEED_CHANGE_IN_SECONDS
        if "MAX_TIME_FOR_10_KNOTS_GROUND_SPEED_CHANGE_IN_SECONDS" in all_keys:
            MAX_TIME_FOR_10_KNOTS_GROUND_SPEED_CHANGE_IN_SECONDS = float(all_values[all_keys.index("MAX_TIME_FOR_10_KNOTS_GROUND_SPEED_CHANGE_IN_SECONDS")])
        else:
            session.add(Configuration("MAX_TIME_FOR_10_KNOTS_GROUND_SPEED_CHANGE_IN_SECONDS", MAX_TIME_FOR_10_KNOTS_GROUND_SPEED_CHANGE_IN_SECONDS))

        global GROUND_SPEED_TOLERANCE_IN_KNOTS
        if "GROUND_SPEED_TOLERANCE_IN_KNOTS" in all_keys:
            GROUND_SPEED_TOLERANCE_IN_KNOTS = int(all_values[all_keys.index("GROUND_SPEED_TOLERANCE_IN_KNOTS")])
        else:
            session.add(Configuration("GROUND_SPEED_TOLERANCE_IN_KNOTS", GROUND_SPEED_TOLERANCE_IN_KNOTS))

        global MAX_TIME_FOR_10_DEGREES_TRACK_CHANGE_IN_SECONDS
        if "MAX_TIME_FOR_10_DEGREES_TRACK_CHANGE_IN_SECONDS" in all_keys:
            MAX_TIME_FOR_10_DEGREES_TRACK_CHANGE_IN_SECONDS = float(all_values[all_keys.index("MAX_TIME_FOR_10_DEGREES_TRACK_CHANGE_IN_SECONDS")])
        else:
            session.add(Configuration("MAX_TIME_FOR_10_DEGREES_TRACK_CHANGE_IN_SECONDS", MAX_TIME_FOR_10_DEGREES_TRACK_CHANGE_IN_SECONDS))

        global TRACK_TOLERANCE_IN_DEGREES
        if "TRACK_TOLERANCE_IN_DEGREES" in all_keys:
            TRACK_TOLERANCE_IN_DEGREES = int(all_values[all_keys.index("TRACK_TOLERANCE_IN_DEGREES")])
        else:
            session.add(Configuration("TRACK_TOLERANCE_IN_DEGREES", TRACK_TOLERANCE_IN_DEGREES))

        global WARNING_REMEMBER_INTERVAL_IN_SECONDS
        if "WARNING_REMEMBER_INTERVAL_IN_SECONDS" in all_keys:
            WARNING_REMEMBER_INTERVAL_IN_SECONDS = float(all_values[all_keys.index("WARNING_REMEMBER_INTERVAL_IN_SECONDS")])
        else:
            session.add(Configuration("WARNING_REMEMBER_INTERVAL_IN_SECONDS", WARNING_REMEMBER_INTERVAL_IN_SECONDS))

        global FLIGHT_DATA_INPUT_MODE
        if "FLIGHT_DATA_INPUT_MODE" in all_keys:
            FLIGHT_DATA_INPUT_MODE = all_values[all_keys.index("FLIGHT_DATA_INPUT_MODE")]
        else:
            session.add(Configuration("FLIGHT_DATA_INPUT_MODE", FLIGHT_DATA_INPUT_MODE))

        global FLIGHT_DATA_HOST
        if "FLIGHT_DATA_HOST" in all_keys:
            FLIGHT_DATA_HOST = all_values[all_keys.index("FLIGHT_DATA_HOST")]
        else:
            session.add(Configuration("FLIGHT_DATA_HOST", FLIGHT_DATA_HOST))

        global FLIGHT_DATA_PORT
        if "FLIGHT_DATA_PORT" in all_keys:
            FLIGHT_DATA_PORT = int(all_values[all_keys.index("FLIGHT_DATA_PORT")])
        else:
            session.add(Configuration("FLIGHT_DATA_PORT", FLIGHT_DATA_PORT))

        global LOG_ALL_AIRCRAFT_MESSAGES
        if "LOG_ALL_AIRCRAFT_MESSAGES" in all_keys:
            LOG_ALL_AIRCRAFT_MESSAGES = int(all_values[all_keys.index("LOG_ALL_AIRCRAFT_MESSAGES")])
        else:
            session.add(Configuration("LOG_ALL_AIRCRAFT_MESSAGES", LOG_ALL_AIRCRAFT_MESSAGES))

        session.commit()

load_settings()