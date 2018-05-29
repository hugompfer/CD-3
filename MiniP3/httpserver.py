
from HttpHandler import HtppHandler
import socket
import threading
from threading import Timer

class HttpServer:

    def __init__(self):
        self.serverPort=8000
        self.serverHost='0.0.0.0'
        self.serverSocket=self.incializeServerSocket()
        self.handler=HtppHandler()

    """Method to create the server socket correctly"""
    def incializeServerSocket(self):
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.bind((self.serverHost, self.serverPort))
        serverSocket.listen(1)
        return serverSocket

    """Method to close client connection"""
    def closeConnection(self,clientConnection):
        clientConnection.close()

    """Method to handle the request from clients"""
    def handle_request(self,clientConnection,clientAdress):
        try:
            connected=True
            while connected:
                # Handle client request
                timer=Timer(self.handler.timeout, self.closeConnection, (clientConnection,))
                timer.start()
                request = clientConnection.recv(1024).decode()
                timer.cancel()
                if(request!=''):
                    print(request)
                    response,connection = self.handler.handleRequest(request, clientAdress)
                    clientConnection.sendall(response)
                    if 'Close' in connection:
                        break
            clientConnection.close()
            connected = False
        except :
            connected=False

    """Method to start the server"""
    def start(self):
        try:
        # Create socket
            print('Listening on port %s ...' % self.serverPort)
            while True:
                # Wait for client connections
                clientConnection, clientAddress = self.serverSocket.accept()
                print('entrou')
                threadUser = threading.Thread(target=self.handle_request,
                                              args=(clientConnection,clientAddress[0]))
                threadUser.start()

            # Close socket
            self.serverSocket.close()
        except:
            self.serverSocket.close()
