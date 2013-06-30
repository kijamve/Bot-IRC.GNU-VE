import socket
import string
import re
import urllib2
import json
from random import choice
import os, sys
import threading 

fpid = os.fork()
if fpid!=0:
  # Running as daemon now. PID is fpid
  sys.exit(0)

sys.stdout = open('out.log', 'w+')
sys.stderr = open('err.log', 'w+')
HOST="irc.radiognu.org"
PORT=6667
NICK="SuperB"
IDENT="SuperB"
REALNAME="SuperB"
CHAN="#radiognu"
USERS = []

def loadJson(name):
	lines = ""
	with open(name, "r") as f:
		for line in f:
			lines+= line
	return json.load(lines) 

entradas_bot = loadJson("entradas_bot.json")
entradas_user = loadJson("entradas_user.json")
entradas = loadJson("salidas.json")
chat_idle = loadJson("chat_idle.json")
menciones = loadJson("menciones.json")
resp_ia	= loadJson("respuestas_inteligentes.json")
salidas_user = loadJson("salidas_user.json")
cambio_nick = loadJson("cambio_nick.json")
radiognu = loadJson("radiognu.json")

readbuffer  = ""
s=socket.socket( )
s.connect((HOST, PORT))
s.send("NICK %s\r\n" % NICK)
s.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))
s.send("JOIN :%s\r\n" % CHAN)
lock = Lock()

def send_msg(msg):
	lock.acquire()
	s.send("PRIVMSG %s :%s\r\n" % (CHAN, msg))
	lock.release()
	print "se envio: %s" % msg
	
class AutoBot(threading.Thread):  
	def __init__(self, num):  
	  threading.Thread.__init__(self)  
	  self.num = num  

	def run(self):  
	while 1:
		sleep(10)
t = AutoBot(1)  
t.start()  

def getRadioGNU():
	response = urllib2.urlopen("http://audio.radiognu.org/json.xsl")
	data = json.load(response) 
	r1 = data["/radiognu.ogg"]
	r2 = data["/radiognu2.ogg"]
	r3 = data["/radiometagnu.ogg"]
	r4 = data["/radiometagnu2.ogg"]
	r5 = data["/radiometagnuam.ogg"]
	r6 = data["/radiognuam.ogg"]
	escuchas = r1["escuchas"] + r2["escuchas"] + r3["escuchas"] + r4["escuchas"] + r5["escuchas"] + r6["escuchas"]
	return {"titulo": r3["titulo"], "artista": r3["artista"], "escuchas": escuchas}
	
while 1:
	readbuffer=readbuffer+s.recv(1024)
	temp=string.split(readbuffer, "\n")
	readbuffer=temp.pop( )
	for line in temp:
		lineSplit = line.split()
		nick = lineSplit[0].split('!')[0][1:]
		if lineSplit[0] == "PING":
			pingid = lineSplit[1]
			s.send("PONG %s\r\n" % pingid)
		elif lineSplit[1] == "353":
			cmd_l = line.split(":")
			_users = cmd_l[2].split()
			for u in _users:
				m = re.search("([a-zA-Z0-9_-]+)", u)
				if m:
					USERS.append(m.group(0))
			send_msg(choice(entradas_bot) % len(USERS))
		elif lineSplit[1] == "PRIVMSG":
			if(nick=="Gnoll") continue  #Evitemos que los bot se respondan entre si, se pueden quedar pegados.
			m = re.search("(:[^:]+:)(.*)", line)
			msg = m.group(2).strip()
			wmsg = msg.split()
			
			if msg.find("radiognu") != -1:
				radio = getRadioGNU()
				send_msg(choice(radiognu) % (radio["titulo"], radio["artista"], radio["escuchas"]))
			else:
				mencion = false
				for p in wmsg:
					palabra = re.search("([a-zA-Z0-9_-]+)", p).group(0)
					if palabra in USERS
						mencion = palabra
						break
				op = []
				for op in resp_ia
				send_msg("%s te recomiendo que le escribas a %s, el tambien se aburre mucho en este canal"%(nick, n))
			print "%s dijo: %s\n" %(nick, msg)
		elif lineSplit[1] == "NICK":
			m = re.search("(:[^:]+:)(.*)", line)
			msg = m.group(2).strip()
			USERS.append(msg)
			USERS.remove(nick)
			send_msg(choice(cambio_nick)%(msg, nick))
		elif lineSplit[1] == "JOIN":
			send_msg(choice(entradas_user)%(nick, choice(USERS)))
			USERS.append(nick)
		elif lineSplit[1] == "QUIT":
			send_msg(choice(salidas_user)%nick)
			USERS.remove(nick)
		else:
			print "UNK: %s\n" % line