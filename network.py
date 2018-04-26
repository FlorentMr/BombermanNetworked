# -*- coding: Utf-8 -*
# Author: aurelien.esnard@u-bordeaux.fr

from model import *
import pygame
import socket, threading
import errno
import time


COUNTDOWN_BOMB= 10
COUNTDOWN_FRUIT= 20
################################################################################
#                          NETWORK SERVER CONTROLLER                           #
################################################################################

class NetworkServerController:

    def __init__(self, model, port, conn_client, nbPlayer, pseudo):
        self.model = model
        self.port = port
        self.conn_client = conn_client
        self.nbPlayer = nbPlayer
        self.pseudo = pseudo
        self.countdown_bomb= COUNTDOWN_BOMB
        self.time_to_dropBomb = (self.countdown_bomb+1)*1000-1
        self.countdown_fruit = COUNTDOWN_FRUIT
        self.time_to_dropfruit = (self.countdown_fruit+1)*1000-1

    # time event
    def isInConn_client(self, name):
        b=False
        for client in self.conn_client.keys():
            if client == name :
                b=True
        return b

    def deconnexion (self, name):
            cpt=0
            for it in self.conn_client:
                if it==name:
                    break
                else:
                    cpt+=1
            del (self.conn_client[name])
            for it in self.conn_client :
                self.conn_client[it].sendall(b"print('Adversaire deconnecte') \n")

            if(self.nbPlayer==2):
                print ("terminer")
                for _ in self.conn_client:
                    self.conn_client[_].sendall(b"print ('Gagne par abandon')\n")
                    self.conn_client[_].sendall(b"self.model.kill_character('"+ self.pseudo[cpt].encode() +b"') \n")
                del(self.pseudo[cpt])
                return False
            else:
                self.nbPlayer -= 1
                for it in self.conn_client :
                    self.conn_client[it].sendall(b"print('Un joueur a quitte la partie')\n")
                    self.conn_client[it].sendall(b"self.model.kill_character('"+ self.pseudo[cpt].encode() +b"') \n")
                del(self.pseudo[cpt])
                return True

    def tick(self, dt):
        if self.time_to_dropBomb >= 0:
            self.time_to_dropBomb -= dt
            self.countdown_bomb = int(self.time_to_dropBomb / 1000)
        else:
            randomPlayer=random.choice(self.pseudo)
            for __ in self.conn_client :
                self.conn_client[__].send(("self.model.drop_bomb('" + str(randomPlayer) + "') \n").encode())
            self.countdown_bomb= COUNTDOWN_BOMB
            self.time_to_dropBomb = (self.countdown_bomb+1)*1000-1

        if self.time_to_dropfruit >= 0:
            self.time_to_dropfruit -= dt
            self.countdown_fruit = int(self.time_to_dropfruit / 1000)
        else:
            randomPosFruit=self.model.map.random()
            randomKindFruit = random.choice(FRUITS)
            for __ in self.conn_client :
                self.conn_client[__].send(("self.model.add_fruit(" + str(randomKindFruit) + "," + str(randomPosFruit) + ")" + "\n" ).encode())
            self.countdown_fruit= COUNTDOWN_FRUIT
            self.time_to_dropfruit = (self.countdown_fruit+1)*1000-1

        for it in self.conn_client :
            self.conn_client[it].setblocking(False)

        for it in self.conn_client :
            try :
                msg = self.conn_client[it].recv(2048)
                for id in self.conn_client :
                    if (id!=it):
                        self.conn_client[id].send(msg)
            except socket.error as e:
                if e.args[0] == errno.EWOULDBLOCK:
                    None
                else :
                    return self.deconnexion(it)

                # quit
        return True

################################################################################
#                          NETWORK CLIENT CONTROLLER                           #
################################################################################

class NetworkClientController:

    def __init__(self, model, host, port, nickname, socket, nbPlayer):
        self.model = model
        self.host = host
        self.port = port
        self.nickname = nickname
        self.socket = socket
        self.nbPlayer = nbPlayer

    # keyboard events

    def keyboard_quit(self):
        print("=> event \"quit\"")
        return False

    def keyboard_move_character(self, direction):
        print("=> event \"keyboard move direction\" {}".format(DIRECTIONS_STR[direction]))
        if not self.nickname: return True
        nickname = self.nickname
        if direction in DIRECTIONS:
            self.model.move_character(nickname, direction)
            self.socket.send(("self.model.move_character('" + str(nickname)+"'," + str(direction) + ") \n").encode())
        return True


    def keyboard_drop_bomb(self):
        print("=> event \"keyboard drop bomb\"")
        if not self.nickname: return True
        nickname = self.nickname
        self.model.drop_bomb(nickname)
        self.socket.send(("self.model.drop_bomb('" + str(nickname) + "') \n").encode())
        return True

    # time event

    def tick(self, dt):
        self.socket.setblocking(False)
        try :
            bomb_random= self.socket.recv(1024)
            print(bomb_random)
            exec(bomb_random.decode())


        except socket.error as e:
            if e.args[0] == errno.EWOULDBLOCK:
                None
            else :
                print("error:", e)
        try :
            coup = self.socket.recv(1024)
            exec(coup.decode())
        except socket.error as e:
            if e.args[0] == errno.EWOULDBLOCK:
                return True
            else :
                keyboard_quit()
        return True
