import socket
import threading


HEADER : int = 64
PORT : int = 5050 #* Port the servers listens on
SERVER = socket.gethostbyname(socket.gethostname()) #* IP from the server
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #* Creates a TCP/IP IPv4 socket
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #* Allows the port to be reused after restart
server.bind(ADDR) #* Binds socket to adress

#* List of all active connections
clients = []
#* Locks to safely modify the client list
clients_lock = threading.Lock()

#* Loops till the entire message arrives
def recv_all(conn, length):
    data = b"" 
    while len(data) < length:
        packet = conn.recv(length - len(data))
        if not packet:
            return None
        data += packet
    return data

#*
def broadcast(message, sender):
    with clients_lock:
        for client in clients:
            if client != sender:
                try:
                    client.sendall(message)
                except Exception:
                    clients.remove(client) #* Removes offline clients

#*
def handle_client(conn, addr):
    ip, port = addr
    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except socket.herror:
        hostname = ip
    print(f"[NEW CONNECTION] {hostname} connected.")

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

            print(f"[{hostname}] {decoded_msg}")

            broadcast(msg, conn)
    except Exception as e:
        print(f"[ERROR] {hostname}: {e}")
    finally: 
        with clients_lock:
            if conn in clients:
                clients.remove(conn)
        conn.close()
        print(f"[DISCONNECTED] {hostname}")

#* start server and check for connections
def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept() #* checks for new connections
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

#* start server
print (f"[STARTING] server is starting...")
#* close server without errors
try:
    start()
except KeyboardInterrupt:
        print("\n[STOPPING] Shutting down server...")
        with clients_lock:
            for client in clients:
                try:
                    client.close()
                except Exception:
                    pass
            clients.clear()
        server.close()
        print("[STOPPED] Server shut down.")