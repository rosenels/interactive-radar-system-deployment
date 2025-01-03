from datetime import datetime, timedelta
from settings import *
from models import *

def validate_altitude(altitude, instructed_altitude):
    if altitude is None or instructed_altitude is None:
        return True
    if altitude < instructed_altitude - ALTITUDE_TOLERANCE_IN_FEET:
        return False
    if altitude > instructed_altitude + ALTITUDE_TOLERANCE_IN_FEET:
        return False
    return True

def validate_ground_speed(ground_speed, instructed_ground_speed):
    if ground_speed is None or instructed_ground_speed is None:
        return True
    if ground_speed < instructed_ground_speed - GROUND_SPEED_TOLERANCE_IN_KNOTS:
        return False
    if ground_speed > instructed_ground_speed + GROUND_SPEED_TOLERANCE_IN_KNOTS:
        return False
    return True

def validate_track(track, instructed_track):
    if track is None or instructed_track is None:
        return True
    if abs(track - instructed_track) > TRACK_TOLERANCE_IN_DEGREES:
        if track >= 180:
            track -= 360
        if instructed_track >= 180:
            instructed_track -= 360
        if abs(track - instructed_track) > TRACK_TOLERANCE_IN_DEGREES:
            return False
    return True

def calculate_due_timestamp(current_value, initial_value, instructed_value, instructed_at_timestamp, seconds_for_one_step, step_size):
    if current_value is None or initial_value is None or instructed_value is None or instructed_at_timestamp is None:
        return None
    assert isinstance(instructed_at_timestamp, datetime)

    diff = instructed_value - initial_value

    if diff < 0:
        diff *= -1

    return instructed_at_timestamp + timedelta(seconds = (seconds_for_one_step * diff) / step_size)

def validate_instructions(flight_dict, instructions):
    assert isinstance(flight_dict, dict)
    assert isinstance(instructions, InstructionsFromATC)

    if instructions.initial_altitude is None:
        instructions.initial_altitude = flight_dict["altitude"]

    if instructions.initial_ground_speed is None:
        instructions.initial_ground_speed = flight_dict["ground_speed"]

    if instructions.initial_track is None:
        instructions.initial_track = flight_dict["track"]

    flight_dict["instructions"] = {}
    flight_dict["instructions"]["id"] = instructions.id
    flight_dict["instructions"]["atc_user_id"] = instructions.atc_user_id
    flight_dict["instructions"]["atc_user_fullname"] = instructions.atc_user_fullname
    flight_dict["instructions"]["altitude"] = instructions.altitude
    flight_dict["instructions"]["altitude_valid"] = validate_altitude(flight_dict["altitude"], instructions.altitude)
    flight_dict["instructions"]["altitude_due"] = calculate_due_timestamp(flight_dict["altitude"], instructions.initial_altitude, instructions.altitude, instructions.altitude_timestamp, MAX_TIME_FOR_100_FT_ALTITUDE_CHANGE_IN_SECONDS, 100)
    flight_dict["instructions"]["ground_speed"] = instructions.ground_speed
    flight_dict["instructions"]["ground_speed_valid"] = validate_ground_speed(flight_dict["ground_speed"], instructions.ground_speed)
    flight_dict["instructions"]["ground_speed_due"] = calculate_due_timestamp(flight_dict["ground_speed"], instructions.initial_ground_speed, instructions.ground_speed, instructions.ground_speed_timestamp, MAX_TIME_FOR_10_KNOTS_GROUND_SPEED_CHANGE_IN_SECONDS, 10)
    flight_dict["instructions"]["track"] = instructions.track
    flight_dict["instructions"]["track_valid"] = validate_track(flight_dict["track"], instructions.track)
    flight_dict["instructions"]["track_due"] = calculate_due_timestamp(flight_dict["track"], instructions.initial_track, instructions.track, instructions.track_timestamp, MAX_TIME_FOR_90_DEGREES_TRACK_CHANGE_IN_SECONDS, 90)
    flight_dict["instructions"]["timestamp"] = instructions.timestamp