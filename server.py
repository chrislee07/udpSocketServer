import random
import socket
import time
from _thread import *
import threading
from datetime import datetime
import json
import ast

clients_lock = threading.Lock()
connected = 0

clients = {}

def connectionLoop(sock):
   
   while True:
      data, addr = sock.recvfrom(1024)
      #data = str(data)
      print("got this: " + str(data))
      if addr in clients:
         if 'heartbeat' in str(data):
            clients[addr]['lastBeat'] = datetime.now()
         if 'x' in str(data):
            clients[addr] = json.loads(data)
            #clients[addr]['currPosition'] = playerPos
            print('moveplayer data : ')
      else:
         if 'connect' in str(data):
            clients[addr] = {}
            clients[addr]['lastBeat'] = datetime.now()
            clients[addr]['color'] = 0
            clients[addr]['currPosition'] = 0
            message = {"cmd": 0,"players": []}

            p = {}
            p['id'] = str(addr)
            p['color'] = 0
            #p['currPosition'] = 0
            message['players'].append(p)

            NewPlayer = {"cmd": 3,"players": []}
            for c in clients: 
               m = json.dumps(message)
               player = {}
               player['id'] = str(c)
               #player['currPosition'] = clients[c]['currPosition']
               NewPlayer['players'].append(player)
               sock.sendto(bytes(m,'utf8'), (c[0],c[1]))

            m = json.dumps(NewPlayer)
            sock.sendto(bytes(m,'utf8'), addr)
            print(data)

def cleanClients(sock):
   while True:
      for c in list(clients.keys()):
         if (datetime.now() - clients[c]['lastBeat']).total_seconds() > 5:
            print('Dropped Client: ', c)
            clients_lock.acquire()
            del clients[c]
            clients_lock.release()
            clearPlayerMessage = {"cmd": 2,"player":"dropped : " + str(c)}
            p = json.dumps(clearPlayerMessage)
            for d in clients.keys():
               sock.sendto(bytes(p,'utf8'), (d[0],d[1]))
      time.sleep(1)

def gameLoop(sock):
   while True:
      #print("Running")
      GameState = {"cmd": 1, "players": []}
      clients_lock.acquire()
      for c in list(clients.keys()):
         player = {}
         #clients[c]['color'] = {"R": random.random(), "G": random.random(), "B": random.random()}
         player['id'] = str(c)
         #player['color'] = clients[c]['color']
         player['currPosition'] = clients[c]['currPosition']
         GameState['players'].append(player)
         s = json.dumps(GameState)
         print('GameLoop - GameState: ' + s)
         sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
      clients_lock.release()
      time.sleep(1)

def main():
   
   port = 12345
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   s.bind(('', port))
   start_new_thread(gameLoop, (s,))
   start_new_thread(connectionLoop, (s,))
   start_new_thread(cleanClients,(s,))
   while True:
      time.sleep(1)

if __name__ == '__main__':
   main()
