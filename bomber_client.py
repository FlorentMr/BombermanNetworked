#!/usr/bin/env python3
# -*- coding: Utf-8 -*
# Author: aurelien.esnard@u-bordeaux.fr

from model import *
from view import *
from keyboard import *
from network import *
import sys
import pygame
import socket
import errno

### python version ###
print("python version: {}.{}.{}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2]))
print("pygame version: ", pygame.version.ver)

################################################################################
#                                 MAIN                                         #
################################################################################

# parse arguments
if (len(sys.argv) != 6 and len(sys.argv) != 5) :
    print("Usage: {} host port nickname".format(sys.argv[0]))
    sys.exit()
host = sys.argv[1]
port = int(sys.argv[2])
nickname = sys.argv[3]
nbPlayer = int(sys.argv[4])
if (len(sys.argv)==5):
    skin = "dk"  ### DK par défaut
else :
    skin = sys.argv[5]

connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_avec_serveur.connect((host, port))
print("Connexion établie avec le serveur sur le port {}".format(port))

# initialization
pygame.display.init()
pygame.font.init()
clock = pygame.time.Clock()

####### Envoie du pseudo au Serveur

#####Récupération de la map via le serveur
mon_fichier= open("maps/map", "w")
msg_recu =connexion_avec_serveur.recv(2048)
mon_fichier.write (msg_recu.decode())
connexion_avec_serveur.sendall(b"ACK")
mon_fichier.close()


model = Model()
model.load_map("maps/map")
msg_recu =connexion_avec_serveur.recv(2048)
exec(msg_recu.decode())

#### Récupération de notre perso et celui de l'adversaire

connexion_avec_serveur.send(str(nickname).encode())  #### Envoie du nickname pour l'adversaire
ACK = connexion_avec_serveur.recv(1000)
connexion_avec_serveur.send(str(skin).encode())     ### Envoie de son choix de skin au serveur
ACK = connexion_avec_serveur.recv(1000)
connexion_avec_serveur.send(str(nbPlayer).encode())  ### Envoie du nombre de joueur que l'on veut dans sa game
ACK = connexion_avec_serveur.recv(1000)
perso_recu =connexion_avec_serveur.recv(2048)
exec("model.add_character(nickname," + perso_recu.decode())
connexion_avec_serveur.send("Perso 1 reçu".encode())
perso_recu =connexion_avec_serveur.recv(2048)
exec(perso_recu.decode())
if (nbPlayer>2):                                    ### Réception du perso Player 3 si il y en a un
    perso_recu =connexion_avec_serveur.recv(2048)
    exec(perso_recu.decode())


## Lancement du visuel
view = GraphicView(model, nickname)
client = NetworkClientController(model, host, port, nickname, connexion_avec_serveur, nbPlayer)
kb = KeyboardController(client)

# main loop
while True:
    # make sure game doesn't run at more than FPS frames per second
    dt = clock.tick(FPS)
    if not kb.tick(dt): break
    if not client.tick(dt): break
    model.tick(dt)
    view.tick(dt)
# quit
print("Game Over!")
connexion_avec_serveur.close()
pygame.quit()
