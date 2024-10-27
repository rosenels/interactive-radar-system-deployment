import socket, threading
# import raw_decoder
import sbs_decoder

REMOTE_HOST = "localhost"
PORT = 0 # 0 means default port for the selected type input
RAW_IN_PORT = 30002
SBS_PORT = 30003

MODE = "sbs" # "raw-in" or "sbs"

flights = []

def raw_in_loop(sock):
    global flights, quit
    try:
        msg = sock.readline(10)
    except:
        msg = None

    if msg:
        print(msg, end="")
        # raw_decoder.parse_raw_message(msg)
        # flights = raw_decoder.flights
    else:
        print("Connection gone.\n")
        quit = True

def sbs_in_loop(sock):
    global flights, quit
    try:
        msg = sock.readline()
    except:
        msg = None

    if msg:
        print(msg, end="")
        sbs_decoder.parse_sbs_message(msg)
        flights = sbs_decoder.flights
    else:
        print("Connection gone.\n")
        quit = True

quit = False
sock = None
receiver_thread = None

def operate():
    global PORT
    if MODE.upper() == "RAW-IN":
        if PORT == 0:
            PORT = RAW_IN_PORT
        loop = raw_in_loop
    elif MODE.upper() == "SBS":
        if PORT == 0:
            PORT = SBS_PORT
        loop = sbs_in_loop
    else:
        print("Wrong MODE was selected.\n")
        exit(1)

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((REMOTE_HOST, PORT))
        sock = sock.makefile(mode="r")
        print("Connected to %s:%d\n" % (REMOTE_HOST, PORT))
    except:
        print("Connection refused\n")
        exit(1)

    global quit
    try:
        while not quit:
            loop(sock)

    except (ConnectionResetError, ConnectionAbortedError):
        print("Connection reset.\n")
        quit = True

    except KeyboardInterrupt:
        print("^C")
        quit = True

def start():
    global receiver_thread
    receiver_thread = threading.Thread(target=operate)
    receiver_thread.start()

def stop():
    global receiver_thread, quit
    quit = True
    receiver_thread.join()
    try:
        sock.close()
    except:
        pass
    print(flights)

if __name__ == "__main__":
    operate()