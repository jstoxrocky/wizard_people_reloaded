#needed for debug mode to work!
from gevent import monkey
monkey.patch_all()

#do some imports!
from flask import Flask, render_template, request, jsonify, session
from flask.ext.socketio import SocketIO, emit
import urllib, json
from random import randint
import threading

#start me up!
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

ipDict = {}
rectList = []
prizeList = []
baddieList = []
playerCount = 0
canvasDim = {}
ipList = []



#FLASK
@app.route('/')
def index():
	return render_template('main.html')


# @app.route('/joeyendpoint', methods=['POST'])
# def funnelFunc():

# 	data = json.loads(request.get_data())
# 	a = data['a']

# 	return jsonify({"result":int(a)**2})




@socketio.on('connect', namespace='/test')
def connectFunc():

	global ipList
	ip = request.remote_addr
	ipList.append(ip)
	msg = "New connection from {ip}".format(ip=ip)
	emit('connectPush', {"msg":msg}, broadcast=True,) 


@socketio.on('createCanvasRequest', namespace='/test')
def createCanvasFunc(d):
	ip = request.remote_addr

	global ipDict
	global rectList
	global prizeList
	global baddieList
	global playerCount	
	global canvasDim
	rectList = []
	prizeList = []
	baddieList = []
	canvasDim = {}

	canvasDim['w'] = d['w']
	canvasDim['h'] = d['h']

	colorList = ['#999999','#35373b', '#8C8C8C', '#212121', "#4f4f4f"]
	googleColorList = ['#0266C8', '#F90101', '#F2B50F', '#00933B']
	
	for i in range(0,9):
		rectList.append(
			{"x":randint(0,d['w']),
			"y":randint(0,d['h']),
			"w":randint(50,d['w']/2),
			"h":randint(50,d['h']/2),
			"c":colorList[randint(0,len(colorList)-1)],
			}
		)

	for i in range(0,25):

		temp = {"x":randint(100,d['w']-100),
			"y":randint(100,d['h']-100),
			"w":25,
			"h":25,
			"c":'#F2B50F',
			}

		c = 0
		for rect in rectList:
			if sqOnSqCollision(temp, rect):
				c += 1

		if c==0:
			prizeList.append(temp)
				




	for i in range(0,20):
		baddieList.append(
			{"x":randint(0,d['w']),
			"y":randint(0,d['h']),
			"w":25,
			"h":25,
			"c":'#FF69B4',
			}
		)	




	circleDict = {
		"x": 10,
		"y": 10,
		"r": 10,
		"c": googleColorList[playerCount]

	}

	playerCount += 1
	if playerCount == 4:
		playerCount = 0

	ipDict[ip] = {"circleDict": circleDict}

	msg = "New canvas request from {ip}".format(ip=ip)
	emit('createCanvasPush', {"msg":msg, "rectList":rectList, "prizeList":prizeList, "baddieList":baddieList, "circleDict": circleDict, "ipDict": ipDict, "ip":ip}, broadcast=True,) 

