#    file containing the high level socket wrappers 
#    to allow for easy use of the encrypted sockets

#    This module is currently undergoing a reworking to use asyncioo
#    the end goal is create full duplex event-loop based sockets for
#    use inside a distributed network.

import socket
import sys
import asyncio
from concurrent.futures import ThreadPoolExecutor

#might be removed if we handle libsodium natively:
import libnacl
from libnacl import secret

class SubscriberSock:
#       This socket will handle a duplex socket through a subscriber based method.
#       internal connections:
#           -> multiple connections added to the dictionary (subscribers) get identical updates of incoming messages
#       external connections:
#           -> all messages from internal senders integrated together and broadcast out through the socket
#           -> this could probably be made more effecient in the future with a queue based structure, but for now
#               is based on Futures passed through run_in_executor(), which may cause the socket to block if flooded
#       
#
#       self.inHost = host to open the listening server on
#       self.inPort = port to open the listening server with
#       self.outHost = remote host to connect to and send encrypted data
#       self.outPort = remote port to connect to and send encrypted data
#       self.box = pre-initialized encryption box provided by libnacl
#
#       ## TODO:
#           -> make sure that we can control the sockets from inside the program, not just hope the connection dies nicely...
#           -> seperate open into different methods (need multiprocessing)
#           -> allow for different input/output types. i.e. pipes, AF_UNIX ... (need IPC?)

    def __init__(self, sockType=socket.AF_INET, inHost=None, inPort=None, exHost=None, exPort=None, outHost=None, outPort=None, box=None):
        self.sockType = sockType
        self.inHost = inHost
        self.inPort = inPort
        self.exHost = exHost
        self.exPort = exPort
        self.outHost = outHost
        self.outPort = outPort
        self.box = box
        self.closed = True
        self.inConn = None
        self.executor = ThreadPoolExecutor(3)
        self.index = 0 #should eventuall define a maximum subscriber and throw a corresponding error

        #for now, all subscibers have the same permissions, this can / should be changed with authentication
        self.internalSubscribers = dict() 

    
    async def internal_conn_recieved(self, reader, writer):
        loop = asyncio.get_running_loop()
        i = self.index
        self.index += 1
        self.internalSubscribers[i] = writer
        while(not reader.at_eof()):
            data = await reader.readline()
            loop.run_in_executor(self.executor, self.encrypt_and_send_external(data))


    async def external_conn_recieved(self, reader, writer):
        loop = asyncio.get_running_loop()
        while(not reader.at_eof()):
            cdata = await reader.read(-1)
            loop.run_in_executor(self.executor, self.decrypt_and_send_internal(cdata))

    # this can throw errors because of the timeout, they will be internally caught by the executor, we should at some point actually
    # them and not just let them be as they could contain mission critical data.
    def encrypt_and_send_external(self, data):
        cdata = self.box.encrypt(data);
        outSock = socket.socket(self.sockType, socket.SOCK_STREAM)
        outSock.settimeout(5) # setting a timeout so that we don't block the executor pool for a spotty connection
        outSock.connect((self.outHost,self.outPort))
        outSock.send(cdata)
        outSock.shutdown(socket.SHUT_RDWR)
        outSock.close()

    def decrypt_and_send_internal(self, cdata):
        data = self.box.decrypt(cdata)
        for writer in self.internalSubscribers.values():
            writer.write(data)
            
    async def open(self):
        loop = asyncio.get_running_loop()
        # create a default socket to bind to with arbitrary program
        internal_server_task = loop.create_task(asyncio.start_server(self.internal_conn_recieved, self.inHost, self.inPort))
        # create the external broadcasting server, the outgoing sock type (TCP / UDP) is arbitrary as far as this implementation is concerned
        external_server_task = loop.create_task(asyncio.start_server(self.external_conn_recieved, self.exHost, self.exPort))
        self.closed = False

        #loop.run_until_complete(asyncio.gather(internal_server_task, external_server_task))
        await asyncio.gather(internal_server_task, external_server_task)
        while(True):
            await asyncio.sleep(5)
            print("still running!")
        
        self.executor.shutdown(True)
        self.closed = True

    def start(self):
        asyncio.run(self.open())



class DecryptSock():
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


