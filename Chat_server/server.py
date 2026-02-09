import socket 
import threading

PORT = 8080
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)