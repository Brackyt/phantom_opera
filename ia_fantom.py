import json
import logging
import os
import random
import socket
from logging.handlers import RotatingFileHandler

import protocol

host = "localhost"
port = 12000
# HEADERSIZE = 10

"""
set up fantom logging
"""
fantom_logger = logging.getLogger()
fantom_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s :: %(levelname)s :: %(message)s", "%H:%M:%S")
# file
if os.path.exists("./logs/fantom.log"):
    os.remove("./logs/fantom.log")
file_handler = RotatingFileHandler('./logs/fantom.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
fantom_logger.addHandler(file_handler)
# stream
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
fantom_logger.addHandler(stream_handler)


class Player():

    def __init__(self):

        self.end = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.data = []
        self.game_state = []
        self.question_type = []
        self.map = []

    def connect(self):
        self.socket.connect((host, port))

    def reset(self):
        self.socket.close()

    def set_map_positions(self):
        """
        Creates a list with the characters in each rooms
        """
        self.map = [[] for i in range(0, 10)]
        [self.map[char['position']].append(char['color']) for char in self.game_state['characters'] if char['suspect'] is True]
    
    def get_least_isolated_characters(self):
        """
        Gets the characters in the rooms with the most amount of characters
        """
        characters = [0] * len(self.data)
        maximum_indexes = []

        for i in range(len(self.data)):
            for room in self.map:
                if self.data[i]["color"] in room:
                    characters[i] = len(room)

        maximum = max(characters)        
        [maximum_indexes.append(i) for i in range(len(characters)) if characters[i] == maximum]

        return maximum_indexes

    def select_character(self):
        """
        Gets a character to isolate
        """
        least_isolated_characters = self.get_least_isolated_characters()
        choice = random.choice(least_isolated_characters)
        return choice

    def select_position(self):
        pass

    def answer(self, question):
        # work
        self.data = question["data"]
        self.game_state = question["game state"]
        self.question = question["question type"]
        fantom_logger.debug("|\n|")
        fantom_logger.debug("inspector answers")

        self.set_map_positions()
        response_index = random.randint(0, len(self.data) - 1)
        if self.question == "select character":
            response_index = self.select_character()
        elif self.question == "select position":
            response_index = self.select_position()
        
        # log
        fantom_logger.debug(f"question type ----- {question['question type']}")
        fantom_logger.debug(f"data -------------- {self.data}")
        fantom_logger.debug(f"response index ---- {response_index}")
        fantom_logger.debug(f"response ---------- {self.data[response_index]}")
        return response_index

    def handle_json(self, data):
        data = json.loads(data)
        response = self.answer(data)
        # send back to server
        bytes_data = json.dumps(response).encode("utf-8")
        protocol.send_json(self.socket, bytes_data)

    def run(self):

        self.connect()

        while self.end is not True:
            received_message = protocol.receive_json(self.socket)
            if received_message:
                self.handle_json(received_message)
            else:
                print("no message, finished learning")
                self.end = True


p = Player()

p.run()
