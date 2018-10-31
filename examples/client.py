import socket
import libnacl
from libnacl import secret

# this will have to be tweaked in order to create a propper function to recieve data

HOST = "127.0.0.1"
PORT = 29292

box = libnacl.secret.SecretBox()
print("generated key: ", box.sk)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen()
conn, addr = sock.accept()
with conn:
    print("connection from: ", addr)
    while True:
        data = conn.recv(1024)
        if not data:
            break
        cdata = box.encrypt(data)
        print(cdata)
sock.close()
print("socket closed, quiting ...")
