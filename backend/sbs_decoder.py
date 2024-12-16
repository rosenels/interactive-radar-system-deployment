from datetime import datetime, timedelta
from dateutil import parser
import settings

flights = []

new_flight = {
    "session_id": None,
    "aircraft_id": None,
    "icao": None,
    "flight_id": None,
    "last_datetime": None,
    "callsign": None,
    "altitude": None,
    "ground_speed": None,
    "track": None,
    "latitude": None,
    "longitude": None,
    "vertical_rate": None,
    "squawk": None,
    "alert_squawk_change": None,
    "emergency_code": None,
    "spi_ident": None,
    "on_ground": None,
    "instructions": None
}

def get_flight(icao):
    for flight in flights:
        if flight["icao"] == icao:
            return dict(flight).copy()
    example_flight = new_flight
    example_flight["icao"] = icao
    return example_flight.copy()

def remove_flight(icao):
    if icao == None:
        return
    for flight in flights:
        if flight["icao"] == icao:
            flights.remove(flight)
            return

def update_flights(flight=None):
    global flights
    updated_flights = []

    if flight != None:
        icao = flight["icao"]
    else:
        icao = None
    remove_flight(icao)

    for i in range(len(flights)):
        if flights[i]["last_datetime"] > datetime.now() - timedelta(seconds=settings.MAX_FLIGHT_UPDATE_INTERVAL_IN_SECONDS):
            updated_flights.append(flights[i])

    if icao != None:
        flight["last_datetime"] = datetime.now()
        updated_flights.append(flight)

    flights = updated_flights

def prepare_value(old_value, new_value):
    if new_value == None or new_value == "":
        return old_value
    if isinstance(new_value, str):
        try:
            new_value = float(new_value)
            if new_value.is_integer():
                new_value = int(new_value)
        except:
            pass
    return new_value

def parse_sbs_message(msg):
    msg_parts = str(msg).replace("\n", "").replace(" ", "").split(",")
    if len(msg_parts) >= 22:
        icao = msg_parts[4]
        flight = get_flight(icao)
        flight["session_id"] = prepare_value(flight["session_id"], msg_parts[2])
        flight["aircraft_id"] = prepare_value(flight["aircraft_id"], msg_parts[3])
        flight["flight_id"] = prepare_value(flight["flight_id"], msg_parts[5])
        try:
            flight["last_datetime"] = prepare_value(flight["last_datetime"], parser.parse(f"{msg_parts[6]} {msg_parts[7]}"))
        except:
            flight["last_datetime"] = prepare_value(flight["last_datetime"], datetime.now())
        flight["callsign"] = prepare_value(flight["callsign"], msg_parts[10])
        flight["altitude"] = prepare_value(flight["altitude"], msg_parts[11])
        flight["ground_speed"] = prepare_value(flight["ground_speed"], msg_parts[12])
        flight["track"] = prepare_value(flight["track"], msg_parts[13])
        flight["latitude"] = prepare_value(flight["latitude"], msg_parts[14])
        flight["longitude"] = prepare_value(flight["longitude"], msg_parts[15])
        flight["vertical_rate"] = prepare_value(flight["vertical_rate"], msg_parts[16])
        flight["squawk"] = prepare_value(flight["squawk"], msg_parts[17])
        flight["alert_squawk_change"] = prepare_value(flight["alert_squawk_change"], msg_parts[18])
        flight["emergency_code"] = prepare_value(flight["emergency_code"], msg_parts[19])
        flight["spi_ident"] = prepare_value(flight["spi_ident"], msg_parts[20])
        flight["on_ground"] = prepare_value(flight["on_ground"], msg_parts[21])
        update_flights(flight)