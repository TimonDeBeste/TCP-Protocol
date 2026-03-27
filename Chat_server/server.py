import socket
import threading

HEADER: int = 64
PORT: int = 5050
SERVER = "192.168.100.102"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(ADDR)

clients = []
clients_lock = threading.Lock()


def recv_all(conn, length):
    data = b""
    while len(data) < length:
        packet = conn.recv(length - len(data))
        if not packet:
            return None
        data += packet
    return data


def broadcast(message):
    with clients_lock:
        for client in list(clients):
            try:
                client.sendall(message)
            except Exception:
                clients.remove(client)


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
            broadcast(header + msg)
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
    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.daemon = True
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Server is shutting down...")
    finally:
        with clients_lock:
            for client in clients:
                try:
                    client.close()
                except Exception:
                    pass
        server.close()
        print("[SHUTDOWN] Server closed.")


print("[STARTING] server is starting...")
start()
