# -*- coding=utf -*-

from __future__ import print_function

from random import randint
from Queue import Empty
from time import sleep

TILE_WIDTH = 500
TILE_HEIGHT = 500
MAP_WIDTH = 15
MAP_HEIGHT = 10

class Game(object):
    def __init__(self, queue, broadcast_state_function):
        self.queue = queue

        self.world_width = MAP_WIDTH*TILE_WIDTH
        self.world_height = MAP_HEIGHT*TILE_HEIGHT

        self.room = Room()
                
        self.broadcast_state = broadcast_state_function

    def run(self):

        game_counter = 0
        while True:


            game_counter += 1
            message = None

            try:
                
                message = self.queue.get(timeout=0.02)
                

            except Empty:
                
                message = {}

                # print("SLEEPING after {} messages".format(count))
                # count = 0
                # sleep(0.1)

            if message == "stop":
                print("!!! stopped!")
                break

            if message:
                print("<-- got message: {}".format(message))



            if message.get('type') == 'player_movement':
                self.issue_commands_to_players(message['dy'],message['dx'])
                self.move_characters(self.room.player_list)


            if game_counter % 5 == 0:

                self.run_game_step()
                # game_counter = 0





    def run_game_step(self):

        msg = "Updating world."

        self.make_badguy_decisions()
        self.correct_badguy_decisions_for_collisions_with_canvas_bounds()
        self.correct_badguy_decisions_for_collisons_with_rectangles()
        self.move_characters(self.room.badguy_list)

        badguy_json = self.all_list_to_json(self.room.badguy_list)
        rect_json = self.all_list_to_json(self.room.rect_list)
        player_json  = self.all_list_to_json(self.room.player_list)

        self.broadcast_state({"msg":msg, "badguy_json":badguy_json, "rect_json":rect_json, "player_json":player_json}) 







    def all_list_to_json(self, item_list):

        list_of_json = []
        for item in item_list:
            list_of_json.append(item.to_json())

        return list_of_json

    def issue_commands_to_players(self, dy, dx):
        for player in self.room.player_list:
            player.dx = dx*player.speed
            player.dy = dy*player.speed


    def make_badguy_decisions(self):
        
        for badguy in self.room.badguy_list:
            badguy.action()


    def correct_badguy_decisions_for_collisions_with_canvas_bounds(self):

        for badguy in self.room.badguy_list:
            if badguy.x + badguy.dx <= 0 or badguy.x + badguy.dx + badguy.width >= self.room.width:
                badguy.dy = badguy.dy
                badguy.dx = -badguy.dx

        for badguy in self.room.badguy_list:
            if badguy.y + badguy.dy <= 0 or badguy.y + badguy.dy + badguy.height >= self.room.height:
                badguy.dy = -badguy.dy
                badguy.dx = badguy.dx


    def rectangle_on_rectangle_collision(self, character, rect):

        return character.x + character.dx < rect.x + rect.width and \
           character.x + + character.dx + character.width > rect.x and \
           character.y + character.dy < rect.y + rect.height and \
           character.height + character.y + character.dy > rect.y


    def correct_badguy_decisions_for_collisons_with_rectangles(self):
        
        for rect in self.room.rect_list:
            for badguy in self.room.badguy_list:

                nine_oclock = badguy.x + badguy.dx < rect.x and badguy.x + badguy.dx + badguy.width > rect.x
                three_oclock = badguy.x + badguy.dx < rect.x + rect.width and badguy.x + badguy.dx + badguy.width > rect.x + rect.width
                twelve_oclock = badguy.y + badguy.dy < rect.y and badguy.y + badguy.dy + badguy.height > rect.y
                six_oclock = badguy.y + badguy.dy < rect.y + rect.height and badguy.y + badguy.dy + badguy.height > rect.y + rect.height


                if self.rectangle_on_rectangle_collision(badguy, rect):

                    if nine_oclock or three_oclock:
                        badguy.dx = -badguy.dx
                    if twelve_oclock or six_oclock:
                        badguy.dy = -badguy.dy




    def move_characters(self, character_list):
        for character in character_list:
            character.move()













