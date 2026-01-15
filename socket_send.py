import socket

SOCKET_IP = "localhost"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((f"{SOCKET_IP}", 8766))

server.listen(5)

while True:
    client, addr = server.accept()
    print(f"Connection from {addr} has been established!")


