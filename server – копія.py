import socket
import threading

HOST = "0.0.0.0"
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(2)

clients = []

print("Сервер запущен, ждём игроков...")

def handle_client(conn, addr):
    print("Игрок подключился:", addr)
    clients.append(conn)

    if len(clients) == 2:
        for c in clients:
            c.send("FOUND".encode())

    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break

            print("Юнит поставлен:", data)

            for c in clients:
                if c != conn:
                    c.send(data.encode())

        except:
            break

    clients.remove(conn)
    conn.close()
    print("Игрок отключился:", addr)

while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr)).start()
