# -*- coding: utf-8 -*- 

#needed for debug mode to work!
from gevent import monkey
monkey.patch_all()

#do some imports!
from flask import Flask, render_template, request, jsonify, current_app, session
from flask.ext.socketio import SocketIO, emit
import urllib, json
# from Queue import Empty
# # from time import sleep

#get game classes
from threading import Thread
from Queue import Queue
from game import Game, Player, Badguy, Room


#start me up!
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

queue = Queue()



#FLASK
@app.route('/')
def index():
    return render_template('main.html')


@socketio.on('connect')
def on_connect():

    # with app.app_context():
    #     if not current_app.id_count:
    #         return 

    session['id'] = current_app.id_count
    msg = "New Connection: {}.".format(session['id'])
    current_app.id_count += 1

    emit('connection_response', {"msg":msg, "player_chosen_colors_dict":current_app.player_chosen_colors_dict}, broadcast=True,) 

@socketio.on('keypress_request')
def keypress_func(d):

    if session.get('id') is not None:
        d['id'] = session['id']
        queue.put_nowait(d)



@socketio.on('player_choose_request')
def player_choose_func(d):

        msg = "Player {} chooses {}.".format(session['id'],d['col'])

        current_app.player_to_color_dict[session['id']] = d['col']

        player_chosen_colors_dict = {'red':0,'blu':0,'gre':0,'yel':0}

        for val in current_app.player_to_color_dict.values():
            player_chosen_colors_dict[val] += 1
        
        emit('player_choose_response', {"msg":msg, "player_chosen_colors_dict":player_chosen_colors_dict,}, broadcast=True,) 




def broadcast_game_state(data):
    socketio.emit('get_game_state_response', data) 



@socketio.on('start_game_request')
def start_game_func(d):

    for key in current_app.player_to_color_dict.keys():
        current_app.game.add_player(id=key,color=current_app.player_to_color_dict[key])

    msg = "Starting game."
    thread = Thread(target=current_app.game.run)
    thread.start()

    emit('start_game_response', {"msg":msg, "world_width":current_app.game.world_width, "world_height":current_app.game.world_height}, broadcast=True,) 




@socketio.on('reset_game_request')
def reset_game_func(d):

    msg = "Resetting game"

    queue.put_nowait({"type":"STOP"})
    game = Game(queue, broadcast_game_state)
    current_app.game = game

    current_app.id_count = 0
    current_app.player_to_color_dict = {}
    current_app.player_chosen_colors_dict = {'red':0,'blu':0,'gre':0,'yel':0}

    emit('connection_response', {"msg":msg, "player_chosen_colors_dict":current_app.player_chosen_colors_dict}, broadcast=True,) 





@app.before_first_request
def initialize_game():

    game = Game(queue, broadcast_game_state)
    current_app.game = game
    current_app.player_chosen_colors_dict = {'red':0,'blu':0,'gre':0,'yel':0}
    current_app.id_count = 0
    current_app.player_to_color_dict = {}




if __name__ == '__main__':


    with app.app_context():
        current_app.game = None
    
    socketio.run(app, host= '0.0.0.0', port=5000)
