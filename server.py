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
threads=[]
active_user = []
mapper = {}  #maps usernames to respective file descriptors
#authenticates the username and password
def login(user,password):
	df=pd.read_csv("users.csv")
	i=df[df['Username'] == user]
	if user in active_user:
		return 2
	elif i.iat[0,2]==password:
		return 1
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

def valid_user(user):
	df=pd.read_csv("users.csv")["Username"].values
	if user in df:
		return 1
	else:
		return 0
      
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
		count=3
		while True:
			try:
				msg=s.recv(BUF_SIZE).decode('utf-8')
				words=msg.split(" ")
				cmd=words[0]
				if cmd=="login" and result==0:
					if len(words)!=3:
						s.send(b"Enter three arguments only. Not less, not more.")
						continue
					username=words[1]
					result=login(words[1],words[2])
					if result==1:
						s.send(b"Login successful")
						active_user.append(username)
						mapper[username] = fd         #add mapping from username to fd
						print("{} logged in".format(username))
						f = open("{}.txt".format(username),'a',encoding='utf-8')
						f.close()
					elif result==2:
						s.send(b"Get lost")
						sys.exit()
					else:
						if count>1:
							count=count-1
							msg="Wrong username or password! Try Again. Attempts remaining:"+str(count)
							s.send(msg.encode('utf-8'))
							continue
						else:
							s.send(b"Login attempts exceeded")
							sys.exit()
				elif cmd=="register" and result==0:
					if len(words)!=4:
						s.send(b"Enter four arguments only.Not less, not more.")
						continue
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
						if len(words)<=2:
							s.send(b"Empty message cannot be sent")
							continue
						receiver=words[1]
						msg=username+">>"
						for i in words[2:]:
							msg=msg+" "+i
						if valid_user(receiver):
							if receiver in active_user:
								queues[mapper[receiver]].put(msg)
							else:
								with open("{}.txt".format(receiver),'a',encoding='utf-8') as f:
									f.write("{}\n".format(msg))	
							s.send(b"Message sent")
						else:
							msg="{} is not registered".format(receiver)
							s.send(msg.encode('utf-8'))				
					elif cmd=="broadcast":
						if len(words)<=2:
							s.send(b"Empty message cannot be sent")
							continue
						msg=username+">>"
						for i in words[2:]:
							msg=msg+" "+i
						if words[1]=="all":
							for p in active_user:
								if p!=username:
									queues[mapper[p]].put(msg)					
						else:
							receivers=words[1].split(",")
							for receiver in receivers:
								if valid_user(receiver):
									if receiver in active_user:
										queues[mapper[receiver]].put(msg)
									else:
										#write to his respective file
										with open("{}.txt".format(receiver),'a',encoding='utf-8') as f:
											f.write("{}\n".format(msg))
						s.send(b"Message broadcast")
						'''elif cmd=="chat":
						talk_with=words[1]
						if talk_with not in active_user:
							s.send(b"Chat not possible. {} is offline or does not exist".format(talk_with))
						else:
							queues[mapper[talk_with]].put("Do you want to chat with {}".format(username))
							s.send(b"Waiting")
						elif cmd=="chat_reply":
						reply=words[1]
						if reply=="accept":
							talk_with=words[2]
							s.send(b"Chat begins. Type bye to exit")
							chats=""
							while chats!="bye":
								try:
									chats=s.recv(BUF_SIZE).decode('utf-8')
									queues[mapper[talk_with]].put(username+">> "+chats)
								except:
									continue
							queues[mapper[talk_with]].put("chat ends")
							s.send(b"Your chat has ended")
						else:
							s.send(b"Request declined")'''	
					elif cmd=="logout":
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
					s.send(b"You need to login first")
									
			except Exception as e:
				s.close()
				break


def send_msg(c,addr):
	global queues
	while True:
		try:
			if not addr:
				continue
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
	try:
		c,addr=s.accept()
		q=queue.Queue()
		queues[c.fileno()]=q
		thread1=clientReceive(c,'127.0.0.1',port)
		thread1.daemon=True
		thread1.start()
		c1,addr1=s1.accept()
		start_new_thread(send_msg,(c1,c.fileno()))
		threads.append(thread1)
	except KeyboardInterrupt:
		print("\nServer Exiting")
		break

#for t in threads:
#	t.join()

