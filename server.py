import socket
import os
import sys
import queue
from threading import Thread
from _thread import *
import pandas as pd
import numpy as np

#1.Login
#2.Register
#3.Send
#4.Broadcast to group of users
#5.Broadcast to all users
#0.Logout 

BUF_SIZE=1024
active_list=[]
queues={}
user_fd={}
threads=[]
#authenticates the username and password
def login(user,password):
	df=pd.read_csv("user.csv")
	i=df.loc[df['Username'] == user]
	if df['Password'][i]==password:
		return 1
	elif user in active_user:
		return 0
	else:
		return 0

#register a new user
def register(name,user,password):
	df=pd.read_csv("user.csv")
	if df['Username']==user:
		return 0
	else:
		df.loc[-1]=[name,user,password]
		df.index=df.index+1
		df.to_csv("user.csv",index=False)
		return 1

def remove(c):
	if c in active_list:
		active_list.remove(c)
      
class clientReceive(Thread):
	def __init__(self,socket,ip,port):
		Thread.__init__(self)
		self.socket=socket
		self.ip=ip
		self.port=port
	
	def run(self):
		s=self.socket
		fd=s.fileno()
		s.send(b"Welcome to the Server\n1.Login\n2.Register\nAny other key to Logout")
		username=""
		result=0
		while True:
			try:
				msg=s.recv(BUF_SIZE).decode('utf-8')
				words=msg.split(" ")
				cmd=words[0]
				if cmd=="login" and result==0:
					username=words[1]
					result=login(words[1],words[2])
					if result:
						s.send(b"Login successful")
						active_user.append(username)
						#add mapping from username to fd
				elif cmd=="register" and result==0:
					username=words[2]
					result=register(words[1],words[2],words[3])
					if result:
						s.send(b"Registration successful")
						active_user.append(username)
						#add mapping from username to fd
				elif result==1:
					if cmd=="online":
						msg=""
						for p in active_user:
							if p!=username:
								p=msg+" "+p
						s.send(msg.encode('utf-8'))
					elif cmd=="send":
						receiver=words[1]
						msg=username+">>"
						for i in words[2:]:
							msg=msg+" "+i
					elif cmd=="broadcast":
						msg=username+">>"
						for i in words[2:]:
							msg=msg+" "+i
						if words[1]=="all":
							for p in active_user:
								if p!=username:
									#add to the respective users' shared queue
									print(p)
						else:
							receivers=words[1].split(",")
							for receiver in receivers:
								if receiver in active_user:
									#add to the respective users shared queue
									print("active",receiver)
								else:
									#write to his respective file
									print("inactive",receiver)
					elif cmd=="logout":
						#remove the user
						print("logout",username)
					elif cmd=="inbox":
						print("Inbox requested")
					else:
						s.send(b"Enter a valid command")
				else:
					s.send(b"Get lost")
					sys.exit()					
			except:
				continue

def send_msg(c,addr):
	global queues
	while True:
		if not addr:
			continue
		msgs = queues[addr]
		while(len(msgs)):
			c.send(msgs.pop(0).encode("utf-8"))
							
#AF_INET implies IPv4 and SOCK_STREAM implies TCP connection
port=int(sys.argv[1])
#creates the first socket where server only receives
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(('127.0.0.1',port))
s.listen()
s1=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s1.bind(('127.0.0.1',2500))
s1.listen()
print("Server is listening")
while True:
	c,addr=s.accept()
	q=queue.Queue()
	queues[c.fileno()]=q
	thread1=clientReceive(c,'127.0.0.1',port)
	thread1.daemon=True
	thread1.start()
	c1,addr1=s1.accept()
	start_new_thread(send_msg,(c1,c.fileno()))
	threads.append(thread1)
	
for t in threads:
	t.join()

