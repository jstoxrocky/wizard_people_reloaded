# -*- coding: utf-8 -*- 

# from __future__ import print_function

from random import uniform, randint
from Queue import Empty
from time import sleep, time

MAP_WIDTH = 30
MAP_HEIGHT = 25

class Game(object):
    def __init__(self, queue, broadcast_state_function):

        self.queue = queue
        self.broadcast_state = broadcast_state_function
        self.reset()

    def run(self):

        self.state = "running"

        game_counter = 0
        while True:

            if self.state == "over":
                self.reset()
                self.status == "running"
                break

            game_counter += 1
            message = None

            try:
                message = self.queue.get(timeout=0.005)
            except Empty:
                message = {}

            if message.get('type') == "STOP":

                break

            if message.get('type') == 'player_movement':

                self.issue_commands_to_players(message['dy'],message['dx'],message['id'])
                self.correct_character_decisions_for_collisions_with_canvas_bounds(self.room.player_list)
                self.correct_character_decisions_for_collisons_with_rectangles(self.room.player_list)
                self.move_players(self.room.player_list, message['id'])

            if message.get('type') == 'attack':

                self.create_orbs_for_players(message['attack_x_direction'],message['attack_y_direction'],message['id'])

            if message.get('type') == 'build':

                self.add_player_built_walls_to_rect_list(message['id'])

            if game_counter % 5 == 0:

                self.run_game_step()



    def make_badguy_decisions(self):
        
        for badguy in self.room.badguy_list:

            target_player = self.check_if_badguys_close_enough_to_chase(badguy)

            if target_player:

                badguy.chase(target_player)

            else:

                badguy.action()

                    
    def check_if_badguys_close_enough_to_chase(self,badguy):

        for player in self.room.player_list:

            xdif = badguy.x - player.x
            ydif = badguy.y - player.y
            eucDist = (xdif**2 + ydif**2)**0.5
            if eucDist <= 3:
                return player

        return None



    def reset(self):
        
        self.world_width = MAP_WIDTH
        self.world_height = MAP_HEIGHT
        self.room = Room()
        self.state = "init"

        self.id_count = 0
        self.player_to_color_dict = {}
        self.player_chosen_colors_dict = {'red':0,'blu':0,'gre':0,'yel':0}
        

    def add_player(self,id, color):
        self.room.player_list.append(Player(1, 1, id, color))

    def remove_dead_players(self):

        for player in self.room.player_list:
            if player.is_dead:
                self.room.player_list.remove(player)


    def run_game_step(self):

        self.make_badguy_decisions()
        self.correct_character_decisions_for_collisions_with_canvas_bounds(self.room.badguy_list)
        self.correct_character_decisions_for_collisons_with_rectangles(self.room.badguy_list)
        self.move_characters(self.room.badguy_list)
        
        self.update_orb_position()
        self.remove_orb_if_collisions_with_canvas_bounds()
        self.remove_orb_if_collision_with_walls()

        self.remove_badguy_if_collision_with_orb()
        self.update_player_health()
        self.remove_dead_players()


        if self.no_more_players_left or self.no_more_badguys_left:
            self.state = "over"

        badguy_json = self.all_list_to_json(self.room.badguy_list)
        rect_json = self.all_list_to_json(self.room.rect_list)
        player_json  = self.all_list_to_json(self.room.player_list)
        orb_json  = self.all_list_to_json(self.room.orb_list)
        bone_json  = self.all_list_to_json(self.room.bone_list)
        room_json = self.room.to_json()


        self.broadcast_state({"badguy_json":badguy_json, 
                              "rect_json":rect_json, 
                              "player_json":player_json, 
                              "orb_json":orb_json, 
                              "room_json":room_json,
                              "game_over":self.state == "over",
                              "bone_json":bone_json}) 




    def add_player_built_walls_to_rect_list(self, id):

        for player in self.room.player_list:
            if player.id == id:
                self.room.rect_list.append(player.build_wall())     


    def create_orbs_for_players(self, orb_x_direction, orb_y_direction, id):



        for player in self.room.player_list:

            if player.id == id:

                if player.can_attack:

                    player_y_center = (player.y + player.y + player.height ) / 2.0
                    player_x_center = (player.x + player.x + player.width) / 2.0

                    orb_x_center = player_x_center + orb_x_direction*player.width
                    orb_y_center = player_y_center + orb_y_direction*player.height

                    player.last_attack_at = time()

                    if not(orb_x_direction == 0 and orb_y_direction == 0):

                        self.room.orb_list.append(AttackOrb(orb_x_center, orb_y_center, orb_x_direction, orb_y_direction, player.color, player.id))

    @property
    def no_more_players_left(self):
        return len(self.room.player_list) <= 0

    @property
    def no_more_badguys_left(self):
        return len(self.room.badguy_list) <= 0

    def update_orb_position(self):

        for orb in self.room.orb_list:

            orb.dy = orb.y_direction*orb.speed
            orb.dx = orb.x_direction*orb.speed
            orb.move()


    def remove_orb_if_collisions_with_canvas_bounds(self):

        for orb in self.room.orb_list:

            if orb.x + orb.dx <= 0 or orb.x + orb.dx + orb.width >= self.room.width:
                self.room.orb_list.remove(orb)

            elif orb.y + orb.dy <= 0 or orb.y + orb.dy + orb.width >= self.room.height:
                self.room.orb_list.remove(orb)


    def remove_orb_if_collision_with_walls(self):

        for rect in self.room.rect_list:
            for orb in self.room.orb_list:
                if self.circle_on_rectangle_collision(orb, rect):
                    self.room.orb_list.remove(orb)


    def remove_badguy_if_collision_with_orb(self):

            
            for badguy in self.room.badguy_list:
                for orb in self.room.orb_list:
                    if self.circle_on_rectangle_collision(orb, badguy):
                        
                        self.room.orb_list.remove(orb)
                        badguy.health -= 1

                        if badguy.health <= 0:
                            self.room.badguy_list.remove(badguy)
                            self.room.bone_list.append(Bone(badguy.x,badguy.y))

                            for player in self.room.player_list:
                                if player.id == orb.shooter_id:
                                    player.points += badguy.point_value

                            break





    def all_list_to_json(self, item_list):

        list_of_json = []
        for item in item_list:
            list_of_json.append(item.to_json())

        return list_of_json


    def issue_commands_to_players(self, dy, dx, id):

        for player in self.room.player_list:
            if player.id == id:
                player.dx = dx*player.speed
                player.dy = dy*player.speed





    def correct_character_decisions_for_collisions_with_canvas_bounds(self, character_list):

        for character in character_list:
            if character.x + character.dx <= 0 or character.x + character.dx + character.width >= self.room.width:
                character.dy = character.dy
                character.dx = -character.dx

            if character.y + character.dy <= 0 or character.y + character.dy + character.height >= self.room.height:
                character.dy = -character.dy
                character.dx = character.dx


    def rectangle_on_rectangle_collision(self, character, rect):

        return character.x + character.dx < rect.x + rect.width and \
           character.x + + character.dx + character.width > rect.x and \
           character.y + character.dy < rect.y + rect.height and \
           character.height + character.y + character.dy > rect.y


    def circle_on_rectangle_collision(self, circle, rect):

        distX = abs(circle.x - rect.x - rect.width / 2.0)
        distY = abs(circle.y - rect.y - rect.height / 2.0)

        if distX > rect.width/2.0 + circle.width:
            return False
        if distY > rect.height/2.0 + circle.width:
            return False

        if distX <= rect.width/2.0:
            return True 
        if distY <= rect.height/2.0:
            return True

        dx = distX - rect.width / 2.0
        dy = distY - rect.height / 2.0

        return dx * dx + dy * dy <= (circle.width * circle.width)


    def correct_character_decisions_for_collisons_with_rectangles(self, character_list):
        
        for rect in self.room.rect_list:
            for character in character_list:

                nine_oclock = character.x + character.dx < rect.x and character.x + character.dx + character.width > rect.x
                three_oclock = character.x + character.dx < rect.x + rect.width and character.x + character.dx + character.width > rect.x + rect.width
                twelve_oclock = character.y + character.dy < rect.y and character.y + character.dy + character.height > rect.y
                six_oclock = character.y + character.dy < rect.y + rect.height and character.y + character.dy + character.height > rect.y + rect.height


                if self.rectangle_on_rectangle_collision(character, rect):

                    if nine_oclock or three_oclock:
                        character.dx = -character.dx
                    if twelve_oclock or six_oclock:
                        character.dy = -character.dy



    def update_player_health(self):

        for badguy in self.room.badguy_list:
            for player in self.room.player_list:
                if self.rectangle_on_rectangle_collision(badguy, player):
                    player.take_damage()


    def move_characters(self, character_list):
        for character in character_list:
            character.move()

    def move_players(self, character_list, id):
        for character in character_list:
            if character.id == id:
                character.move()








