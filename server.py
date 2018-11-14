import socket

def authenticate(username,password):
	return b'1'

#AF_INET implies IPv4 and SOCK_STREAM implies TCP connection
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print("Socket successfully created")

#reserving a port for the server
port=12345
s.bind(('127.0.0.1',port))
print("Socket bound to %s"%port)

s.listen()
print("Server is listening")

while True:
	c,addr=s.accept()
	print("connection request from ",addr)
	c.send(b'Enter your username and password')
	username=c.recv(1024).decode('utf-8')
	password=c.recv(1024).decode('utf-8')
	f=authenticate(username,password)
	c.send(f)
	c.close()
