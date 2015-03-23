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
from game import Player, Badguy, Room


#start me up!
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


#FLASK
@app.route('/')
def index():
    return render_template('main.html')


@socketio.on('connect', namespace='/test')
def connectFunc():
    msg = "New Connection."
    emit('connection_response', {"msg":msg}, broadcast=True,) 



@socketio.on('create_canvas_request', namespace='/test')
def createCanvasFunc(d):
    msg = "Drawing canvas."

    current_app.room = Room()

    current_app.badguy_list = []
    current_app.badguy_list.append(Badguy('goblin'))
    current_app.badguy_list.append(Badguy('rat'))

    emit('create_canvas_response', {"msg":msg}, broadcast=True,) 




@socketio.on('get_game_state_request', namespace='/test')
def createCanvasFunc(d):
    msg = "Updating canvas."

    badguy_json = []
    for badguy in current_app.badguy_list:
        badguy_json.append(badguy.to_json())

    emit('get_game_state_response', {"msg":msg, "badguy_json":badguy_json}, broadcast=True,) 



if __name__ == '__main__':
    socketio.run(app, host= '0.0.0.0', port=6020)