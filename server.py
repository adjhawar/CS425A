import socket
import os
import sys
from _thread import *

BUF_SIZE=1024
active_list=[]

#authenticates the username and password
def login(username,password):
	return b'1'

#register a new user
def register(s):
	return b'1'

def remove(c):
	if c in active_list:
		active_list.remove(c)
		

def send_msg(c,addr):
	global send_queue
	while True:
		if(not c.fileno()):
			continue	
		msgs =  send_queue[c.fileno()]
		while (len(msgs)):
			c.send(msgs.pop(0).encode("utf-8"))
			
			
def clientThread(c,addr):
	c.send(b"Welcome to the Server")
	flag=0
	while flag>=0:
		try:
			msg=c.recv(BUF_SIZE)
			if msg:
				print(msg)
			else:
				remove(c)
		except:
			continue


send_queue = {}

#AF_INET implies IPv4 and SOCK_STREAM implies TCP connection
port=int(sys.argv[1])
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

#binding the server to a port
s.bind(('127.0.0.1',port))
s.listen()
print("Server is listening")
while True:
	c,addr=s.accept()
	active_list.append(c)
	start_new_thread(send_msg,(c,addr))
	start_new_thread(clientThread, (c,addr))
s.close()
