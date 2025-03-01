from datetime import datetime, timedelta
import socket, threading, traceback
from settings import *
from models import *
# import raw_decoder
import sbs_decoder
import validator

flights = []
flights_instructions = {}

def raw_in_loop(sock):
    global flights, quit

    msg = sock.readline()

    if msg:
        if configuration["LOG_ALL_AIRCRAFT_MESSAGES"]:
            print(msg, end="")
        # raw_decoder.parse_raw_message(msg)
        # flights = raw_decoder.flights
    else:
        raise Exception("No messages")

def sbs_in_loop(sock):
    global flights, quit

    msg = sock.readline()

    if msg:
        if configuration["LOG_ALL_AIRCRAFT_MESSAGES"]:
            print(msg, end="")
        sbs_decoder.parse_sbs_message(msg)
        flights = sbs_decoder.flights
    else:
        raise Exception("No messages")

quit = False
sock = None
receiver_thread = None
validator_thread = None

def operate():
    global configuration, sock, quit

    if not quit:
        if str(configuration["FLIGHT_DATA_INPUT_MODE"]).upper() == "RAW-IN":
            if configuration["FLIGHT_DATA_PORT"] == 0:
                configuration["FLIGHT_DATA_PORT"] = RAW_IN_DEFAULT_PORT
            loop = raw_in_loop
        elif str(configuration["FLIGHT_DATA_INPUT_MODE"]).upper() == "SBS":
            if configuration["FLIGHT_DATA_PORT"] == 0:
                configuration["FLIGHT_DATA_PORT"] = SBS_DEFAULT_PORT
            loop = sbs_in_loop
        else:
            print("Wrong INPUT_MODE was selected.\n")
            quit = True

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((configuration["FLIGHT_DATA_HOST"], configuration["FLIGHT_DATA_PORT"]))
            sock = sock.makefile(mode="r")
            print(f"Connected to {configuration['FLIGHT_DATA_HOST']}:{configuration['FLIGHT_DATA_PORT']}\n")
        except:
            # print("Connection refused\n")
            return

    try:
        while not quit:
            loop(sock)

    except (ConnectionResetError, ConnectionAbortedError):
        print("Connection reset.\n")

    except KeyboardInterrupt:
        print("^C")
        quit = True

    except Exception as e:
        print(f"{str(type(e))}: {str(e)}\n{traceback.format_exc()}")

def keep_operating():
    global flights, flights_instructions, receiver_thread, quit

    with Session(db_engine) as session:
        try:
            flights_in_db = list(session.scalars(select(FlightInformation).where(FlightInformation.timestamp > datetime.now() - timedelta(seconds=configuration["INSTRUCTION_VALIDITY_TIME_AFTER_FLIGHT_IS_LOST_IN_SECONDS"])).order_by(FlightInformation.timestamp.desc())))

            flights_icao_addresses = []

            for flight in flights_in_db:
                if flight.icao not in flights_icao_addresses:
                    flights_instructions[flight.icao] = {
                        "id": flight.atc_instructions_id,
                        "timestamp": flight.timestamp
                    }
                    flights_icao_addresses.append(flight.icao)

        except Exception as e:
            print(f"{str(type(e))}: {str(e)}\n{traceback.format_exc()}")

        while not quit:
            current_timestamp = datetime.now()

            for flight_icao in flights_instructions.copy().keys():
                if flights_instructions[flight_icao]["timestamp"] < current_timestamp - timedelta(seconds=configuration["INSTRUCTION_VALIDITY_TIME_AFTER_FLIGHT_IS_LOST_IN_SECONDS"]):
                    flights_instructions.pop(flight_icao)

            flights_instructions_copy = flights_instructions.copy()

            while current_timestamp > datetime.now() - timedelta(seconds=configuration["RADAR_FLIGHTS_UPDATE_TIME_IN_SECONDS"] / 2):
                if flights_instructions_copy != flights_instructions or quit:
                    break

            try:
                flights_in_db = list(session.scalars(select(FlightInformation).where(FlightInformation.timestamp > datetime.now() - timedelta(seconds=0.8 * configuration["MAX_FLIGHT_UPDATE_INTERVAL_BEFORE_CONSIDERED_AS_LOST_IN_SECONDS"])).order_by(FlightInformation.timestamp.desc())))

                updated_flights = []
                flights_icao_addresses = []

                for flight in flights_in_db:
                    if flight.icao not in flights_icao_addresses:
                        updated_flights.append(flight)
                        flights_icao_addresses.append(flight.icao)

                flights_in_db = updated_flights
                updated_flights = []

                atc_instructions_in_db = list(session.scalars(select(InstructionsFromATC).where(InstructionsFromATC.flight_last_seen_at > datetime.now() - timedelta(seconds=configuration["INSTRUCTION_VALIDITY_TIME_AFTER_FLIGHT_IS_LOST_IN_SECONDS"])).order_by(InstructionsFromATC.timestamp.desc())))

                flights_copy = flights.copy()

                for i in range(len(flights_copy)):
                    if flights_copy[i]["last_datetime"] > datetime.now() - timedelta(seconds=configuration["MAX_FLIGHT_UPDATE_INTERVAL_BEFORE_CONSIDERED_AS_LOST_IN_SECONDS"]):
                        temp_flight = FlightInformation.from_flight_dict(flights_copy[i])

                        flights_copy[i]["instructions"] = None

                        if temp_flight.icao in flights_instructions.keys():
                            temp_flight.atc_instructions_id = flights_instructions[temp_flight.icao]["id"]

                        if temp_flight.atc_instructions_id is not None:
                            for instruction in atc_instructions_in_db:
                                if instruction.id == temp_flight.atc_instructions_id:
                                    instruction.flight_last_seen_at = temp_flight.timestamp
                                    validator.validate_instructions(flights_copy[i], instruction)
                                    break

                        flight_not_found = True
                        for flight in flights_in_db:
                            if temp_flight == flight:
                                flight_not_found = False
                                # flights_instructions.pop(temp_flight.icao, None)
                                break

                        if flight_not_found:
                            session.add(temp_flight)

                        updated_flights.append(flights_copy[i])

                flights = updated_flights
                session.commit()

                if not receiver_thread.is_alive():
                    receiver_thread = threading.Thread(target=operate, daemon=True)
                    receiver_thread.start()

            except Exception as e:
                print(f"{str(type(e))}: {str(e)}\n{traceback.format_exc()}")

def start():
    global receiver_thread, validator_thread, quit
    quit = False
    receiver_thread = threading.Thread(target=operate, daemon=True)
    receiver_thread.start()
    validator_thread = threading.Thread(target=keep_operating)
    validator_thread.start()

def stop():
    global quit, sock
    quit = True
    try:
        sock.close()
    except:
        pass
    # print(flights)

def restart():
    global receiver_thread, validator_thread
    stop()
    while receiver_thread.is_alive() or validator_thread.is_alive():
        pass
    start()

if __name__ == "__main__":
    operate()