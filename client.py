import socket

def authenticate(s):
	username=input()
	password=input()
	s.send(username.encode('utf-8'))
	s.send(password.encode('utf-8'))
	f=s.recv(8).decode('utf-8')
	return f

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print("Socket successfully created")

#reserving a port for the server
port=12345
s.connect(('127.0.0.1',port))
data=s.recv(1024).decode('utf-8')
print(data)
flag=authenticate(s)
if flag=="0":
	print("Authentication failed. Retry")
	s.close()
else:
	print("Continue")
s.close()
