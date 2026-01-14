import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 8766))
client.send(b"Hello, Server!")
print(client.recv(1024).decode())