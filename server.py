import socket
import threading

HEADER = 10
IP = "127.0.0.1"
PORT = 1234
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))

sockets = [server_socket]
clients = {}

def handleClient(client_socket, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        msg = receive_data(client_socket)
        broadcast_message(client_socket, msg)

    client_socket.close()
    sockets.remove(client_socket)
    del clients[client_socket]

def broadcast_message(client_socket, msg):

    user = clients[client_socket]

    for socket in clients:
        socket.send(user["header"] + user["data"] + msg["header"] + msg["data"])

def receive_data(client_socket):
    try:
        msg_header = client_socket.recv(HEADER)
        if not msg_header:
            return False

        msg_len = int(msg_header.decode(FORMAT))

        return {"header": msg_header, "data": client_socket.recv(msg_len)}

    except:
        return False

def start():
    server_socket.listen()
    print(f"[LISTENING] Server is listening on {(IP, PORT)}")

    while True:
        client_socket, client_addr = server_socket.accept()
        username = receive_data(client_socket)
        print("USERNAME:", username)
        if not username:
            continue

        sockets.append(client_socket)
        clients[client_socket] = username

        thread = threading.Thread(target=handleClient, args=(client_socket, client_addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

print("[STARTING] server is starting...")
start()

