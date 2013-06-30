import socket
import string
import re
import sqlite3
import urllib2
import json
from random import choice

HOST="irc.radiognu.org"
PORT=6667
NICK="BCuado"
IDENT="BCuado"
REALNAME="BCuado"
CHAN="#radiognu"
USERS = []
readbuffer  = ""
s=socket.socket( )
s.connect((HOST, PORT))
s.send("NICK %s\r\n" % NICK)
s.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))
s.send("JOIN :%s\r\n" % CHAN)

def send_msg(msg):
	s.send("PRIVMSG %s :%s\r\n" % (CHAN, msg))
	print "se envio: %s" % msg

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
		elif lineSplit[1] == "PRIVMSG":
			m = re.search("(:[^:]+:)(.*)", line)
			msg = m.group(2).strip()
			if msg.find("radiognu") != -1:
				response = urllib2.urlopen("http://audio.radiognu.org/json.xsl")
				data = json.load(response) 
				r1 = data["/radiognu.ogg"]
				r2 = data["/radiognu2.ogg"]
				r3 = data["/radiometagnu.ogg"]
				r4 = data["/radiometagnu2.ogg"]
				r5 = data["/radiometagnuam.ogg"]
				r6 = data["/radiognuam.ogg"]
				escuchas = r1["escuchas"] + r2["escuchas"] + r3["escuchas"] + r4["escuchas"] + r5["escuchas"] + r6["escuchas"]
				send_msg("%s de %s nos esta durmiendo, solo %d personas los escucha :(" % (r3["titulo"], r3["artista"], escuchas))
			
			if msg.find("estoy aburrido") != -1:
				n = choice(USERS)
				while n==nick:
					n = choice(USERS)
				send_msg("%s te recomiendo que le escribas a %s, el tambien se aburre mucho en este canal"%(nick, n))
			print "%s dijo: %s\n" %(nick, msg)
			wmsg = msg.split()
		elif lineSplit[1] == "NICK":
			m = re.search("(:[^:]+:)(.*)", line)
			msg = m.group(2).strip()
			USERS.append(msg)
			USERS.remove(msg)
		elif lineSplit[1] == "JOIN":
			USERS.append(nick)
		elif lineSplit[1] == "QUIT":
			USERS.remove(nick)
		else:
			print "UNK: %s\n" % line
