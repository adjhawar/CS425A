import socket,os,sys
from _thread import *

BUF_SIZE=1024

def authenticate(s):
	username=input()
	password=input()
	s.send(username.encode('utf-8'))
	s.send(password.encode('utf-8'))
	f=s.recv(8).decode('utf-8')
	return f

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
ip_address= '127.0.0.1'
port=int(sys.argv[1])
s.connect((ip_address,port))

def rcv_thread(s,a):
	#print("in rcv")
	while True:
		try:
			data = s.recv(1024).decode('utf-8')
			if data:
				print(data)
		except:
			continue
	#s.close()

start_new_thread(rcv_thread , (s,1))

flag=0
while flag>=0:
	try:
		'''data=s.recv(1024).decode('utf-8')
		if data:
			print(data)
		print("Enter the data")	'''
		data=input()
		s.send(data.encode('utf-8'))
	except:
		continue
s.close()
#print(data)

