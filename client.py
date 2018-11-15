import socket,os,sys

BUF_SIZE=1024

def authenticate(s):
	username=input()
	password=input()
	s.send(username.encode('utf-8'))
	s.send(password.encode('utf-8'))
	f=s.recv(8).decode('utf-8')
	return f

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
ip_address=sys.argv[1]
port=int(sys.argv[2])
s.connect((ip_address,port))

flag=0
while flag>=0:
	try:
		data=s.recv(1024).decode('utf-8')
		if data:
			print(data)
		print("Enter the data")	
		data=input()
		s.send(data.encode('utf-8'))
	except:
		continue
s.close()
print(data)

