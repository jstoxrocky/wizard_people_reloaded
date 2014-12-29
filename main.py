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
playerList = []
uidCount = 0



#FLASK
@app.route('/')
def index():
	return render_template('main.html')


@socketio.on('connect', namespace='/test')
def connectFunc():

	#import global playerList and uidCount (combine with player count?)
	global playerList
	global uidCount

	#give uid equal to uidCount
	session['uid'] = uidCount
	playerList.append(session['uid'])
	uidCount += 1
	

	msg = "Player {uid} connected.".format(uid=session['uid'])
	emit('connectPush', {"msg":msg}, broadcast=True,) 





@socketio.on('createCanvasRequest', namespace='/test')
def createCanvasFunc(d):

	ip = session['uid']

	global ipDict
	global rectList
	global prizeList
	global baddieList
	global playerCount	
	global canvasDim

	canvasDim['w'] = d['w']
	canvasDim['h'] = d['h']

	#select level and colors
	#push most of this to browser
	googleColorList = ['#0266C8', '#F90101', '#F2B50F', '#00933B']
	levelList = ['cave', 'grassy', 'icy']
	levelNum = randint(0,len(levelList)-1)

	if levelList[levelNum] == 'grassy':
		colorList = ['#999999','#35373b', '#8C8C8C', '#212121', "#4f4f4f"]
		bgcolor = '#86C67C'
		baddieColor = '#87421F'
	elif levelList[levelNum] == 'cave':
		colorList = ['#42526C','#35373b', '#2F4F4F', '#212121', "#4f4f4f"]
		bgcolor = '#8C8C8C'
		baddieColor = '#86C67C'
	elif levelList[levelNum] == 'icy':
		colorList = ['#BFEFFF','#35373b', '#82CFFD', '#212121', "#4f4f4f"]
		bgcolor = '#FFFAFA'
		baddieColor = '#e5e1e1'


	#create rectangles
	rectNum = d['w']*d['h']/91022
	for i in range(0,rectNum):
		rectList.append(
			{"x":randint(0,d['w']),
			"y":randint(0,d['h']),
			"w":randint(50,d['w']/2),
			"h":randint(50,d['h']/2),
			"c":colorList[randint(0,len(colorList)-1)],
			}
		)

	#create prizes
	prizeNum = d['w']*d['h']/32768
	while len(prizeList) < prizeNum:

		temp = {"x":randint(100,d['w']-100),
			"y":randint(100,d['h']-100),
			"w":25,
			"h":25,
			}

		c = 0
		for rect in rectList:
			if sqOnSqCollision(temp, rect):
				c += 1
				break
		if c==0:
			prizeList.append(temp)
				
	baddieNum = d['w']*d['h']/100960
	while len(baddieList) < baddieNum:

		temp = {"x":randint(0,d['w']),
			"y":randint(0,d['h']),
			"w":35,
			"h":35,
			"c":baddieColor,
			}

		c = 0
		for rect in rectList:
			if sqOnSqCollision(temp, rect):
				c += 1
				break
		if c==0:
			baddieList.append(temp)

	playerDict = {
		"x": 10,
		"y": 10,
		"w": 29,
		"h": 29,
		"c": googleColorList[session['uid']],
		"r": 0,
		"id": session['uid'],
		"state": 'rest',
	}

	ipDict[ip] = playerDict

	emit('createCanvasPush', {"rectList":rectList, "prizeList":prizeList, "baddieList":baddieList, "ipDict": ipDict, "ip":ip, 'bgcolor':bgcolor}, broadcast=True,) 

