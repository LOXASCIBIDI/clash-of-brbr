import socket
import threading

HOST = "0.0.0.0"
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []

print("сервер запущен")

def broadcast(msg, sender):
    for c in clients:
        if c != sender:
            try:
                c.send(msg)
            except:
                pass


def handle_client(conn, addr):
    global clients

    print("игрок подключился:", addr)
    clients.append(conn)

    if len(clients) == 2:
        print("найден матч")
        for c in clients:
            c.send("FOUND".encode())

    while True:
        try:
            data = conn.recv(1024)

            if not data:
                break

            print("NET:", data.decode())

            broadcast(data, conn)

        except:
            break

    print("игрок отключился:", addr)

    if conn in clients:
        clients.remove(conn)

    conn.close()

    if len(clients) == 1:
        try:
            clients[0].send("OPPONENT_LEFT".encode())
        except:
            pass


while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()