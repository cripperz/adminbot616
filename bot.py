#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) 2015 noteness
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import socket
import sys
import time
from KThread import *
from optparse import OptionParser
import crypt
import config
import os
from subprocess import *
import smtplib
import random
import sqlite3
sudo_password=config.sudopassword
homedir=config.userhome
host=config.hostname
ssh_port=config.sshport
def check_db():
        try:
            conn = sqlite3.connect("./example.db")
            print "CONNECTION ESTABLISHED"
            c = conn.cursor()
        except:
            print "Connection not established"
            return "Blargh"
    
        sql = 'CREATE TABLE IF NOT EXISTS users (user text,name text,email text)'
        try:
           c.execute(sql)
           conn.commit()
           conn.close()
           print 'VOILA'
        except:
           conn.rollback()
           conn.close()
           print 'NO VOILA'
    
        
def ddeluser(user):
    try:
        conn = sqlite3.connect("example.db")
        print "CONNECTION ESTABLISHED"
        c = conn.cursor()
    except:
        print "Connection not established"
        return "Blargh"
    
    sql = "DELETE FROM users WHERE user='%s'"% (user)
    try:
       c.execute(sql)
       conn.commit()
       conn.close()
       print 'voila'
    except:
       conn.rollback()
       conn.close()
       print 'no voila'

def dadduser(name,user,email):
    try:
        conn = sqlite3.connect("example.db")
        print "CONNECTION ESTABLISHED"
        c = conn.cursor()
    except:
        print "Connection not established"
        return "Blargh"
    
    sql = """INSERT INTO users(user,
         name,email )
         VALUES ('%s','%s','%s')"""% (user,name,email)
    try:
       c.execute(sql)
       conn.commit()
       conn.close()
       print 'voila'
    except:
       conn.rollback()
       conn.close()
       print 'no voila'
def searchuser(user,nick):
    try:
        conn = sqlite3.connect("example.db")
        print "CONNECTION ESTABLISHED"
        c = conn.cursor()
    except:
        print "Connection not established"
        return "Blargh"
    ss= "SELECT * FROM users WHERE user='"+user+"'"
    try:      
      c.execute(ss)
      results=c.fetchall()
      print "voila"
    except:
        print "no viola"
        return
    for row in results:
            fname = row[0]
            lname = row[1]
            age = row[2]
            send("PRIVMSG %s :user=%s,name=%s,email=%s" % (nick,fname, lname, age ))
            
def createUser(name,username,password,chann,nicc,email,homedir):
    global host
    global ssh_port
    encPass = crypt.crypt(password,"22")
    print "Making user"
    command = "useradd -p "+encPass+ " -s "+ "/bin/bash "+ "-d "+ homedir + username+ " -m "+ " -c \""+ name+"\" " + username
    command = command.split()
    p = Popen(['sudo', '-S'] + command, stdin=PIPE, stderr=PIPE,
          universal_newlines=True)
    sudo_prompt = p.communicate(sudo_password + '\n') [1]
    sudo_prompt = sudo_prompt.strip("[sudo] password for noteness:")
    if sudo_prompt=="" or (sudo_prompt.find("[warning]")!=-1 and sudo_prompt.find("[error]")!= -1) and (not sudo_prompt.find("'"+username+"' already exists")!=-1 ):
        send("PRIVMSG "+ chann +" :"+nick+": User "+username+" successfully added")
        dadduser(name,username,email)
        send_mail(email,name,password,username,host,ssh_port)
        
    else:
        send("PRIVMSG "+ chann +" :"+nick+": "+sudo_prompt)