class AttackOrb(object):

    def __init__(self, x, y, orb_x_direction, orb_y_direction, color, id):

        self.x_direction = orb_x_direction
        self.y_direction = orb_y_direction
        self.x = x
        self.y = y
        self.width = 0.3
        self.dx = 0
        self.dy = 0
        self.speed = 0.2
        self.color = color
        self.shooter_id = id

    def to_json(self):

        return {"x_direction":self.x_direction, 
                "x":self.x, 
                "y":self.y, 
                "y_direction":self.y_direction, 
                "width":self.width, 
                "color":self.color
                }

    def move(self):

        self.x += self.dx
        self.y += self.dy




class Player(object):


    def __init__(self, x, y, id, color):

        self.health = 3
        self.hearts = u'♥♥♥'
        self.x = x
        self.y = y
        self.points = 0
        self.dx = 0
        self.dy = 0
        self.y_direction = 1
        self.x_direction = 1
        self.width = 0.8 #half of tile
        self.height = 0.8
        self.speed = 0.07 #of a tile
        self.id = id
        self.color = color
        self.last_attack_at = None
        self.last_damage_at = None
        self.wall = None

    @property
    def can_attack(self):
        return not self.last_attack_at or time() - self.last_attack_at >= 0.3

    @property
    def is_mortal(self):
        return not self.last_damage_at or time() - self.last_damage_at >= 1


    def take_damage(self, amount=1):
        if self.is_mortal:
            self.health -= amount
            self.last_damage_at = time()
            self.hearts = u'♥'*self.health + u'♡'*(3-self.health)

    @property
    def is_dead(self):
        return self.health <= 0



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

        return {"health":self.health, 
                "hearts":self.hearts,
                "x":self.x, 
                "y":self.y, 
                "points":self.points, 
                "dx":self.dx, 
                "dy":self.dy, 
                "width":self.width, 
                "height":self.height,
                "is_mortal":self.is_mortal,
                "color":self.color}

    def build_wall(self):

        return Rect(x = self.x + self.x_direction*(self.width*1.2), y = self.y, color="#000000")


