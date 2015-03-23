# -*- coding: utf-8 -*- 

#needed for debug mode to work!
from gevent import monkey
monkey.patch_all()

#do some imports!
from flask import Flask, render_template, request, jsonify, current_app
from flask.ext.socketio import SocketIO, emit
import urllib, json
from random import randint

#get game classes
from threading import Thread
from Queue import Queue
from game import Player, Badguy, Room


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


# @socketio.on('connect', namespace='/test')
# def connectFunc():
#     msg = "New Connection."
#     emit('connection_response', {"msg":msg}, broadcast=True,) 

@socketio.on('connect')
def on_connect():
    msg = "New Connection."
    emit('connection_response', {"msg":msg}, broadcast=True,) 


@socketio.on('create_canvas_request')
def createCanvasFunc(d):
    msg = "Drawing canvas."

    current_app.room = Room()

    current_app.badguy_list = []
    current_app.badguy_list.append(Badguy('goblin'))
    # current_app.badguy_list.append(Badguy('rat'))

    emit('create_canvas_response', {"msg":msg}, broadcast=True,) 




# @socketio.on('get_game_state_request', namespace='/test')
# def createCanvasFunc(d):
#     msg = "Updating canvas."

#     badguy_json = []
#     for badguy in current_app.badguy_list:
#         badguy_json.append(badguy.to_json())

#     queue.put_nowait(badguy_json)

#     emit('get_game_state_response', {"msg":msg, "badguy_json":badguy_json}, broadcast=True,) 


# @app.route("/message/<message>")
# def send_message(message):
#     print("--> sending message: {}".format(message))

#     queue.put_nowait(message)
#     return "ok"

from Queue import Empty
from time import sleep

class Game(object):
    def __init__(self, queue):
        self.queue = queue

    def run(self):
        while True:
            message = None

            try:
                message = self.queue.get_nowait()
            except Empty:
                print("--- sleeping")
                sleep(0.1)

            if message == "stop":
                print("!!! stopped!")
                break

            if message:
                print("<-- got message: {}".format(message))


            update_badguys_position()

            

def update_badguys_position():

    msg = "Updating badguys."

    with app.app_context():
        badguy_json = []
        for badguy in current_app.badguy_list:
            badguy.move(dy=0,dx=badguy.speed)
            badguy_json.append(badguy.to_json())



    socketio.emit('get_game_state_response', {"msg":msg,"badguy_json":badguy_json}) 







@app.before_first_request
def initialize_game():
    game = Game(queue)

    thread = Thread(target=game.run)
    thread.start()
    current_app.game = game

if __name__ == '__main__':
    socketio.run(app, host= '0.0.0.0', port=6020)