def deluser(username,chann,nicc):
    ddeluser(username)
    print "Deleting user"

    command = "rm -r /home/"+ username
    command = command.split()
    p = Popen(['sudo', '-S'] + command, stdin=PIPE, stderr=PIPE,
          universal_newlines=True)

    sudo_prompt = p.communicate(sudo_password + '\n') [1]
    sudo_prompt = sudo_prompt.strip("[sudo] password for noteness:")
    command = "deluser "+ username
    command = command.split()
    p = Popen(['sudo', '-S'] + command, stdin=PIPE, stderr=PIPE,
          universal_newlines=True)
    sudo_prompt = p.communicate(sudo_password + '\n') [1]
    sudo_prompt = sudo_prompt.strip("[sudo] password for noteness:")

    if sudo_prompt=="" or (sudo_prompt.find("[warning]")!=-1 and sudo_prompt.find("[error]")!= -1):
        send("PRIVMSG "+ chann +" :"+nick+": User "+username+" successfully deleted")
        
    else:
        send("PRIVMSG "+ chann +" :"+nick+": "+sudo_prompt)
parser = OptionParser()
parser.add_option("-v", "--verbose",
                  action="store_true",dest="verbose", default=False,
                  help="displays everything")
parser.add_option("-c", "--control",
                  action="store_true",dest="control", default=False,
                  help="Allows you to send raw IRC commands through the command line itself")
(options, args) = parser.parse_args()
mserver = config.server
jchannel = config.channels
botnick = config.nick
addrchar=config.addrchar
ownercloak=config.owners
username = config.username
password = config.password
port = config.port
def send_mail(email,name,password,username,host,ssh_port):
    
    SERVER = "localhost"

    FROM = "Admin <admin@bassamazzam.com>"
    TO = [email,] # must be a list

    SUBJECT = "Your username has been activated"


    message = """From: %s
To: %s
Subject: %s

Hello %s  ,

Your user %s has been created and your password is : %s

SSH details:
host: %s
port: %s

Regards,
    Admin
    Bassamazzam
    
    """ % (FROM, ", ".join(TO), SUBJECT,name ,username,password,host,ssh_port)



    server = smtplib.SMTP(SERVER)
    server.sendmail(FROM, TO, message)
    server.quit()
def st():
   line = sys.stdin.readline()
   while line:
      send(line)
      line = sys.stdin.readline()
sthr =KThread(target=st)
def quitf():
    thr.kill()
    sthr.kill()
    sys.exit()
def send(msg):
   ircsock.send(msg+"\n")
   if options.verbose == True:
      print "-> "+msg

def prmsg(msg):
   if options.verbose == True:
      print "<- "+msg

