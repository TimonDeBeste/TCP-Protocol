import socket
import threading


HEADER : int = 64
PORT : int = 5050 #* Port the servers listens on
SERVER = '192.168.100.102' #* IP from the server
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #* Creates a TCP/IP IPv4 socket
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #* Allows the port to be reused after restart
server.bind(ADDR) #* Binds socket to ip and port

#* List of all active connections
clients = []
#* Locks to safely modify the client list
clients_lock = threading.Lock()

def recv_all(conn, length):
    data = b"" 
    while len(data) < length:
        packet = conn.recv(length - len(data))
        if not packet:
            return None
        data += packet
    return data

def broadcast(message, sender):
    with clients_lock:
        for client in clients:
            if client != sender:
                try:
                    client.sendall(message)
                except Exception:
                    clients.remove(client) #* Removes offline clients

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    with clients_lock:
        clients.append(conn)

    try:
        while True:
            header = recv_all(conn, HEADER)
            if not header:
                break

            msg_length = int(header.decode(FORMAT).strip())
            
            msg = recv_all(conn, msg_length)
            if not msg:
                break
            decoded_msg = msg.decode(FORMAT)

            if decoded_msg == DISCONNECT_MESSAGE:
                break

            print(f"[{addr}] {decoded_msg}")

            broadcast(msg, conn)

    except Exception as e:
        print(f"[ERROR] {addr}: {e}")

    finally: 
        with clients_lock:
            if conn in clients:
                clients.remove(conn)
        conn.close()
        print(f"[DISCONNECTED] {addr}")


def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

#* start server
print ("[STARTING] server is starting...")
start()