import socket
import os
import sys
import queue
from threading import Thread
from _thread import *
import pandas as pd
import numpy as np
from multiprocessing import Lock

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
active_user = []
mapper = {}  #maps usernames to respective file descriptors
mutex = Lock()

#authenticates the username and password
def login(user,password):
	df=pd.read_csv("users.csv")
	i=df[df['Username'] == user]
	if i.iat[0,2]==password:
		return 1
	elif user in active_user:
		return 0
	else:
		return 0

#register a new user
def register(name,user,password):
	df=pd.read_csv("users.csv")
	if (df['Username']==user).any():
		return 0
	else:
		df.loc[-1]=[name,user,password]
		df.index=df.index+1
		df.to_csv("users.csv",index=False)
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
						mapper[username] = fd         #add mapping from username to fd
						print("{} logged in".format(username))
						f = open("{}.txt".format(username),'a',encoding='utf-8')
						f.close()
					else:
						s.send(b"Wrong username or password! Try Again")
						continue
				elif cmd=="register" and result==0:
					username=words[2]
					result=register(words[1],words[2],words[3])
					if result:
						s.send(b"Registration successful")
						active_user.append(username)
						mapper[username] = fd         #add mapping from username to fd
						f = open("{}.txt".format(username),'a',encoding='utf-8')
						f.close()
					else:
						s.send(b"Sorry, username already taken! Try again")
						continue
				elif result==1:
					if cmd=="online":
						msg=""
						for p in active_user:
							if p!=username:
								msg=msg+" "+p
						if msg=="":
							msg="No active users excluding you"
						s.send(msg.encode('utf-8'))
					elif cmd=="send":
						receiver=words[1]
						msg=username+">>"
						for i in words[2:]:
							msg=msg+" "+i
						#print(msg)
						if receiver in active_user:
							with mutex:
								queues[mapper[receiver]].put(msg)
						else:
							with open("{}.txt".format(receiver),'a',encoding='utf-8') as f:
								f.write("{}\n".format(msg))
						s.send(b" ")
						
					elif cmd=="broadcast":
						msg=username+">>"
						for i in words[2:]:
							msg=msg+" "+i
						if words[1]=="all":
							for p in active_user:
								if p!=username:
									with mutex:
										queues[mapper[p]].put(msg)
									#add to the respective users' shared queue
									print(p)
									
						else:
							receivers=words[1].split(",")
							for receiver in receivers:
								if receiver in active_user:
									with mutex:
										queues[mapper[receiver]].put(msg)
									#add to the respective users shared queue
									print("active",receiver)
								else:
									#write to his respective file
									with open("{}.txt".format(receiver),'a',encoding='utf-8') as f:
										f.write("{}\n".format(msg))
									print("inactive",receiver)
						s.send(b" ")
									
					elif cmd=="logout":
						active_user.remove(username)
						print("logout",username)
					elif cmd=="inbox":
						msg=""
						with open("{}.txt".format(username),'r',encoding='utf-8') as f:
							for line in f:
								msg+= (line+"\n")
						s.send(line.encode("utf-8"))
						if(msg==""):
							s.send(b" ")
						print("Inbox requested by {}".format(username))
					else:
						s.send(b"Enter a valid command")
				else:
					s.send(b"Get lost")
					sys.exit()
									
			except Exception as e:
				#print(e)
				s.close()
				break


def send_msg(c,addr):
	global queues
	while True:
		try:
			if not addr:
				continue
			with mutex:
				msgs = queues[addr]
			while(not msgs.empty()):
				c.send(msgs.get().encode("utf-8"))
		except:
			c.close()
			break
							
#AF_INET implies IPv4 and SOCK_STREAM implies TCP connection
port=int(sys.argv[1])

#creates the first socket where server only receives
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('127.0.0.1',port))
s.listen()

s1=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s1.bind(('127.0.0.1',2501))
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

