from datetime import datetime, timedelta
import socket, threading, time
from settings import *
# import raw_decoder
import sbs_decoder

flights = []

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
    global PORT, sock, quit
    if INPUT_MODE.upper() == "RAW-IN":
        if PORT == 0:
            PORT = RAW_IN_DEFAULT_PORT
        loop = raw_in_loop
    elif INPUT_MODE.upper() == "SBS":
        if PORT == 0:
            PORT = SBS_DEFAULT_PORT
        loop = sbs_in_loop
    else:
        print("Wrong INPUT_MODE was selected.\n")
        quit = True

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((REMOTE_HOST, PORT))
        sock = sock.makefile(mode="r")
        print("Connected to %s:%d\n" % (REMOTE_HOST, PORT))
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

    except Exception:
        pass

def keep_operating():
    global flights, receiver_thread, quit
    while not quit:
        updated_flights = []
        for i in range(len(flights)):
            if flights[i]["last_datetime"] > datetime.now() - timedelta(seconds=MAX_FLIGHT_UPDATE_INTERVAL_IN_SECONDS):
                updated_flights.append(flights[i])
        flights = updated_flights

        if not receiver_thread.is_alive():
            receiver_thread = threading.Thread(target=operate)
            receiver_thread.start()

def start():
    global receiver_thread, quit
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
        receiver_thread.join()
    except:
        pass
    try:
        sock.close()
    except:
        pass
    # print(flights)

if __name__ == "__main__":
    operate()