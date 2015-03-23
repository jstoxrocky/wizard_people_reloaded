# -*- coding=utf -*-

# from Queue import Empty
# from time import sleep

# class Game(object):
#     def __init__(self, queue):
#         self.queue = queue

#     def run(self):
#         while True:
#             message = None

#             try:
#                 message = self.queue.get_nowait()
#             except Empty:
#                 print("--- sleeping")
#                 sleep(0.1)

#             if message == "stop":
#                 print("!!! stopped!")
#                 break

#             if message:
#                 print("<-- got message: {}".format(message))


#             # update_badguys_position()
#             #
            


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
    def __init__(self,type):

        self.health = 1
        self.x = 100
        self.y = 100
        self.dx = 0
        self.dy = 0
        self.type = type
        self.width = 35
        self.height = 35
        self.speed = 5


    def move(self,dy,dx):

        self.x += dx
        self.y += dy

    def to_json(self):

        return {"health":self.health, "x":self.x, "y":self.y, "type":self.type, "dx":self.dx, "dy":self.dy, "width":self.width, "height":self.height}







class Room(object):

    def __init__(self):

        self.players = 0
        self.badguys = 10
        self.y = 0
