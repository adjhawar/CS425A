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
	c.send(b"Welcome to the Server")
	global send_queue
	msg = input()
	while True:
		c.send(msg.encode("utf-8"))
		if(msg == "exit"):	
			break
		msg = input()
			
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
s.close()
