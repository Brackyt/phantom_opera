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
    
    def get_least_full_rooms(self):
        """
        Gets the nearest rooms with the lowest amount of characters
        """
        # Create a list with the number of characters in each room
        room_sizes = [len(room) for room in self.map if self.map.index(room) in self.data]
        # Get the number of characters in the room that contains the least
        if len(room_sizes) > 0 :
            size_least_rooms = min(room_sizes)
        else :
            size_least_rooms = 8
        # inspector_logger.debug("Size least room:", size_biggest_rooms)

        if size_least_rooms == 8:
            return [0]

        most_least_rooms = []
        # Create list of all the rooms with size_least_rooms number of characters
        [most_least_rooms.append(self.map.index(room)) for room in self.map if len(room) == size_least_rooms and self.map.index(room) in self.data]
        return most_least_rooms

    def get_most_full_rooms(self):
        """
        Gets the rooms with the biggest amount of characters
        """
        # Create a list with the number of characters in each room
        room_sizes = [len(room) for room in self.map if self.map.index(room) in self.data]
        # Get the number of characters in the room that contains the most
        size_biggest_rooms = max(room_sizes) if len(room_sizes) > 0 else 0
        # inspector_logger.debug("Size biggest room:", size_biggest_rooms)

        if size_biggest_rooms == 0:
            return [0]

        most_full_rooms = []
        # Create list of all the rooms with size_biggest_rooms number of characters
        [most_full_rooms.append(self.map.index(room)) for room in self.map if len(room) == size_biggest_rooms and self.map.index(room) in self.data]
        return most_full_rooms
    
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
        i = 0
        
        for char in self.data:
            if char["color"] == "grey":
                return i
            i += 1
        least_isolated_characters = self.get_least_isolated_characters()
        choice = random.choice(least_isolated_characters)
        return choice

    def select_position(self):
        """
        Gets a room that contains the lowest amount of characters
        """
        least_full_rooms = self.get_least_full_rooms()
        if least_full_rooms == [0]:
            return 0
        selected_room = random.choice(least_full_rooms)
        # fantom_logger.debug("Least full rooms:", least_full_rooms)
        # fantom_logger.debug("Selected room:", selected_room)
        return self.data.index(selected_room)

    def select_position2(self):
        """
        Gets a room that contains the biggest amount of characters
        """
        most_full_rooms = self.get_most_full_rooms()
        if most_full_rooms == [0]:
            return 0
        selected_room = random.choice(most_full_rooms)
        # inspector_logger.debug("Most full rooms:", most_full_rooms)
        # inspector_logger.debug("Selected room:", selected_room)
        return self.data.index(selected_room)

    def answer(self, question):
        # work
        self.data = question["data"]
        self.game_state = question["game state"]
        self.question = question["question type"]
        fantom_logger.debug("|\n|")
        fantom_logger.debug("fantom answers")
        

        self.set_map_positions()
        response_index = random.randint(0, len(self.data) - 1)
        if self.question == "select character":
            response_index = self.select_character()
        elif self.question == "select position":
            response_index = self.select_position()
        elif self.question == "grey character power room":
            response_index = self.select_position2()
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
