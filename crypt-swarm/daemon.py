import socket
import libnacl
from libnacl import secret

# dummy port and ip for testing on LocalHost
HOST = "127.0.0.1"
PORT = 29292

# generate a secret key and print it out for the purpose of sharing
box = libnacl.secret.SecretBox()
print("generated key: ", box.sk)

# create a default socket to bind to with arbitrary program
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen()
conn, addr = sock.accept()
with conn:
    print("connection from: ", addr)
    while True:
        data = conn.recv(1024) #recieve standard bytes
        if not data:
            break
        cdata = box.encrypt(data) #encrypte the recieved data in a binary representation
        print(cdata) # print it out for refference
sock.close()
print("socket closed, quiting ...")