@socketio.on('keypressRequest', namespace='/test')
def keypressFunc(d):

	global ipDict
	global rectList
	global prizeList
	global playerCount

	if not prizeList:
		refreshGlobals()
		msg = "Global variables refreshed."
		emit('refreshGlobalsPush', {"msg":msg}, broadcast=True,) 

	# ip = request.remote_addr
	ip = session['uid']
	
	#incrememnt move
	# ipDict[ip]['playerDict']['x'] += d['dx']
	# ipDict[ip]['playerDict']['y'] += d['dy']
	# ipDict[ip]['playerDict']['dx'] = d['dx']
	# ipDict[ip]['playerDict']['dy'] = d['dy']

	ipDict[ip]['x'] += d['dx']
	ipDict[ip]['y'] += d['dy']
	ipDict[ip]['dx'] = d['dx']
	ipDict[ip]['dy'] = d['dy']

	#create boundaries for player on canvas
	# if (ipDict[ip]['playerDict']['x'] < 0 or ipDict[ip]['playerDict']['x'] > canvasDim['w']):
	# 	while (ipDict[ip]['playerDict']['x'] < 0 or ipDict[ip]['playerDict']['x'] > canvasDim['w']):
	# 		sign = d['dx']/abs(d['dx'])
	# 		ipDict[ip]['playerDict']['x'] -= sign

	# if (ipDict[ip]['playerDict']['y'] < 0 or ipDict[ip]['playerDict']['y'] > canvasDim['h']):
	# 	while (ipDict[ip]['playerDict']['y'] < 0 or ipDict[ip]['playerDict']['y'] > canvasDim['h']):
	# 		sign = d['dy']/abs(d['dy'])
	# 		ipDict[ip]['playerDict']['y'] -= sign

	if (ipDict[ip]['x'] < 0 or ipDict[ip]['x'] > canvasDim['w']):
		while (ipDict[ip]['x'] < 0 or ipDict[ip]['x'] > canvasDim['w']):
			sign = d['dx']/abs(d['dx'])
			ipDict[ip]['x'] -= sign

	if (ipDict[ip]['y'] < 0 or ipDict[ip]['y'] > canvasDim['h']):
		while (ipDict[ip]['y'] < 0 or ipDict[ip]['y'] > canvasDim['h']):
			sign = d['dy']/abs(d['dy'])
			ipDict[ip]['y'] -= sign



	#create boundaries for player on rectangles
	for rect in rectList:
		# if sqOnSqCollision(ipDict[ip]['playerDict'], rect):
		if sqOnSqCollision(ipDict[ip], rect):

			if ipDict[ip]['state'] == 'rest': #janky hack to fix endless loop
				
				# tempDict = ipDict[ip]['playerDict'].copy()
				tempDict = ipDict[ip].copy()
				tempdy = 0
				tempdx = 0

				if d['dx'] != 0:
					tempDict['x'] = tempDict['x'] - d['dx']
					if not sqOnSqCollision(tempDict, rect):
						# print('allow movement in y direction')
						tempDict['x'] = tempDict['x'] + d['dx']
						tempdy = d['dy']
				
				if d['dy'] != 0:
					tempDict['y'] = tempDict['y'] - d['dy']
					if not sqOnSqCollision(tempDict, rect):
						# print('allow movement in x direction')
						tempDict['y'] = tempDict['y'] + d['dy']
						tempdx = d['dx']

				# while sqOnSqCollision(ipDict[ip]['playerDict'], rect):
				while sqOnSqCollision(ipDict[ip], rect):

					if d['dx'] == 0:
						#y collision only
						signx = 0
					else:
						signx = d['dx']/abs(d['dx'])
					
					
					if d['dy'] == 0:
						#x collision only
						signy = 0
					else:
						signy = d['dy']/abs(d['dy'])

					
					# ipDict[ip]['playerDict']['y'] -= signy
					# ipDict[ip]['playerDict']['x'] -= signx
					ipDict[ip]['y'] -= signy
					ipDict[ip]['x'] -= signx

				# ipDict[ip]['playerDict']['y'] += tempdy
				# ipDict[ip]['playerDict']['x'] += tempdx
				ipDict[ip]['y'] += tempdy
				ipDict[ip]['x'] += tempdx


	#create collison for prizes
	for index, prize in enumerate(prizeList):
		# if sqOnSqCollision(ipDict[ip]['playerDict'], prize):
		if sqOnSqCollision(ipDict[ip], prize):
			prizeList.pop(index)
			c = ipDict[ip].get('score', 0)
			ipDict[ip]['score'] = c + 1



	# create collison for baddies
	for index, baddie in enumerate(baddieList):

		# if sqOnSqCollision(ipDict[ip]['playerDict'], baddie) and ipDict[ip]['state'] == 'rest':
		if sqOnSqCollision(ipDict[ip], baddie) and ipDict[ip]['state'] == 'rest':
			baddieList.pop(index)
			# ipDict[ip]['circleDict']['r'] -= 4 
			# ipDict[ip]['radius'] -= 10
			# ipDict[ip]['playerDict']['w'] -= 10
			# ipDict[ip]['playerDict']['h'] -= 10
			ipDict[ip]['w'] -= 10
			ipDict[ip]['h'] -= 10

			# if ipDict[ip]['circleDict']['r'] <= 0:
			# if ipDict[ip]['playerDict']['w'] <= 0:
			if ipDict[ip]['w'] <= 0:

				# playerCount -= 1
				# if playerCount == 0:
					refreshGlobals()

					msg = "Global variables refreshed."
					emit('refreshGlobalsPush', {"msg":msg}, broadcast=True,) 





	emit('keypressPush', {"ipDict":ipDict, "ip":ip, "prizeList":prizeList, "baddieList":baddieList}, broadcast=True,) 


