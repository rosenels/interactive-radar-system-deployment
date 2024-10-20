from datetime import datetime, timedelta
from dateutil import parser

MAX_FLIGHT_UPDATE_INTERVAL_IN_SECONDS = 10

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
    "on_ground": None
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
        if flights[i]["last_datetime"] > datetime.now() - timedelta(seconds=MAX_FLIGHT_UPDATE_INTERVAL_IN_SECONDS):
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

def parse_sbs_msg(msg):
    msg = str(msg).replace("\n", "").split(",")
    icao = msg[4]
    flight = get_flight(icao)
    flight["session_id"] = prepare_value(flight["session_id"], msg[2])
    flight["aircraft_id"] = prepare_value(flight["aircraft_id"], msg[3])
    flight["flight_id"] = prepare_value(flight["flight_id"], msg[5])
    flight["last_datetime"] = prepare_value(flight["last_datetime"], parser.parse(f"{msg[6]} {msg[7]}"))
    flight["callsign"] = prepare_value(flight["callsign"], msg[8])
    flight["altitude"] = prepare_value(flight["altitude"], msg[9])
    flight["ground_speed"] = prepare_value(flight["ground_speed"], msg[10])
    flight["track"] = prepare_value(flight["track"], msg[11])
    flight["latitude"] = prepare_value(flight["latitude"], msg[12])
    flight["longitude"] = prepare_value(flight["longitude"], msg[13])
    flight["vertical_rate"] = prepare_value(flight["vertical_rate"], msg[14])
    flight["squawk"] = prepare_value(flight["squawk"], msg[15])
    flight["alert_squawk_change"] = prepare_value(flight["alert_squawk_change"], msg[16])
    flight["emergency_code"] = prepare_value(flight["emergency_code"], msg[17])
    flight["spi_ident"] = prepare_value(flight["spi_ident"], msg[18])
    flight["on_ground"] = prepare_value(flight["on_ground"], msg[19])
    update_flights(flight)