def commands(nick,channel,message):
   global botnick
   if message.find(':VERSION ')!=-1:
      return send('NOTICE'+nick+':VERSION  Note Bot v1.01' )
   elif message.find(':'+addrchar+'help ')!=-1:
      acco=message.rsplit(":"+addrchar+"help ") [1]
      if acco=="opme":
         return send("PRIVMSG %s :%s: opme: Give you op .If the bot isn't op, tries to do so through ChanServ (only usable in channel)" % (channel,nick))
      if acco=="op":
         return send("PRIVMSG %s :%s: op: Ops [<nick>] .Without args, Ops the bot, with args, Ops <nick>.If the bot isn't op, tries to do so through ChanServ (only usable in channel)" % (channel,nick))
      if acco=="deopme":
         return send("PRIVMSG %s :%s: deopme: Deops you .If the bot is isn't op, tries to do so through ChanServ (only usable in channel)" % (channel,nick))
      if acco=="deop":
         return send("PRIVMSG %s :%s: deop: Deops [<nick>] .Without args, Ops the bot, with args, Ops <nick>..If the bot is isn't op, tries to do so through ChanServ (only usable in channel)" % (channel,nick))
      if acco=="send":
         return send("PRIVMSG %s :%s: send <args> . Sends raw IRC lines" % (channel,nick))
      if acco=="do":
         return send("PRIVMSG %s :%s: do <text> . sends a /me to the channel (only usable in channel)" % (channel,nick))
      if acco=="say":
         return send("PRIVMSG %s :%s: say <text> . says <text> in the channel (only usable in channel)" % (channel,nick))
      if acco=="chgnick":
         return send("PRIVMSG %s :%s: chgnick <nick> . changes nick to <nick>" % (channel,nick))
      if acco=="restart":
         return send("PRIVMSG %s :%s: restarts the bot" % (channel,nick))
      if acco=="quit":
         return send("PRIVMSG %s :%s: Make the bot die" % (channel,nick))
      if acco=="topic":
         return send("PRIVMSG %s :%s: topic <text> .changes the channel topic to <text> , (only usable in channel)" % (channel,nick))
      if acco=="adduser":
         return send("PRIVMSG %s :%s: adduser <name> <username> <email>. Get the <username> a shell, the password will be mailed to the <email>" % (channel,nick))
      if acco=="deluser":
         return send("PRIVMSG %s :%s: Deletes <user>" % (channel,nick))
      if acco=="who":
         return send("PRIVMSG %s :%s: messages you the information about the <user>" % (channel,nick))
   elif message.find(":"+addrchar+"adduser ")!=-1:
      acco=message.split(":"+addrchar+"adduser ") [1]
      accob = acco.split(" ")
      try:
          name = accob [0]
          username = accob [1]
          password = str(int(random.random()*100000000000000000))
          email = str(accob [2])
          
      except IndexError:
          return send("PRIVMSG %s :%s: name or username or email is missing" % (channel,nick))
      createUser(name,username,password,channel,nick,email,homedir)
      return send("PRIVMSG %s :%s: Your account has been created, check your email for instructions and password" % (channel,nick))
   elif message.find(':'+addrchar+'help')!=-1:
      return send("PRIVMSG %s :%s: adduser <name> <username> <email>,  restriced commands are send , opme , op [<nick>] , deopme, deop [<nick>] , say <text> , do <text> , chgnick <nick> , restart , quit , topic <text> , deluser <user> , who <user>" % (channel,nick))

   if cloak in ownercloak:
      if message.find(':'+addrchar+'quit')!=-1:
         send("QUIT :forced quit from "+ nick)
         quitf()
      if message.find(':'+addrchar+'send ')!=-1:
         acco=message.rsplit(":"+addrchar+"send ") [1]
         return send(acco)
      elif message.find(":"+addrchar+"deluser ")!=-1:
        acco=message.split(":"+addrchar+"deluser ") [1]

        try:
          deluser(acco,channel,nick)
        except IndexError:
          return send("PRIVMSG %s :%s: name or username or email is missing" % (channel,nick))
      if message.find(':'+addrchar+'gpull')!=-1:
        Popen("git pull",shell=True)
      if message.find(':'+addrchar+'who ')!=-1:
         accon=message.rsplit(":"+addrchar+"who ") [1]
         searchuser(accon,nick)
      elif message.find(':'+addrchar+'say ')!=-1:
         accon=message.rsplit(":"+addrchar+"say ") [1]
         return send("PRIVMSG %s :%s\r" % (channel,accon))
      if message.find(':'+addrchar+'opme')!=-1 and channel != nick:
         send("MODE %s +o %s\r" % (channel,nick))
         send("CHANSERV :OP %s %s\r" % (channel,nick))
      elif message.find(':'+addrchar+'op')!=-1 and channel != nick:
         accon=message.rsplit(":"+addrchar+"op") [1]
         send("CHANSERV :OP %s %s\r" % (channel,accon))
         send("MODE %s +o %s\r" % (channel,accon))

      elif message.find(':'+addrchar+'deopme')!=-1 and channel != nick:
         send("CHANSERV :DEOP %s %s\r" % (channel,nick))
         send("MODE %s -o %s\r" % (channel,nick))
      elif message.find(':'+addrchar+'deop')!=-1 and channel != nick:
         accon=message.rsplit(":"+addrchar+"deop") [1]
         send("CHANSERV :DEOP %s %s\r" % (channel,accon))
         send("MODE %s -o %s\r" % (channel,accon))
      elif message.find(':'+addrchar+'do ')!=-1:
         accon=message.rsplit(":"+addrchar+"do ") [1]
         send("PRIVMSG %s :ACTION %s \r" % (channel,accon))
     
      elif message.find(':'+addrchar+'tstart')!=-1:
            thr.start()
      elif message.find(':'+addrchar+'tstop')!=-1:
            thr.kill()
      elif message.find(':'+addrchar+'topic ')!=-1:
         accon=message.rsplit(":"+addrchar+"topic ") [1]
         send("TOPIC %s :%s\r" % (channel,accon))
         send("CHANSERV :TOPIC %s %s\r" % (channel,accon))
      elif message.find(':'+addrchar+'restart')!=-1:
          python = sys.executable
          send("QUIT :Restarting....")
          os.execl(python, python, *sys.argv)
      elif message.find(':'+addrchar+'chgnick ')!=-1:
            acco=message.rsplit(":"+addrchar+"chgnick ") [1]
            if acco.find(' ')!=-1:
                return send("PRIVMSG %s :%s: Not a valid nick\r" % (channel,nick))
            else:
                botnick = acco
                return send("NICK "+ botnick )

      if channel == nick :
         return send("PRIVMSG %s :Not in a channel\r" % (nick))
   elif not cloak in ownercloak and message.find(':'+addrchar)!=-1:
      return send("PRIVMSG %s :%s: You are not authorized to run this, sorry\r" % (channel,nick))
          

