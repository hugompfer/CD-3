import unittest
import socket
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8000


class TestStringMethods(unittest.TestCase):

    def setUp(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((SERVER_HOST, SERVER_PORT))

    def tearDown(self):
        self.client_socket.close()

    def testGET(self):
        """ test 200 OK in a get request"""
        msg = "GET / HTTP/1.1\n\n"
        self.client_socket.sendall(msg.encode())
        res = self.client_socket.recv(1024).decode()
        self.assertIn("200",res)

    def testNotFound(self):
        """ test 404 Not found in a get request"""
        msg = "GET /public/sdfs.html HTTP/1.1"
        self.client_socket.sendall(msg.encode())
        res = self.client_socket.recv(1024).decode()
        self.assertIn("404", res)

    def testBadRequest(self):
        """ test 400 Bad Request in a get request"""
        msg = "GET HTTP/1.1"
        self.client_socket.sendall(msg.encode())
        res = self.client_socket.recv(1024).decode()
        self.assertIn("400", res)

    def testForbidden(self):
        """ test 403 Forbidden in a get request"""
        msg = "GET /private/file.html HTTP/1.1"
        self.client_socket.sendall(msg.encode())
        res = self.client_socket.recv(1024).decode()
        self.assertIn("403", res)

    def testBadRequestFormated(self):
        """ test 400 Bad Request in a get request"""
        msg = "HTTP/1.1 /public/sdfs.html GET"
        self.client_socket.sendall(msg.encode())
        res = self.client_socket.recv(1024).decode()
        self.assertIn("400", res)

    def testPOSTData(self):
        """ test if the post response data return the json format"""
        msg = "POST / HTTP/1.1\nContent-Type: application/x-www-form-urlencoded\n\nname=oi&last=oi2&middle=oi3"
        self.client_socket.sendall(msg.encode())
        res = self.client_socket.recv(1024).decode()
        self.assertIn('{"name": "oi", "last": "oi2", "middle": "oi3"}', res)

    def testPOSTContentType(self):
        """ test if the post response content type return application/json"""
        msg = "POST / HTTP/1.1\nContent-Type: application/x-www-form-urlencoded\n\nname=oi&last=oi2&middle=oi3"
        self.client_socket.sendall(msg.encode())
        res = self.client_socket.recv(1024).decode()
        self.assertIn('Content-Type:application/json', res)

    def testPOSTBadRequest(self):
        """ test if the post response data return bad request"""
        msg = "POST / HTTP/1.1\nContent-Type: application/x-www-form-urlencoded\n\nname=oi&&&last=oi2&middle=oi3"
        self.client_socket.sendall(msg.encode())
        res = self.client_socket.recv(1024).decode()
        self.assertIn('400', res)


    def testHEAD(self):
        """ test 200 OK in a head request"""
        msg = "HEAD /public/ipsum.html HTTP/1.1"
        self.client_socket.sendall(msg.encode())
        res = self.client_socket.recv(1024).decode()
        self.assertIn("200", res)

    def testHEADNotFound(self):
        """ test 404 Not Found in a head request"""
        msg = "HEAD /public/dsa.html HTTP/1.1"
        self.client_socket.sendall(msg.encode())
        res = self.client_socket.recv(1024).decode()
        self.assertIn("404", res)

    def testHEADBadRequest(self):
        """ test 400 Bad Request in a head request"""
        msg = " /public/dsa.html HEAD HTTP/1.1"
        self.client_socket.sendall(msg.encode())
        res = self.client_socket.recv(1024).decode()
        self.assertIn("400", res)

    def testPUTForbidden(self):
        """ test 404 Not Found in a head request"""
        msg = "PUT /extras/put HTTP/1.1\n\ntime=20"
        self.client_socket.sendall(msg.encode())
        res = self.client_socket.recv(1024).decode()
        self.assertIn("403", res)

    def testDELETEForbidden(self):
        """ test 403 Forbidden in a delete request"""
        msg = "DELETE /extras/files/file.txt HTTP/1.1"
        self.client_socket.sendall(msg.encode())
        res = self.client_socket.recv(1024).decode()
        self.assertIn("403", res)

    def testLanguageParse(self):
        """ test if response data return default language"""
        msg = "GET /extras/translate HTTP/1.1\n\nola"
        self.client_socket.sendall(msg.encode())
        res = self.client_socket.recv(1024).decode()
        self.assertIn("ola", res)

    def testLanguageParse(self):
        """ test if response data return requested language"""
        msg = "GET /extras/translate HTTP/1.1\nAccept-Language: en-US\n\nola"
        self.client_socket.sendall(msg.encode())
        res = self.client_socket.recv(1024).decode()
        self.assertIn("hello", res)

    def testGifImage(self):
        """ test 200 OK in a get gif request"""
        msg = "GET /extras/gif.html HTTP/1.1"
        self.client_socket.sendall(msg.encode())
        res = self.client_socket.recv(1024).decode()
        self.assertIn("200", res)

    def testImageVideoImage(self):
        """ test 200 OK in a get audio/video request"""
        msg = "GET /extras/audio_video.html HTTP/1.1"
        self.client_socket.sendall(msg.encode())
        res = self.client_socket.recv(1024).decode()
        self.assertIn("200", res)

    def testConnectionClose(self):
        """ test if response data return to close the client connection"""
        msg = "GET /extras/audio_video.html HTTP/1.1\nConnection: Close"
        self.client_socket.sendall(msg.encode())
        res = self.client_socket.recv(1024).decode()
        self.assertIn("Connection:Close", res)

    def testBadRequestHTTP(self):
        """ test if response data return bad request"""
        msg = "GET /extras/audio_video.html HTTP/1.1\nConnection: Close\nfdsfsdfsdfsdfs"
        self.client_socket.sendall(msg.encode())
        res = self.client_socket.recv(1024).decode()
        self.assertIn("400", res)