@socketio.on('attackRequest', namespace='/test')
def attackFunc(d):

	global ipDict
	global prizeList
	global baddieList


	#need to update x and y val with radius!!




	# ip = request.remote_addr
	ip = session['uid']

	# ipDict[ip]['playerDict']['c'] = '#ffffff'
	ipDict[ip]['state'] = 'attack'
	# ipDict[ip]['playerDict']['r'] = 40#ipDict[ip]['circleDict']['r']*3
	ipDict[ip]['r'] = 40#ipDict[ip]['circleDict']['r']*3







	# auraDict = {'x':ipDict[ip]['playerDict']['x'] + ipDict[ip]['playerDict']['w']/2, 
	# 			'y':ipDict[ip]['playerDict']['y'] + ipDict[ip]['playerDict']['h']/2, 
	# 			'r': ipDict[ip]['playerDict']['r']}

	auraDict = {'x':ipDict[ip]['x'] + ipDict[ip]['w']/2, 
				'y':ipDict[ip]['y'] + ipDict[ip]['h']/2, 
				'r': ipDict[ip]['r']}

	for index, baddie in enumerate(baddieList):


		if collision(auraDict, baddie) and ipDict[ip]['state'] == 'attack':
			# print('hi')
			baddieList.pop(index)

	for index, eachip in enumerate(ipDict.keys()):

		if eachip != ip:

			# _auraDict = {'x':ipDict[eachip]['playerDict']['x'] + ipDict[eachip]['playerDict']['w']/2, 
			# 	'y':ipDict[eachip]['playerDict']['y'] + ipDict[eachip]['playerDict']['h']/2, 
			# 	'r': ipDict[eachip]['playerDict']['r']}
			_auraDict = {'x':ipDict[eachip]['x'] + ipDict[eachip]['w']/2, 
				'y':ipDict[eachip]['y'] + ipDict[eachip]['h']/2, 
				'r': ipDict[eachip]['r']}

			if circleOncircleCollision(auraDict, _auraDict) and ipDict[ip]['state'] == 'attack':
				# print('hi')
				# baddieList.pop(index)

				# ipDict[eachip]['radius'] -= 10
				# ipDict[eachip]['playerDict']['w'] -= 10
				# ipDict[eachip]['playerDict']['h'] -= 10
				ipDict[eachip]['w'] -= 10
				ipDict[eachip]['h'] -= 10

				# if ipDict[ip]['circleDict']['r'] <= 0:
				# if ipDict[eachip]['playerDict']['w'] <= 0:
				if ipDict[eachip]['w'] <= 0:

					# playerCount -= 1
					# if playerCount == 0:
						refreshGlobals()

						msg = "Global variables refreshed."
						emit('refreshGlobalsPush', {"msg":msg}, broadcast=True,) 

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
	global uidCount
	global playerList

	ipDict = {}
	rectList = []
	prizeList = []
	baddieList = []
	playerCount = 0
	uidCount = 0
	playerList = []


def sqOnSqCollision(rect1, rect2):

	return rect1['x'] < rect2['x'] + rect2['w'] and \
	   rect1['x'] + rect1['w'] > rect2['x'] and \
	   rect1['y'] < rect2['y'] + rect2['h'] and \
	   rect1['h'] + rect1['y'] > rect2['y']

