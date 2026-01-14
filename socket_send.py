
"""
import socket

SOCKET_IP = "localhost"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((f"{SOCKET_IP}", 8766))

server.listen(5)

while True:
    client, addr = server.accept()
    print(f"Connection from {addr} has been established!")

"""


import json

with open("socket_temp/robot_response.json", "r") as json_file:
    x = json.load(json_file)
print(x.get("text"))
x["text"] = "test"

with open("socket_temp/robot_response.json", "w") as json_file:
    json.dump(x, json_file, indent=4)
