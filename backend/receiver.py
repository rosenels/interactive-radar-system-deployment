from datetime import datetime, timedelta
import socket, threading, time, traceback
from settings import *
from models import *
# import raw_decoder
import sbs_decoder

flights = []
flights_instructions = {}

def raw_in_loop(sock):
    global flights, quit

    msg = sock.readline()

    if msg:
        print(msg, end="")
        # raw_decoder.parse_raw_message(msg)
        # flights = raw_decoder.flights
    else:
        raise Exception("No messages")

def sbs_in_loop(sock):
    global flights, quit

    msg = sock.readline()

    if msg:
        print(msg, end="")
        sbs_decoder.parse_sbs_message(msg)
        flights = sbs_decoder.flights
    else:
        raise Exception("No messages")

quit = False
sock = None
receiver_thread = None

def operate():
    global FLIGHT_DATA_PORT, sock, quit

    if not quit:
        if FLIGHT_DATA_INPUT_MODE.upper() == "RAW-IN":
            if FLIGHT_DATA_PORT == 0:
                FLIGHT_DATA_PORT = RAW_IN_DEFAULT_PORT
            loop = raw_in_loop
        elif FLIGHT_DATA_INPUT_MODE.upper() == "SBS":
            if FLIGHT_DATA_PORT == 0:
                FLIGHT_DATA_PORT = SBS_DEFAULT_PORT
            loop = sbs_in_loop
        else:
            print("Wrong INPUT_MODE was selected.\n")
            quit = True

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((FLIGHT_DATA_HOST, FLIGHT_DATA_PORT))
            sock = sock.makefile(mode="r")
            print("Connected to %s:%d\n" % (FLIGHT_DATA_HOST, FLIGHT_DATA_PORT))
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
        while not quit:
            time.sleep(RADAR_FLIGHTS_UPDATE_TIME_IN_SECONDS / 2)

            try:
                flights_in_db = list(session.scalars(select(FlightInformation).where(FlightInformation.timestamp > datetime.now() - timedelta(seconds=0.8 * MAX_FLIGHT_UPDATE_INTERVAL_IN_SECONDS)).order_by(FlightInformation.timestamp.desc())))

                updated_flights = []
                flights_icao_addresses = []

                for flight in flights_in_db:
                    if flight.icao not in flights_icao_addresses:
                        updated_flights.append(flight)
                        flights_icao_addresses.append(flight.icao)

                flights_in_db = updated_flights
                updated_flights = []

                atc_instructions_in_db = list(session.scalars(select(InstructionsFromATC).where(InstructionsFromATC.timestamp > datetime.now() - timedelta(seconds=INSTRUCTION_VALIDITY_TIME_AFTER_FLIGHT_IS_LOST_IN_SECONDS)).order_by(InstructionsFromATC.timestamp.desc())))

                for i in range(len(flights)):
                    if flights[i]["last_datetime"] > datetime.now() - timedelta(seconds=MAX_FLIGHT_UPDATE_INTERVAL_IN_SECONDS):
                        temp_flight = FlightInformation.from_flight_dict(flights[i])

                        # flight_not_found = True
                        # for flight in flights_in_db:
                        #     if temp_flight == flight:
                        #         flight_not_found = False
                        #         break

                        # if flight_not_found:
                        flights[i]["instructions"] = None

                        if temp_flight.icao in flights_instructions.keys():
                            temp_flight.atc_instructions_id = flights_instructions[temp_flight.icao]

                        if temp_flight.atc_instructions_id != None:
                            for instruction in atc_instructions_in_db:
                                if instruction.id == temp_flight.atc_instructions_id:
                                    # instruction.timestamp = datetime.now()
                                    flights[i]["instructions"] = {}
                                    flights[i]["instructions"]["id"] = instruction.id
                                    flights[i]["instructions"]["atc_user_id"] = instruction.atc_user_id
                                    flights[i]["instructions"]["atc_user_fullname"] = instruction.atc_user_fullname
                                    flights[i]["instructions"]["altitude"] = instruction.altitude
                                    flights[i]["instructions"]["ground_speed"] = instruction.ground_speed
                                    flights[i]["instructions"]["track"] = instruction.track
                                    flights[i]["instructions"]["vertical_rate"] = instruction.vertical_rate
                                    flights[i]["instructions"]["timestamp"] = instruction.timestamp
                                    break

                        flight_not_found = True
                        for flight in flights_in_db:
                            if temp_flight == flight:
                                flight_not_found = False
                                flights_instructions.pop(temp_flight.icao, None)
                                break

                        if flight_not_found:
                            session.add(temp_flight)

                        updated_flights.append(flights[i])

                flights = updated_flights
                session.commit()

                if not receiver_thread.is_alive():
                    receiver_thread = threading.Thread(target=operate)
                    receiver_thread.start()

            except Exception as e:
                print(f"{str(type(e))}: {str(e)}\n{traceback.format_exc()}")

def start():
    global receiver_thread, quit
    quit = False
    receiver_thread = threading.Thread(target=operate)
    receiver_thread.start()
    validator_thread = threading.Thread(target=keep_operating)
    validator_thread.start()
    time.sleep(1) # wait 1 second because in this period it is possible: quit = True
    if quit:
        exit()

def stop():
    global receiver_thread, quit
    quit = True
    try:
        sock.close()
        receiver_thread.join()
    except:
        pass
    # print(flights)

def restart():
    stop()
    start()

if __name__ == "__main__":
    operate()