@socketio.on('keypressRequest', namespace='/test')
def keypressFunc(d):

	global ipDict
	global rectList
	global prizeList

	if not prizeList:
		refreshGlobals()
		msg = "Global variables refreshed."
		emit('refreshGlobalsPush', {"msg":msg}, broadcast=True,) 

	ip = request.remote_addr
	
	#incrememnt move
	ipDict[ip]['circleDict']['x'] += d['dx']
	ipDict[ip]['circleDict']['y'] += d['dy']

	#create boundaries for player on canvas
	# xboundBool = (ipDict[ip]['circleDict']['x'] < 0 or ipDict[ip]['circleDict']['x'] > canvasDim['w'])
	# yboundBool = (ipDict[ip]['circleDict']['y'] < 0 or ipDict[ip]['circleDict']['y'] > canvasDim['h'])

	if (ipDict[ip]['circleDict']['x'] < 0 or ipDict[ip]['circleDict']['x'] > canvasDim['w']):
		while (ipDict[ip]['circleDict']['x'] < 0 or ipDict[ip]['circleDict']['x'] > canvasDim['w']):
			sign = d['dx']/abs(d['dx'])
			ipDict[ip]['circleDict']['x'] -= sign

	if (ipDict[ip]['circleDict']['y'] < 0 or ipDict[ip]['circleDict']['y'] > canvasDim['h']):
		while (ipDict[ip]['circleDict']['y'] < 0 or ipDict[ip]['circleDict']['y'] > canvasDim['h']):
			sign = d['dy']/abs(d['dy'])
			ipDict[ip]['circleDict']['y'] -= sign




	#create boundaries for player on rectangles
	for rect in rectList:
		if collision(ipDict[ip]['circleDict'], rect):

			while collision(ipDict[ip]['circleDict'], rect):
				# ipDict[ip]['circleDict']['x'] -= d['dx']
				# ipDict[ip]['circleDict']['y'] -= d['dy']

				if d['dx'] != 0:
					sign = d['dx']/abs(d['dx'])
					ipDict[ip]['circleDict']['x'] -= sign
				else:
					sign = d['dy']/abs(d['dy'])
					ipDict[ip]['circleDict']['y'] -= sign



	#create collison for prizes
	for index, prize in enumerate(prizeList):
		if collision(ipDict[ip]['circleDict'], prize):
			prizeList.pop(index)
			c = ipDict[ip].get('score', 0)
			ipDict[ip]['score'] = c + 1



	# create collison for prizes
	for index, baddie in enumerate(baddieList):

		if collision(ipDict[ip]['circleDict'], baddie):
			baddieList.pop(index)
			ipDict[ip]['circleDict']['r'] -= 4 

			if ipDict[ip]['circleDict']['r'] <= 0:

				refreshGlobals()

				msg = "Global variables refreshed."
				emit('refreshGlobalsPush', {"msg":msg}, broadcast=True,) 


		# baddie['x'] += randint(-10,10)
		# baddie['y'] += randint(-10,10)





	emit('keypressPush', {"ipDict":ipDict, "ip":ip, "prizeList":prizeList, "baddieList":baddieList}, broadcast=True,) 


@socketio.on('refreshGlobalsRequest', namespace='/test')
def refreshGlobalsFunc(d):

	refreshGlobals()
	msg = "Global variables refreshed."
	emit('refreshGlobalsPush', {"msg":msg}, broadcast=True,) 


def refreshGlobals():

	global ipDict
	global rectList
	global playerCount
	global prizeList
	global baddieList

	ipDict = {}
	rectList = []
	prizeList = []
	baddieList = []
	playerCount = 0


def sqOnSqCollision(rect1, rect2):

	return rect1['x'] < rect2['x'] + rect2['w'] and \
	   rect1['x'] + rect1['w'] > rect2['x'] and \
	   rect1['y'] < rect2['y'] + rect2['h'] and \
	   rect1['h'] + rect1['y'] > rect2['y']


def collision(circle, rect):

		distX = abs(circle['x'] - rect['x'] - rect['w'] / 2.0)
		distY = abs(circle['y'] - rect['y'] - rect['h'] / 2.0)

		if distX > rect['w']/2.0 + circle['r']:
			return False
		if distY > rect['h']/2.0 + circle['r']:
			return False

		if distX <= rect['w']/2.0:
			return True 
		if distY <= rect['h']/2.0:
			return True

		dx = distX - rect['w'] / 2.0
		dy = distY - rect['h'] / 2.0

		return dx * dx + dy * dy <= (circle['r'] * circle['r'])

@socketio.on('incrementBagGuysPositionRequest', namespace='/test')
def incrementBagGuysPositionFunc(d):

	global baddieList
	global ipDict
	global ipList

	ip = request.remote_addr

	if ip == ipList[0]:

		for index, baddie in enumerate(baddieList):

			if collision(ipDict[ip]['circleDict'], baddie):
				baddieList.pop(index)
				ipDict[ip]['circleDict']['r'] -= 4 

				if ipDict[ip]['circleDict']['r'] <= 0:

					global rectList
					global playerCount
					global prizeList

					ipDict = {}
					rectList = []
					prizeList = []
					baddieList = []
					playerCount = 0
					msg = "Global variables refreshed."
					emit('refreshGlobalsPush', {"msg":msg}, broadcast=True,) 

			dy = randint(0,20)
			dx = randint(0,20)
			baddie['x'] += randint(-dx,dx)
			baddie['y'] += randint(-dx,dx)

			# create boundaries for player on rectangles
			for rect in rectList:
				if sqOnSqCollision(baddie, rect):
					baddie['x'] -= dx
					baddie['y'] -= dy

		emit('incrementBagGuysPositionPush', {"ipDict": ipDict, "baddieList":baddieList, "ip": ip}, broadcast=True,) 






if __name__ == '__main__':
	socketio.run(app, host= '0.0.0.0', port=6020)