# -*- coding=utf -*-
from random import randint
from Queue import Empty
from time import sleep


class Game(object):
    def __init__(self, queue, broadcast_state_function):
        self.queue = queue

        self.room = Room()
                
        self.broadcast_state = broadcast_state_function

    def run(self):
        while True:
            message = None

            try:
                message = self.queue.get_nowait()
            except Empty:
                # print("--- sleeping")
                sleep(0.1)

            if message == "stop":
                print("!!! stopped!")
                break

            if message:
                print("<-- got message: {}".format(message))

            msg = "Updating world."
            self.update_badguys_position()
            self.correct_for_collisions_with_canvas_bounds()

            self.check_for_collison_with_rectangle()

            badguy_json = self.all_list_to_json(self.room.badguy_list)
            rect_json = self.all_list_to_json(self.room.rect_list)



            self.broadcast_state({"msg":msg, "badguy_json":badguy_json, "rect_json":rect_json}) 

            

    def update_badguys_position(self):
        
        for badguy in self.room.badguy_list:
            badguy.action()


    def all_list_to_json(self, item_list):

        list_of_json = []
        for item in item_list:
            list_of_json.append(item.to_json())

        return list_of_json

    def correct_for_collisions_with_canvas_bounds(self):

        for badguy in self.room.badguy_list:
            if badguy.x <= 0 or badguy.x + badguy.width >= self.room.width:

                # badguy.move(dy=badguy.dy,dx=-badguy.x_direction*badguy.speed)
                badguy.move(dy=badguy.dy,dx=-badguy.dx)

        for badguy in self.room.badguy_list:
            if badguy.y <= 0 or badguy.y + badguy.height >= self.room.height:

                # badguy.move(dy=-badguy.y_direction*badguy.speed,dx=badguy.dx)
                badguy.move(dy=-badguy.dy,dx=badguy.dx)




    def rectangle_on_rectangle_collision(self, rect1, rect2):

        return rect1.x < rect2.x + rect2.width and \
           rect1.x + rect1.width > rect2.x and \
           rect1.y < rect2.y + rect2.height and \
           rect1.height + rect1.y > rect2.y


    def check_for_collison_with_rectangle(self):

        for badguy in self.room.badguy_list:
            for rect in self.room.rect_list:
                if self.rectangle_on_rectangle_collision(badguy,rect):

                    badguy.x -= badguy.dx
                    if not self.rectangle_on_rectangle_collision(badguy,rect):
                        badguy.x += badguy.dx
                        badguy.move(dy=badguy.y_direction,dx=-badguy.dx)

                    else:

                        badguy.x += badguy.dx
                        badguy.move(dy=-badguy.dy,dx=badguy.x_direction)




















class Player(object):
    def __init__(self):

        self.health = 3
        self.x = 0
        self.y = 0
        self.points = 0

    def move(self,dy,dx):

        self.x += dx
        self.y += dy

    def attack(self):
        #do some attacking
        pass

    def to_json(self):

        return {"health":self.health, "x":self.x, "y":self.y, "points":self.points}




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
            self.width = 50
            self.height = 50
            self.action = self.patrol

        elif type=='rat':
            self.speed = 4
            self.width = 50
            self.height = 20
            self.action = self.explore

    def patrol(self):

        self.move(dy=randint(-2,2),dx=self.x_direction*self.speed)

    def explore(self):

        self.move(dy=self.y_direction*(self.speed + randint(0,5)),dx=self.x_direction*(self.speed*3 + randint(0,5)))


    def move(self,dy,dx):

        self.dx = dx
        self.dy = dy
        self.x += dx
        self.y += dy

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


TILE_WIDTH = 100
TILE_HEIGHT = 100
MAP_WIDTH = 15
MAP_HEIGHT = 10


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
               " x  x        xx" \
               " x  x g   xxxxx" \
               " xxxx      xxxx" \
               "    xxxx       " \
               " r       xxxx  " \
               " xxxx   xxxr   " \
               " x  x g xxx    " \
               " x      xxx    " \
               "    x     x    "

        self.width = TILE_WIDTH * MAP_WIDTH
        self.height = TILE_HEIGHT * MAP_HEIGHT

        self.build_room(room)
        
    def build_room(self, room_map):

        self.rect_list = []
        self.badguy_list = []
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







