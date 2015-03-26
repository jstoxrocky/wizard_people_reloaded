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


    with app.app_context():
        if not current_app.game:
            return
        
        session['id'] = current_app.id_count
        msg = "New Connection: {}.".format(session['id'])
        current_app.id_count += 1
        emit('connection_response', {"msg":msg, "world_width":current_app.game.world_width, "world_height":current_app.game.world_height}, broadcast=True,) 




@socketio.on('keypress_request')
def keypress_func(d):

    d['id'] = session['id']
    queue.put_nowait(d)
    emit('key_press_response', broadcast=True,) 




def broadcast_game_state(data):
    socketio.emit('get_game_state_response', data) 


@app.before_first_request
def initialize_game():

    game = Game(queue, broadcast_game_state)

    thread = Thread(target=game.run)
    thread.start()
    current_app.game = game
    current_app.id_count = 0




if __name__ == '__main__':


    with app.app_context():
        current_app.game = None
    
    socketio.run(app, host= '0.0.0.0', port=6020)