if options.control == True:
   sthr.start()

def joinchan(chan):
   send("JOIN "+chan)
def ping():
   send("PONG :pingis")  

def sendmsg(chan , msg): 
  send("PRIVMSG "+ chan +" :"+ msg +"!") 
def hello(): 
  send("PRIVMSG "+ channel +" :Hello "+ nick )
def func():
   count = 1
   while 1:
      time.sleep(10)
      if count == 1:
         send("PRIVMSG ##notness :"+str(count)+"st time saying")
      elif count == 2:
         send("PRIVMSG ##notness :"+str(count)+"nd time saying")
      elif count == 3:
         send("PRIVMSG ##notness :"+str(count)+"rd time saying")
      else:
         send("PRIVMSG ##notness :"+str(count)+"th time saying")
      count += 1
thr = KThread(target=func)

print "Starting Bot......"
check_db()
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock.connect((mserver, port)) 
send("USER "+ botnick +" "+ botnick +" "+ botnick + " "+botnick) 
send("NICK "+ botnick ) 

    



while 1:
    ircmsg = ircsock.recv(4096) 
    ircmsg = ircmsg.strip('\n\r')
    ircmsg = ircmsg.strip('\n')
    ircmsg = ircmsg.strip('\r')
    prmsg(ircmsg)
    try:
         if ircmsg.split(" ") [1].split(" ") [0] == 'PRIVMSG':
            	nick=ircmsg.split('!')[0][1:]
            	cloak=ircmsg.split('@')[1].split(' ')[0]
            	channel=ircmsg.split(' PRIVMSG ')[-1].split(' :')[0]
                if channel==botnick:
                    channel=nick
            	commands(nick,channel,ircmsg)
         
         if (ircmsg.find("Nickname is already in use") != -1) and (ircmsg.split(" ") [1].split(" ") [0]=='433'):
              botnick +="_"
              send("NICK "+botnick)
         if ircmsg.lower().find(":hello "+ botnick.lower()) != -1:
             send("PRIVMSG "+channel+" :Hello there "+nick+"!")
         if ircmsg.find("PING :") != -1: 
             ping()
         if ircmsg.find("MODE "+botnick) != -1:
             send("NICKSERV :id "+username+" "+password)
         if (ircmsg.find(":NickServ!NickServ",0, 25) != 1) and  (ircmsg.find("NOTICE "+botnick+" :You are now identified for ")!= -1):
             joinchan(jchannel)
         if (ircmsg.find(":"+botnick,0, 25) != 1) and (ircmsg.find(" NICK ") != 1):
             acco = ircmsg.split("NICK ") [1]
             acco = acco.strip(":")
             botnick = acco
         if channel == botnick:
             channel = nick
    except IndexError:
        pass