class Badguy(object):

    def __init__(self,type, x, y):

        
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.type = type
        self.y_direction = randint(-1,1)
        self.x_direction = randint(-1,1)

        
        if type=='goblin':
            self.health = 1
            self.speed = 0.02
            self.width = 0.8
            self.height = 0.8 
            self.action = self.patrol
            self.point_value = 2

        elif type=='rat':
            self.health = 1
            self.speed = 0.02
            self.width = 0.8
            self.height = 0.5 
            self.action = self.explore
            self.point_value = 1

        elif type=='goblin_king':
            self.health = 3
            self.speed = 0.02
            self.width = 2.0
            self.height = 2.0
            self.action = self.patrol
            self.point_value = 5

    def patrol(self):

        self.dy=uniform(-0.05,0.05)
        self.dx=self.x_direction*self.speed

    def explore(self):

        self.dy=self.y_direction*(self.speed + uniform(-0.05,0.05))
        self.dx=self.x_direction*(self.speed*3 + uniform(0,0.05))

    def chase(self, player):

        xdif = self.x - player.x
        ydif = self.y - player.y

        if xdif > 0:
            self.dx = -(self.speed*3 )
        else:
            self.dx = (self.speed*3 )

        if ydif > 0:
            self.dy = -(self.speed*3 )
        else:
            self.dy = (self.speed*3 )




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

        return {"health":self.health, 
                "x":self.x, 
                "y":self.y, 
                "type":self.type, 
                "dx":self.dx, 
                "dy":self.dy, 
                "width":self.width, 
                "height":self.height,
                "point_value":self.point_value}




class Rect(object):

    def __init__(self, x, y, color):

        self.width = 1
        self.height = 1
        self.x = x
        self.y = y
        self.color = color

    def to_json(self):

        return {"x":self.x, "y":self.y, "width":self.width, "height":self.height, "color":self.color}



class Bone(object):

    def __init__(self,x,y):

        self.x = x
        self.y = y
        self.width = 0.5
        self.height = 0.5

    def to_json(self):
        return {"x":self.x, "y":self.y, "width":self.width, "height":self.height}