class Player(object):
    def __init__(self, x, y):

        self.health = 3
        self.x = x
        self.y = y
        self.points = 0
        self.dx = 0
        self.dy = 0
        self.y_direction = 1
        self.x_direction = 1
        self.width = TILE_WIDTH/2.0
        self.height = TILE_HEIGHT/2.0 
        self.speed = 10

    def move(self):

        self.x += self.dx
        self.y += self.dy

        if self.dx >= 0:
            self.x_direction = 1
        else:
            self.x_direction = -1

        if self.dy >= 0:
            self.y_direction = 1
        else:
            self.y_direction = -1

    def attack(self):
        #do some attacking
        pass

    def to_json(self):

        return {"health":self.health, "x":self.x, "y":self.y, "points":self.points, "dx":self.dx, "dy":self.dy, "width":self.width, "height":self.height}




class Badguy(object):

    def __init__(self,type, x, y):

        self.health = 1
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.type = type
        self.y_direction = 1
        self.x_direction = 1
        
        if type=='goblin':
            self.speed = 8
            self.width = TILE_WIDTH/2.0
            self.height = TILE_HEIGHT/2.0 
            self.action = self.patrol

        elif type=='rat':
            self.speed = 4
            self.width = TILE_WIDTH/2.0
            self.height = TILE_HEIGHT/3.5 
            self.action = self.explore

    def patrol(self):

        self.dy=randint(-2,2)
        self.dx=self.x_direction*self.speed

    def explore(self):

        self.dy=self.y_direction*(self.speed + randint(-5,5))
        self.dx=self.x_direction*(self.speed*3 + randint(0,5))


    def move(self):

        self.x += self.dx
        self.y += self.dy

        if self.dx >= 0:
            self.x_direction = 1
        else:
            self.x_direction = -1

        if self.dy >= 0:
            self.y_direction = 1
        else:
            self.y_direction = -1

    def to_json(self):

        return {"health":self.health, "x":self.x, "y":self.y, "type":self.type, "dx":self.dx, "dy":self.dy, "width":self.width, "height":self.height}




class Rect(object):

    def __init__(self, x, y):

        self.width = TILE_WIDTH
        self.height = TILE_HEIGHT
        self.x = x
        self.y = y
        self.color = "#855E42"

    def to_json(self):

        return {"x":self.x, "y":self.y, "width":self.width, "height":self.height, "color":self.color}


class Room(object):

    def __init__(self):
        #       000000000011111
        #       012345678901234
        room = "               " \
               "  xxx          " \
               "  x x   g      " \
               "  xxx          " \
               "        p       " \
               "  xxxxxxx      " \
               "  x            " \
               "  x     x      " \
               "  xxxxxxx      " \
               "               "

        self.width = TILE_WIDTH * MAP_WIDTH
        self.height = TILE_HEIGHT * MAP_HEIGHT

        self.build_room(room)
        
    def build_room(self, room_map):

        self.rect_list = []
        self.badguy_list = []
        self.player_list = []

        for x in range(0, MAP_WIDTH):
            for y in range(0, MAP_HEIGHT):
                item = room_map[y*MAP_WIDTH + x]


                if item == 'x':
                    # TODO: rename to Wall
                    rect = Rect(x * TILE_WIDTH, y * TILE_HEIGHT)
                    self.rect_list.append(rect)
                elif item == 'r':
                    self.badguy_list.append(Badguy('rat', x*TILE_WIDTH, y*TILE_HEIGHT))
                elif item == 'g':
                    self.badguy_list.append(Badguy('goblin', x*TILE_WIDTH, y*TILE_HEIGHT))
                elif item == 'p':
                    self.player_list.append(Player(x*TILE_WIDTH, y*TILE_HEIGHT))






