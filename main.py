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
uidCount = 0



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
	global uidCount

	session['uid'] = uidCount

	uidCount += 1

	# ip = request.remote_addr
	ip = session['uid']


	ipList.append(ip)
	msg = "New connection from {ip}".format(ip=ip)
	emit('connectPush', {"msg":msg}, broadcast=True,) 


@socketio.on('createCanvasRequest', namespace='/test')
def createCanvasFunc(d):
	# ip = request.remote_addr
	ip = session['uid']

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

	# colorList = ['#999999','#35373b', '#8C8C8C', '#212121', "#4f4f4f"]
	googleColorList = ['#0266C8', '#F90101', '#F2B50F', '#00933B']
	

	
	levelList = ['cave', 'grassy', 'icy']
	levelNum = randint(0,len(levelList)-1)

	if levelList[levelNum] == 'grassy':
		colorList = ['#999999','#35373b', '#8C8C8C', '#212121', "#4f4f4f"]
		bgcolor = '#86C67C'
		baddieColor = '#87421F'
	elif levelList[levelNum] == 'cave':
		# colorList = ['#2F4F4F','#607B8B','#6C7B8B','#42526C','#2F2F4F']
		colorList = ['#42526C','#35373b', '#2F4F4F', '#212121', "#4f4f4f"]
		bgcolor = '#8C8C8C'
		baddieColor = '#86C67C'
	elif levelList[levelNum] == 'icy':
		colorList = ['#BFEFFF','#35373b', '#82CFFD', '#212121', "#4f4f4f"]
		bgcolor = '#FFFAFA'
		baddieColor = '#e5e1e1'



	# print('rect') #91022
	# print(d['w']*d['h']/9)
	# print('prize') #32768
	# print(d['w']*d['h']/25)
	# print('baddie') #40960
	# print(d['w']*d['h']/20)


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

	prizeNum = d['w']*d['h']/32768
	while len(prizeList) < prizeNum:
	# for i in range(0,25):

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
				
	baddieNum = d['w']*d['h']/100960
	while len(baddieList) < baddieNum:
	# for i in range(0,20):

		temp = {"x":randint(0,d['w']),
			"y":randint(0,d['h']),
			"w":25,
			"h":25,
			"c":baddieColor,
			}

		c = 0
		for rect in rectList:
			if sqOnSqCollision(temp, rect):
				c += 1

		if c==0:
			baddieList.append(temp)

	# if ip == 0:
	circleDict = {
		"x": 10,
		"y": 10,
		"r": 10,
		"c": googleColorList[session['uid']]

	}
	# else:
	# 	circleDict = {
	# 		"x": 10,
	# 		"y": 10,
	# 		"r": 10,
	# 		"c": googleColorList[session['uid']]

	# 	}



	ipDict[ip] = {"circleDict": circleDict, "color":googleColorList[session['uid']], "radius":10}
	ipDict[ip]['state'] = 'rest'
	# playerCount += 1
	# if playerCount == 4:
	# 	playerCount = 0

	

	msg = "New canvas request from {ip}".format(ip=ip)
	emit('createCanvasPush', {"msg":msg, "rectList":rectList, "prizeList":prizeList, "baddieList":baddieList, "circleDict": circleDict, "ipDict": ipDict, "ip":ip, 'bgcolor':bgcolor}, broadcast=True,) 

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
	ipDict[ip]['circleDict']['x'] += d['dx']
	ipDict[ip]['circleDict']['y'] += d['dy']

	#create boundaries for player on canvas
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

			if ipDict[ip]['state'] == 'rest': #janky hack to fix endless loop
				
				tempDict = ipDict[ip]['circleDict'].copy()
				tempdy = 0
				tempdx = 0

				if d['dx'] != 0:
					tempDict['x'] = tempDict['x'] - d['dx']
					if not collision(tempDict, rect):
						# print('allow movement in y direction')
						tempDict['x'] = tempDict['x'] + d['dx']
						tempdy = d['dy']
				
				if d['dy'] != 0:
					tempDict['y'] = tempDict['y'] - d['dy']
					if not collision(tempDict, rect):
						# print('allow movement in x direction')
						tempDict['y'] = tempDict['y'] + d['dy']
						tempdx = d['dx']

				while collision(ipDict[ip]['circleDict'], rect):

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

					
					ipDict[ip]['circleDict']['y'] -= signy
					ipDict[ip]['circleDict']['x'] -= signx

				ipDict[ip]['circleDict']['y'] += tempdy
				ipDict[ip]['circleDict']['x'] += tempdx


	#create collison for prizes
	for index, prize in enumerate(prizeList):
		if collision(ipDict[ip]['circleDict'], prize):
			prizeList.pop(index)
			c = ipDict[ip].get('score', 0)
			ipDict[ip]['score'] = c + 1



	# create collison for baddies
	for index, baddie in enumerate(baddieList):

		if collision(ipDict[ip]['circleDict'], baddie) and ipDict[ip]['state'] == 'rest':
			baddieList.pop(index)
			# ipDict[ip]['circleDict']['r'] -= 4 
			ipDict[ip]['radius'] -= 4 

			# if ipDict[ip]['circleDict']['r'] <= 0:
			if ipDict[ip]['radius'] <= 0:

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

	ipDict[ip]['circleDict']['c'] = '#ffffff'
	ipDict[ip]['state'] = 'attack'
	ipDict[ip]['circleDict']['r'] = 30#ipDict[ip]['circleDict']['r']*3


	for index, baddie in enumerate(baddieList):

		if collision(ipDict[ip]['circleDict'], baddie) and ipDict[ip]['state'] == 'attack':
			# print('hi')
			baddieList.pop(index)

	for index, eachip in enumerate(ipDict.keys()):

		if eachip != ip:

			if circleOncircleCollision(ipDict[ip]['circleDict'], ipDict[eachip]['circleDict']) and ipDict[ip]['state'] == 'attack':
				# print('hi')
				# baddieList.pop(index)

				ipDict[eachip]['radius'] -= 4 

				# if ipDict[ip]['circleDict']['r'] <= 0:
				if ipDict[eachip]['radius'] <= 0:

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
	global ipList

	ipDict = {}
	rectList = []
	prizeList = []
	baddieList = []
	playerCount = 0
	uidCount = 0
	ipList = []


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
	global ipList
	global playerCount




	# ip = request.remote_addr
	ip = session['uid']

	# for _ip in ipDict.keys():

	#return vars to normal after attack etc
	if ipDict[ip]['circleDict']['r'] > ipDict[ip]['radius'] and ipDict[ip]['state'] == 'attack':
		# print(ipDict[ip]['circleDict']['r'])
		# print(ipDict[ip]['radius'])
		ipDict[ip]['circleDict']['r'] -=  10
	else:

		ipDict[ip]['circleDict']['c'] = ipDict[ip]['color']
		ipDict[ip]['circleDict']['r'] = ipDict[ip]['radius']
		ipDict[ip]['state'] = 'rest'





	# print(ip)
	# print(ipDict[ip]['circleDict']['r'])
	if ip == ipList[0]:


		for index, baddie in enumerate(baddieList):

			# for _ip in ipDict.keys():


			if collision(ipDict[ip]['circleDict'], baddie) and ipDict[ip]['state'] == 'rest':
				
				# print('here')

				baddieList.pop(index)
				
				# ipDict[ip]['circleDict']['r'] -= 4 
				ipDict[ip]['radius'] -= 4 

				# if ipDict[ip]['circleDict']['r'] <= 0:
				if ipDict[ip]['radius'] <= 0:

					# playerCount -= 1
					# if playerCount == 0:
						refreshGlobals()

						msg = "Global variables refreshed."
						emit('refreshGlobalsPush', {"msg":msg}, broadcast=True,) 


			#identify if circle is near
			targetList = []
			for _ip in ipList:
				xdif = baddie['x'] - ipDict[_ip]['circleDict']['x']
				ydif = baddie['y'] - ipDict[_ip]['circleDict']['y']
				eucDist = (xdif**2 + ydif**2)**0.5
				if eucDist < 200:
					targetList.append(_ip)

			if targetList:
				targetList.sort()
				target_ip = targetList[0]
				xdif = baddie['x'] - ipDict[target_ip]['circleDict']['x']
				ydif = baddie['y'] - ipDict[target_ip]['circleDict']['y']
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