import socket,os,sys
from _thread import *

BUF_SIZE=1024

def rcv_thread(s,a):
	while True:
		try:
			data = s.recv(BUF_SIZE).decode('utf-8')
			if data:
				print(data)
		except:
			break


def send_thread(s,a):
	while True:
		try:
			data=s.recv(BUF_SIZE).decode('utf-8')
			print(data)
			if data=="Get lost" or data=="Login attempts exceeded":
				s.close()
				sys.exit()
			cmd=""
			while cmd=="":
				cmd=input()
			s.send(cmd.encode('utf-8'))
			if cmd=="logout":
				s.close()
				sys.exit()
		except:
			s.close()
			break
			


s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
ip_address= '127.0.0.1'


s1=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s1.connect((ip_address,2501))
start_new_thread(rcv_thread , (s1,1))
#rcv_thread(s1,1)

port=int(sys.argv[1])
s.connect((ip_address,port))
send_thread(s,1)

s.close()
#print(data)

