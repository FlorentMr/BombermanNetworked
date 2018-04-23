# -*- coding: Utf-8 -*
# Author: aurelien.esnard@u-bordeaux.fr

from model import *
import pygame
import socket
import errno

################################################################################
#                          NETWORK SERVER CONTROLLER                           #
################################################################################

class NetworkServerController:

    def __init__(self, model, port, conn_client, nbPlayer):
        self.model = model
        self.port = port
        self.conn_client = conn_client
        self.nbPlayer = nbPlayer

    # time event

    def tick(self, dt):
        self.conn_client["Thread-1"].setblocking(False)
        self.conn_client["Thread-2"].setblocking(False)
        if (self.nbPlayer>2):
            self.conn_client["Thread-3"].setblocking(False)
        try :
            msg = self.conn_client["Thread-1"].recv(2048)
            self.conn_client["Thread-2"].send(msg)
            if (self.nbPlayer>2):
                self.conn_client["Thread-3"].send(msg)
        except socket.error as e:
            if e.args[0] == errno.EWOULDBLOCK:
                None
            else :
                print("error:", e)

        try :
            msg = self.conn_client["Thread-2"].recv(2048)
            self.conn_client["Thread-1"].send(msg)
            if (self.nbPlayer>2):
                self.conn_client["Thread-3"].send(msg)

        except socket.error as e:
            if e.args[0] == errno.EWOULDBLOCK:
                None
            else :
                print("error:", e)
        if (self.nbPlayer>2):
            try :
                msg = self.conn_client["Thread-3"].recv(2048)
                self.conn_client["Thread-2"].send(msg)
                self.conn_client["Thread-1"].send(msg)
            except socket.error as e:
                if e.args[0] == errno.EWOULDBLOCK:
                    return True
                else :
                    print("error:", e)
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
            coup = self.socket.recv(1024)
            exec(coup.decode())
        except socket.error as e:
            if e.args[0] == errno.EWOULDBLOCK:
                return True
            else :
                print("error:", e)
        return True
