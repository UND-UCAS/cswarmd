#    file containing the high level socket wrappers 
#    to allow for easy use of the encrypted sockets

import socket
import sys

#might be removed if we handle libsodium natively:
import libnacl
from libnacl import secret

class EncryptSock:
#        This object handles the encryption of incoming messages, and outputs them to an arbitrary host,port tuple
#
#        self.inHost = host to open the listening server on
#        self.inPort = port to open the listening server with
#        self.outHost = remote host to connect to and send encrypted data
#        self.outPort = remote port to connect to and send encrypted data
#        self.box = pre-initialized encryption box provided by libnacl
#
#        ## TODO:
#            -> make sure that we can control the sockets from inside the program, not just hope the connection dies nicely...
#            -> seperate open into different methods (need multiprocessing)
#            -> allow for different input/output types. i.e. pipes, AF_UNIX ... (need IPC?)

    def __init__(self, sockType=socket.AF_INET, inHost=None, inPort=None, outHost=None, outPort=None, box=None):
        self.sockType = sockType
        self.inHost = inHost
        self.inPort = inPort
        self.outHost = outHost
        self.outPort = outPort
        self.box = box
        self.closed = True
        self.inConn = None

    def open(self):
        # create a default socket to bind to with arbitrary program
        inSock = socket.socket(self.sockType, socket.SOCK_STREAM)
        inSock.bind((self.inHost, self.inPort))
        inSock.listen(1)

        self.closed = False
        outSock = socket.socket(self.sockType, socket.SOCK_STREAM)

        conn, addr = inSock.accept()
        with conn:
            self.inConn = addr
            outSock.connect((self.outHost,self.outPort))
            while True:
                data = conn.recv(1024) #recieve standard bytes
                if not data:
                    break
                cdata = self.box.encrypt(data) #encrypte the recieved data in a binary representation
                outSock.sendall(cdata)
                #print(cdata) # print it out for refference
        self.inConn = None
        inSock.shutdown(socket.SHUT_RDWR)
        inSock.close()
        outSock.shutdown(socket.SHUT_RDWR)
        outSock.close()
        self.closed = True

class DecryptSock:
    
#        This object handles the decryption of incoming messages, and hosts them to an arbitrary host,port tuple
#
#        self.inHost = host to open the listening server on
#        self.inPort = port to open the listening server with
#        self.outHost = remote host to connect to and send encrypted data
#        self.outPort = remote port to connect to and send encrypted data
#        self.box = pre-initialized encryption box provided by libnacl
#
#        ## TODO:
#            -> make sure that we can control the sockets from inside the program, not just hope the connection dies nicely...
#            -> seperate open into different methods (need multiprocessing)
#            -> allow for different input/output types. i.e. pipes, AF_UNIX ... (need IPC?)
   

    def __init__(self, sockType=socket.AF_INET, inHost=None, inPort=None, outHost=None, outPort=None, box=None):
        self.sockType = sockType
        self.inHost = inHost
        self.inPort = inPort
        self.outHost = outHost
        self.outPort = outPort
        self.box = box
        self.closed = True
        self.inConn = None

    def open(self):
        # create a default socket to bind to with arbitrary program
        inSock = socket.socket(self.sockType, socket.SOCK_STREAM)
        inSock.bind((self.inHost, self.inPort))
        inSock.listen(1)

        self.closed = False
        outSock = socket.socket(self.sockType, socket.SOCK_STREAM)

        conn, addr = inSock.accept()
        with conn:
            self.inConn = addr
            outSock.connect((self.outHost,self.outPort))
            while True:
                cdata = conn.recv(1024) #recieve standard bytes
                if not cdata:
                    break
                data = self.box.decrypt(cdata) #encrypte the recieved data in a binary representation
                outSock.sendall(data)
                #print(cdata) # print it out for refference
        self.inConn = None
        inSock.shutdown(socket.SHUT_RDWR)
        inSock.close()
        outSock.shutdown(socket.SHUT_RDWR)
        outSock.close()
        self.closed = True


