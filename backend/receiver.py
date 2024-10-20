import socket
from sbs_decoder import *

REMOTE_HOST = "localhost"
PORT  = 0 # 0 means default port for the selected type input
RAW_IN_PORT = 30002
SBS_PORT = 30003

MODE = "sbs" # "raw-in" or "sbs"

def raw_in_loop(sock):
    global quit
    try:
        msg = sock.readline(10)
    except:
        msg = None

    if msg:
        print(msg, end="")
    else:
        print("Connection gone.\n")
        quit = True

def sbs_in_loop(sock):
    global quit
    try:
        msg = sock.readline()
    except:
        msg = None

    if msg:
        print(msg, end="")
        parse_sbs_msg(msg)
    else:
        print("Connection gone.\n")
        quit = True

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

quit = False

try:
    while not quit:
        loop(sock)

except (ConnectionResetError, ConnectionAbortedError):
    print("Connection reset.\n")
    quit = True

except KeyboardInterrupt:
    print("^C")
    quit = True

sock.close()
print(flights)