class Room(object):

    def __init__(self):
        #       000000000011111111112222222222
        #       012345678901234567891234567890
        room = "          xxxxxxx             " \
               "  xxx           x gg          " \
               "  x x   g       x             " \
               "                x        r    " \
               "                x   x         " \
               "  xxxxxxx           x r       " \
               "  x  rr x           xxxxxxxxx " \
               "  x rrr             x         " \
               "  xxxxxxxx      x   x         " \
               "         x      x             " \
               "         x      x   g         " \
               "  xxx               r         " \
               "  x x   g                     " \
               "  xxx    x      x             " \
               "         x      x             " \
               "         x      x             " \
               "         xxxxxxxxxxxxxxxxx    " \
               "         x    rrr    rr  x    " \
               "            rr    k  r   x    " \
               "         x   rr x  r     x    " \
               "xxxx  xxxxx xxxxxxxxxxxxxx    " \
               "    gg          x             " \
               "                              " \
               "                x             " \
               "                x             " \



        room_aj =  "                              " \
                   "      x           gg          " \
                   "    rrx  g                    " \
                   "  xxxxx             x         " \
                   "                    x  rr     " \
                   "  xxxxxxxxxxxxxxxxxxx         " \
                   "  x  rr         x   xxxxxx    " \
                   "  x rrr     x   x        x    " \
                   "  xxxxxxxxxxx            x    " \
                   "     x                   x    " \
                   "  x     x  g       gg    x    " \
                   "  xxxxxxxxxxxx           x    " \
                   "  x    g     x    xxxxxxxx    " \
                   "  x  g    g  x                " \
                   "  x    xxxxxxxxxxxxxxxxxxx    " \
                   "  x    x                      " \
                   "  x   xx   xxxxxxxxxxxxxxx    " \
                   "  x    x   x  rrr    rr  x    " \
                   "  xx   x   x     x   k r  x    " \
                   "       x         x       x    " \
                   "       xxxxxxxxxxxxxxxxxxx    " \
                   "    gg                        " \
                   "                 p            " \
                   "                              " \
                   "                              " \

        room_test =  "                              " \
                    "                              " \
                    "                              " \
                    "                              " \
                    "                              " \
                    "                              " \
                    "                              " \
                    "                              " \
                    "                              " \
                    "                              " \
                    "                              " \
                    "                              " \
                    "                   g          " \
                    "                              " \
                    "                              " \
                    "                              " \
                    "                              " \
                    "                              " \
                    "                              " \
                    "                              " \
                    "                              " \
                    "                              " \
                    "                              " \
                    "                              " \
                    "                              " \





        self.width = MAP_WIDTH
        self.height = MAP_HEIGHT

        self.select_color_palette()

        room_list = [room, room_aj]
        curr_room = room_list[randint(0,1)]

        self.build_room(curr_room)
        


    def select_color_palette(self):
    
        level_type_list = ['cave', 'grassy', 'icy', 'sand']
        level_number = randint(0,3)

        if level_type_list[level_number] == 'grassy':
            color_list = ['#999999','#35373b', '#8C8C8C', '#212121', "#4f4f4f"]
            bg_color = '#659D32'
        elif level_type_list[level_number] == 'cave':
            color_list = ['#42526C','#35373b', '#2F4F4F', '#212121', "#4f4f4f"]
            bg_color = '#8C8C8C'
        elif level_type_list[level_number] == 'icy':
            color_list = ['#BFEFFF','#35373b', '#82CFFD', '#212121', "#4f4f4f"]
            bg_color = '#FFFAFA'
        elif level_type_list[level_number] == 'sand':
            color_list = ['#956c4b','#905120', '#502d12', '#d4803f', "#b08563"]
            bg_color = '#edd9af'

        self.bg_color = bg_color
        self.color_list = color_list

        
    def build_room(self, room_map):

        self.rect_list = []
        self.badguy_list = []
        self.player_list = []
        self.orb_list = []
        self.bone_list = []


        for x in range(0, MAP_WIDTH):
            for y in range(0, MAP_HEIGHT):
                item = room_map[y*MAP_WIDTH + x]


                if item == 'x':
                    # TODO: rename to Wall
                    rect = Rect(x, y, color=self.color_list[randint(0,len(self.color_list)-1)])
                    self.rect_list.append(rect)
                elif item == 'r':
                    self.badguy_list.append(Badguy('rat', x, y))
                elif item == 'g':
                    self.badguy_list.append(Badguy('goblin', x, y))
                elif item == 'k':
                    self.badguy_list.append(Badguy('goblin_king', x, y))


    def to_json(self):

        return {"bg_color": self.bg_color}





