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

msg=s.recv(1024).decode('utf-8')
print(msg)
data=input()
s.send(data.encode('utf-8'))
'''msg=s.recv(1024).decode('utf-8')
if num!=1 and num!=2:
	s.close()
elif int(data)==2:
	name=input()
else:
	name=""
user=input()
password=input()
to_send=name+"\n"+user+"\n"+password
s.send(to_send.encode('utf-8'))
msg=s.recv(1024).decode('utf-8')'''
s.close()

