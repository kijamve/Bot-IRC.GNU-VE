import socket
import string
import re
import urllib2
import json
from random import choice
import os, sys
import threading 
import time 
import codecs

#fpid = os.fork()
#if fpid!=0:
#  sys.exit(0)

#sys.stdout = open('out.log', 'w+')
#sys.stderr = open('err.log', 'w+')
HOST="irc.radiognu.org"
PORT=6667
NICK="SuperB"
IDENT="SuperB"
REALNAME="SuperB"
CHAN="#radiognu"
USERS = []

def loadJson(name):
	lines = ""
	with codecs.open(name, 'rb', 'utf-8') as f:
		for line in f:
			lines+= line
	return json.loads(lines.encode('utf-8')) 

entradas_bot = loadJson("entradas_bot.json")
entradas_user = loadJson("entradas_user.json")
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
lock = threading.Lock()

def send_msg(msg):
	print "Enviando: %s" % msg
	lock.acquire()
	s.send(("PRIVMSG %s :%s\r\n".encode('utf-8') % (CHAN, msg)).encode('utf-8'))
	lock.release()
	print "Enviado"
	
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
	return {"titulo": r3["titulo"], "artista": r3["artista"], "escuchas": "%d"%escuchas}
	
class AutoBot(threading.Thread):  
	def __init__(self, num):  
	  threading.Thread.__init__(self)  
	  self.num = num  

	def run(self):  
		while 1:
			time.sleep(10*60)
			radio = getRadioGNU()
			send_msg(choice(radiognu).replace("__TITULO__",radio["titulo"]).replace("__ARTISTA__", radio["artista"]).replace("__ESCUCHAS__", radio["escuchas"]))

t = AutoBot(1)  
t.start()  

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
			send_msg(choice(entradas_bot).replace("__CONECTADOS__", "%d"%len(USERS)))
		elif lineSplit[1] == "PRIVMSG":
			if(nick=="Gnoll"):
				continue  #Evitemos que los bot se respondan entre si, se pueden quedar pegados.
			m = re.search("(:[^:]+:)(.*)", line)
			msg = m.group(2).strip()
			wmsg = msg.split()
			mencion = None
			for p in wmsg:
				palabra = re.search("([a-zA-Z0-9_-]+)", p)
				if(palabra):
					palabra = palabra.group(0)
					if palabra in USERS:
						mencion = palabra
						break
			if(mencion):
				print "%s fue mencionado"%mencion
			op = []
			for r in resp_ia:
				if((mencion and r["mencion"]) or (not r["mencion"])):
					if(re.search(r["patron"], msg.lower(), re.IGNORECASE)):
						print "Encontrado %s"%r["respuesta"]
						op.append(r["respuesta"])
					else:
						print "Patron '%s' no encontrado"%r["patron"]

			rnick=choice(USERS)	
			while(rnick==nick):
				rnick=choice(USERS)
			if(len(op)>0):
				if(mencion):
					send_msg(choice(op).replace("__MENCION__", mencion).replace("__NICK__", nick).replace("__RNICK__", rnick));
				else:
					send_msg(choice(op).replace("__NICK__", nick).replace("__RNICK__", rnick));
			print "%s dijo: %s\n" %(nick, msg)
		elif lineSplit[1] == "NICK":
			m = re.search("(:[^:]+:)(.*)", line)
			msg = m.group(2).strip()
			USERS.append(msg)
			USERS.remove(nick)
			send_msg(choice(cambio_nick).replace("__NICK_ANT__", nick).replace("__NEW_NICK__", msg))
		elif lineSplit[1] == "JOIN":
			if(len(USERS)>2):
				send_msg(choice(entradas_user).replace("__NICK__", nick).replace("__RNICK__", choice(USERS)))
			USERS.append(nick)
		elif lineSplit[1] == "QUIT":
			#send_msg(choice(salidas_user).replace("__NICK__", nick))
			USERS.remove(nick)
		else:
			print "UNK: %s\n" % line