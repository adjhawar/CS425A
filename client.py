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

def rcv_thread(s,a):
	#print("in rcv")
	while True:
		try:
			data = s.recv(BUF_SIZE).decode('utf-8')
			if data:
				print(data)
		except:
			continue
	#s.close()

def send_thread(s,a):
	while True:
		try:
			data=s.recv(BUF_SIZE).decode('utf-8')
			print(data)
			if data=="Get lost":
				sys.exit()
			cmd=input()
			s.send(cmd.encode('utf-8'))
			if cmd=="logout":
				sys.exit()
		except:
			continue

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
ip_address= '127.0.0.1'
port=int(sys.argv[1])
s.connect((ip_address,port))
start_new_thread(send_thread,(s,1))
s1=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s1.connect((ip_address,2500))
start_new_thread(rcv_thread , (s1,1))

#s.close()
#print(data)

