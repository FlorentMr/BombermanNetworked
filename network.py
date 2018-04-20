# -*- coding: Utf-8 -*
# Author: aurelien.esnard@u-bordeaux.fr

from model import *
import pygame

################################################################################
#                          NETWORK SERVER CONTROLLER                           #
################################################################################

class NetworkServerController:

    def __init__(self, model, port):
        self.model = model
        self.port = port

    # time event

    def tick(self, dt):

        return True

################################################################################
#                          NETWORK CLIENT CONTROLLER                           #
################################################################################

class NetworkClientController:

    def __init__(self, model, host, port, nickname, socket):
        self.model = model
        self.host = host
        self.port = port
        self.nickname = nickname
        self.socket = socket

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
            self.socket.send(("model.move_character('Player 2'," + str(direction) + ")").encode())
        return True


    def keyboard_move_character_Player_2(self):
        print("=> event \"keyboard move direction\" {}".format(DIRECTIONS_STR[direction]))
        msg= self.socket.recv(2048)
        print (msg)
        return True

    def keyboard_drop_bomb(self):
        print("=> event \"keyboard drop bomb\"")
        if not self.nickname: return True
        nickname = self.nickname
        self.model.drop_bomb(nickname)
        return True

    # time event

    def tick(self, dt):

        return True
