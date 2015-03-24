# -*- coding: utf-8 -*- 

#needed for debug mode to work!
from gevent import monkey
monkey.patch_all()

#do some imports!
from flask import Flask, render_template, request, jsonify, current_app
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
    msg = "New Connection."
    emit('connection_response', {"msg":msg}, broadcast=True,) 

# @app.route("/message/<message>")
# def send_message(message):
#     print("--> sending message: {}".format(message))

#     queue.put_nowait(message)
#     return "ok"



def broadcast_game_state(data):
    socketio.emit('get_game_state_response', data) 


@app.before_first_request
def initialize_game():

    game = Game(queue, broadcast_game_state)

    thread = Thread(target=game.run)
    thread.start()
    current_app.game = game




if __name__ == '__main__':
    socketio.run(app, host= '0.0.0.0', port=6020)
