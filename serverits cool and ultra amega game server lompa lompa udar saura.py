import socket
import threading

HOST = "0.0.0.0"
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print("сервер запущен")

clients = []
lock = threading.Lock()


def broadcast(msg, sender):
    for c in clients:
        if c != sender:
            try:
                c.send(msg)
            except:
                pass


def handle_client(conn, addr):
    global clients

    print("подключился:", addr)

    with lock:
        if len(clients) >= 2:
            conn.close()
            return

        clients.append(conn)

        if len(clients) == 2:
            print("матч найден")
            for c in clients:
                try:
                    c.send("FOUND".encode())
                except:
                    pass

    while True:
        try:
            data = conn.recv(1024)

            if not data:
                break

            broadcast(data, conn)

        except:
            break

    print("отключился:", addr)

    with lock:
        if conn in clients:
            clients.remove(conn)

        for c in clients:
            try:
                c.send("OPPONENT_LEFT".encode())
                c.close()
            except:
                pass

        clients.clear()

    conn.close()


while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()