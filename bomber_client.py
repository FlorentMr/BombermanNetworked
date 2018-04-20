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

### python version ###
print("python version: {}.{}.{}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2]))
print("pygame version: ", pygame.version.ver)

################################################################################
#                                 MAIN                                         #
################################################################################

# parse arguments
if len(sys.argv) != 4:
    print("Usage: {} host port nickname".format(sys.argv[0]))
    sys.exit()
host = sys.argv[1]
port = int(sys.argv[2])
nickname = sys.argv[3]

connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_avec_serveur.connect((host, port))
print("Connexion établie avec le serveur sur le port {}".format(port))


# initialization
pygame.display.init()
pygame.font.init()
clock = pygame.time.Clock()

#####Récupération de la map via le serveur
msg_recu =connexion_avec_serveur.recv(2048)
mon_fichier= open("maps/map", "w")
mon_fichier.write (msg_recu.decode())
mon_fichier.close()
connexion_avec_serveur.send("Map bien reçu ! Les fruits ?".encode())
model = Model()
model.load_map("maps/map")
msg_recu =connexion_avec_serveur.recv(100000)
exec(msg_recu.decode())
connexion_avec_serveur.send("Les fruits sont là ! Mon perso ?".encode())

#### Récupération de notre perso et celui de l'adversaire
perso_recu =connexion_avec_serveur.recv(100000)
exec("model.add_character(nickname," + perso_recu.decode())
connexion_avec_serveur.send("Perso 1 reçu".encode())
perso_recu =connexion_avec_serveur.recv(100000)
exec("model.add_character('Player 2'," + perso_recu.decode())


## Lancement du visuel
view = GraphicView(model, nickname)
client = NetworkClientController(model, host, port, nickname, connexion_avec_serveur)
kb = KeyboardController(client)

# main loop
while True:
    # make sure game doesn't run at more than FPS frames per second
    dt = clock.tick(FPS)
    if not kb.tick(dt): break
    if not client.tick(dt): break
    model.tick(dt)
    view.tick(dt)

    ###### Faire un select de recv qui met a jour les coup Player 2 TOUT le TEMPS


# quit
print("Game Over!")
connexion_avec_serveur.close()
pygame.quit()
