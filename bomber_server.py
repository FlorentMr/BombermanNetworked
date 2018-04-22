#!/usr/bin/env python3
# -*- coding: Utf-8 -*
# Author: aurelien.esnard@u-bordeaux.fr

from model import *
from view import *
from network import *
import sys
import pygame
import socket, threading
import errno

### python version ###
print("python version: {}.{}.{}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2]))
print("pygame version: ", pygame.version.ver)



################################################################################
#                                  Fonctions
################################################################################
class ThreadClient(threading.Thread):
    '''dérivation d'un objet thread pour gérer la connexion avec un client'''
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.connexion = conn

def isInConn_client(name):
    b=False
    for client in conn_client.keys():
        if client == name :
            b=True
    return b
################################################################################
#                                 MAIN                                         #
################################################################################


#### Initialisation
if len(sys.argv) == 2:
    port = int(sys.argv[1])
    map_file = "maps/map1"
elif len(sys.argv) == 3:
    port = int(sys.argv[1])
    map_file = sys.argv[2]
else:
    print("Usage: {} port [map_file]".format(sys.argv[0]))
    sys.exit()

mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM,0)
try:
    mySocket.bind(("localhost", port))

except socket.error:
    print ("La liaison du socket à l'adresse choisie a échoué.")
    sys.exit()

print ("Serveur prêt, en attente de requêtes ...")

mySocket.listen(5)

conn_client = {} # dictionnaire des connexions clients

pygame.display.init()
pygame.font.init()
clock = pygame.time.Clock()
model = Model()
model.load_map(map_file)
for _ in range(10): model.add_fruit()
pseudo=[]


        # main loop
while True:
    connexion, adresse = mySocket.accept()

            # Créer un nouvel objet thread pour gérer la connexion :
    th = ThreadClient(connexion)

            # Mémoriser la connexion dans le dictionnaire :
    it = th.getName()
            # redonner les noms Thread-1 / Thread-2 lorsqu'ils sont dispos
    print (conn_client)
    if isInConn_client("Thread-1")==False:
        th.setName("Thread-1")
    elif isInConn_client("Thread-2")==False:
        th.setName("Thread-2")
    elif isInConn_client("Thread-3")==False:
        th.setName("Thread-3")
    it= th.getName()
    conn_client[it] = connexion

    print ("Client {} connecté, adresse IP {}, port {}. \n".format(it, adresse[0], adresse[1]))
    model.add_character(it)
    server = NetworkServerController(model, port, conn_client)
    th.start()


### Envoie de la map a tout les joueurs connecté
    for i in server.model.map.array :
        for j in i :
            map_text = str(j)
            conn_client[it].sendall(map_text.encode())
        conn_client[it].sendall("\n".encode())
    msg = conn_client[it].recv(2048)
    print (msg.decode())


#### Envoie des fruits
    for f in server.model.fruits :
        conn_client[it].sendall(("model.add_fruit(" + str(f.kind) + "," + str(f.pos) + ")" + "\n" ).encode())

    pseudo.append(conn_client[it].recv(2048).decode())

#### Envoie des personnages aux joueurs
    if (it=="Thread-1"):
        conn_client[it].sendall((" True," + str(server.model.characters[0].kind)+ "," + str(server.model.characters[0].pos) + ")" + "\n" ).encode())
        msg = conn_client[it].recv(2048)
        print (msg.decode())
    elif (it=="Thread-2") :
        conn_client[it].sendall((" True," + str(server.model.characters[1].kind)+ "," + str(server.model.characters[1].pos) + ")" + "\n" ).encode())
        msg = conn_client[it].recv(2048)
        print (msg.decode())
        conn_client["Thread-1"].sendall(("model.add_character('" + str(pseudo[1]) + "', False," + str(server.model.characters[1].kind)+ "," + str(server.model.characters[1].pos) + ")" + "\n" ).encode())
        conn_client[it].sendall(("model.add_character('" + str(pseudo[0]) +  "', False," + str(server.model.characters[0].kind)+ "," + str(server.model.characters[0].pos) + ")" + "\n" ).encode())
    elif (it=="Thread-3"):
        conn_client[it].sendall((" True," + str(server.model.characters[2].kind)+ "," + str(server.model.characters[2].pos) + ")" + "\n" ).encode())
        msg = conn_client[it].recv(2048)
        print (msg.decode())
        conn_client["Thread-1"].sendall(("model.add_character('" + str(pseudo[2]) + "', False," + str(server.model.characters[2].kind)+ "," + str(server.model.characters[2].pos)+ ")" + "\n" ).encode())
        conn_client["Thread-2"].sendall(("model.add_character('" + str(pseudo[2]) + "', False," + str(server.model.characters[2].kind)+ "," + str(server.model.characters[2].pos)+ ")" + "\n" ).encode())
        conn_client[it].sendall(("model.add_character('" + str(pseudo[0]) +  "', False," + str(server.model.characters[0].kind)+ "," + str(server.model.characters[0].pos) + ")" + "\n" ).encode())
        conn_client[it].sendall(("model.add_character('" + str(pseudo[1]) +  "', False," + str(server.model.characters[1].kind)+ "," + str(server.model.characters[1].pos) + ")" + "\n" ).encode())

    ##### Transmission des coups des joueurs
        while True :
            dt = clock.tick(FPS)
            server.tick(dt)
            model.tick(dt)

print("Game Over!")
pygame.quit()
