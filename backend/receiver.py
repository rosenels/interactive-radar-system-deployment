import socket, threading
# import raw_decoder
import sbs_decoder

MODE = "sbs" # "raw-in" or "sbs"

REMOTE_HOST = "localhost"
PORT = 0 # 0 means the default port for the selected input mode
RAW_IN_DEFAULT_PORT = 30002
SBS_DEFAULT_PORT = 30003

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
    global PORT, quit
    if MODE.upper() == "RAW-IN":
        if PORT == 0:
            PORT = RAW_IN_DEFAULT_PORT
        loop = raw_in_loop
    elif MODE.upper() == "SBS":
        if PORT == 0:
            PORT = SBS_DEFAULT_PORT
        loop = sbs_in_loop
    else:
        print("Wrong MODE was selected.\n")
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
        # quit = True

    except KeyboardInterrupt:
        print("^C")
        quit = True

    except Exception:
        pass

def keep_operating():
    global receiver_thread, quit
    while not quit:
        if not receiver_thread.is_alive():
            receiver_thread = threading.Thread(target=operate)
            receiver_thread.start()

def start():
    global receiver_thread, quit
    receiver_thread = threading.Thread(target=operate)
    receiver_thread.start()
    validator_thread = threading.Thread(target=keep_operating)
    validator_thread.start()
    if quit:
        exit()

def stop():
    global receiver_thread, quit
    quit = True
    receiver_thread.join()
    try:
        sock.close()
    except:
        pass
    # print(flights)

if __name__ == "__main__":
    operate()