def circleOncircleCollision(circle1,circle2):

	# print(circle1['x'])
	# print(circle1['y'])
	# print(circle1['y'])

	# print(circle2['x'])
	# print(circle2['y'])
	# print(circle2['r'])



	dx = (circle1['x']) - (circle2['x']) #10+30 - (10 + 10) = 20
	dy = (circle1['y']) - (circle2['y']) #30 + 30 - (10+10) = 40
	distance = ((dx ** 2) + (dy ** 2))**0.5 # (400+1600)**0.5 = 44...



	# print(circle1['r'])
	if distance < circle1['r'] + circle2['r']: 

	    return True



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
	global playerList
	global playerCount




	# ip = request.remote_addr
	ip = session['uid']

	# for _ip in ipDict.keys():

	#return vars to normal after attack etc
	# if ipDict[ip]['playerDict']['r'] > ipDict[ip]['radius'] and ipDict[ip]['state'] == 'attack':
	# if ipDict[ip]['playerDict']['r'] > 0 and ipDict[ip]['state'] == 'attack':
	if ipDict[ip]['r'] > 0 and ipDict[ip]['state'] == 'attack':
		# print(ipDict[ip]['circleDict']['r'])
		# print(ipDict[ip]['radius'])
		# ipDict[ip]['playerDict']['r'] -=  10
		ipDict[ip]['r'] -=  10
		# ipDict[ip]['playerDict']['h'] -=  10
	else:

		# ipDict[ip]['playerDict']['c'] = ipDict[ip]['color']
		# ipDict[ip]['playerDict']['w'] = ipDict[ip]['radius']
		# ipDict[ip]['playerDict']['r'] = 0
		ipDict[ip]['r'] = 0

		ipDict[ip]['state'] = 'rest'





	# print(ip)
	# print(ipDict[ip]['circleDict']['r'])
	if ip == playerList[0]:


		for index, baddie in enumerate(baddieList):

			# for _ip in ipDict.keys():


			# if sqOnSqCollision(ipDict[ip]['playerDict'], baddie) and ipDict[ip]['state'] == 'rest':
			if sqOnSqCollision(ipDict[ip], baddie) and ipDict[ip]['state'] == 'rest':	
				# print('here')

				baddieList.pop(index)
				
				# ipDict[ip]['circleDict']['r'] -= 4 
				# ipDict[ip]['radius'] -= 10
				# ipDict[ip]['playerDict']['w'] -= 10
				# ipDict[ip]['playerDict']['h'] -= 10
				ipDict[ip]['w'] -= 10
				ipDict[ip]['h'] -= 10

				# if ipDict[ip]['circleDict']['r'] <= 0:
				# if ipDict[ip]['playerDict']['w'] <= 0:
				if ipDict[ip]['w'] <= 0:

					# playerCount -= 1
					# if playerCount == 0:
						refreshGlobals()

						msg = "Global variables refreshed."
						emit('refreshGlobalsPush', {"msg":msg}, broadcast=True,) 


			#identify if circle is near
			targetList = []
			for _ip in playerList:
				# xdif = baddie['x'] - ipDict[_ip]['playerDict']['x']
				# ydif = baddie['y'] - ipDict[_ip]['playerDict']['y']
				xdif = baddie['x'] - ipDict[_ip]['x']
				ydif = baddie['y'] - ipDict[_ip]['y']
				eucDist = (xdif**2 + ydif**2)**0.5
				if eucDist < 200:
					targetList.append(_ip)

			if targetList:
				targetList.sort()
				target_ip = targetList[0]
				# xdif = baddie['x'] - ipDict[target_ip]['playerDict']['x']
				# ydif = baddie['y'] - ipDict[target_ip]['playerDict']['y']
				xdif = baddie['x'] - ipDict[target_ip]['x']
				ydif = baddie['y'] - ipDict[target_ip]['y']
				if xdif > 0:
					ddx = -(4 + randint(0,2))
				else:
					ddx = (4 + randint(0,2))

				if ydif > 0:
					ddy = -(4 + randint(0,2))
				else:
					ddy = (4 + randint(0,2))
			
			else:

				dx = randint(0,5)
				dy = randint(0,5)

				ddx = randint(-dx,dx)
				ddy = randint(-dy,dy)

				if ddx == 0: 
					ddx += 1
				if ddy == 0:
					ddy += 1

			baddie['x'] += ddx
			baddie['y'] += ddy
			baddie['dx'] = ddx
			baddie['dy'] = ddy

			# create boundaries for player on rectangles





			for rect in rectList:
				if sqOnSqCollision(baddie, rect):


					tempDict = baddie.copy()
					tempdy = 0
					tempdx = 0

					if ddx != 0:
						tempDict['x'] = tempDict['x'] - ddx
						if not sqOnSqCollision(tempDict, rect):
							# print('allow movement in y direction')
							tempDict['x'] = tempDict['x'] + ddx
							tempdy = ddy
					
					if ddy != 0:
						tempDict['y'] = tempDict['y'] - ddy
						if not sqOnSqCollision(tempDict, rect):
							# print('allow movement in x direction')
							tempDict['y'] = tempDict['y'] + ddy
							tempdx = ddx

						baddie['x'] -= ddx - tempdx
						baddie['y'] -= ddy - tempdy

			if (baddie['x'] < 0 or baddie['x'] > canvasDim['w']):
				baddie['x'] -= ddx

			if (baddie['y'] < 0 or baddie['y'] > canvasDim['h']):
				baddie['y'] -= ddy

		emit('incrementBagGuysPositionPush', {"ipDict": ipDict, "baddieList":baddieList, "ip": ip}, broadcast=True,) 






if __name__ == '__main__':
	socketio.run(app, host= '0.0.0.0', port=6020)