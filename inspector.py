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
set up inspector logging
"""
inspector_logger = logging.getLogger()
inspector_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s :: %(levelname)s :: %(message)s", "%H:%M:%S")
# file
if os.path.exists("./logs/inspector.log"):
    os.remove("./logs/inspector.log")
file_handler = RotatingFileHandler('./logs/inspector.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
inspector_logger.addHandler(file_handler)
# stream
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
inspector_logger.addHandler(stream_handler)

class Player():

    def __init__(self):
        self.end = False
        # self.old_question = ""
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
        self.map = [[] for i in range(0, 10)]
        [self.map[char['position']].append(char['color']) for char in self.game_state['characters'] if char['suspect'] is True]

    def get_isolated_characters(self):
        characters = [0] * len(self.data)
        minimum_indexes = []

        for i in range(len(self.data)):
            for case in self.map:
                if self.data[i]["color"] in case:
                    characters[i] = len(case)

        minimum = min(characters)        
        [minimum_indexes.append(i) for i in range(len(characters)) if characters[i] == minimum]

        return minimum_indexes

    def select_character(self):
        isolated_characters = self.get_isolated_characters()
        choice = random.choice(isolated_characters)
        print(choice)
        return choice

    def select_position(self):
        pass

    def answer(self, question):
        # work
        self.data = question["data"]
        self.game_state = question["game state"]
        self.question = question["question type"]
        self.set_map_positions()
        print(question["question type"])
        print(self.map)
        print(self.data)
        response_index = random.randint(0, len(self.data) - 1)
        if self.question == "select character":
            self.select_character()
        elif self.question == "select position":
            self.select_position()
        print("------------")
        # log
        inspector_logger.debug("|\n|")
        inspector_logger.debug("inspector answers")
        inspector_logger.debug(f"question type ----- {question['question type']}")
        inspector_logger.debug(f"data -------------- {self.data}")
        inspector_logger.debug(f"response index ---- {response_index}")
        inspector_logger.debug(f"response ---------- {self.data[response_index]}")
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
