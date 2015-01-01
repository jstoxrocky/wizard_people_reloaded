# -*- coding: utf-8 -*- 


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
bonesList = []
baddieList = []
canvasDim = {}
uidCount = 0
colsChosen = {}
globalHeadip = -1

#FLASK
@app.route('/')
def index():
	return render_template('main.html')


@socketio.on('connect', namespace='/test')
def connectFunc():

	# import global playerList and uidCount (combine with player count?)
	global uidCount
	global rectList
	global ipDict
	global colsChosen

	if rectList:
		msg = "Game in progress. Try again later."
		emit('gameInProgressPush', {"msg":msg}, broadcast=False,) 
	else:

		# if not ipDict:
			# uidCount = 0

		#give uid equal to uidCount
		session['uid'] = uidCount
		uidCount += 1
		msg = "New connection"

		colsDict = {'red':0,'blu':0,'gre':0,'yel':0}
		for val in colsChosen.values():
			# c = colsDict.get(val, 0)
			colsDict[val] += 1

		# print(colsDict)

		emit('connectPush', {"msg":msg, 'colsDict':colsDict}, broadcast=True,) 



@socketio.on('playerChooseRequest', namespace='/test')
def playerChooseFunc(d):


	#import global playerList and uidCount (combine with player count?)
	global ipDict
	global colsChosen
	global globalHeadip

	ip = session['uid']
	
	playerDict = {
		"x": 10,
		"y": 10,
		"w": 29,
		"h": 29,
		"c": d['col'],
		"r": 0,
		"id": ip,
		"state": 'rest',
		"health": {"hearts":u'♥♥♥',"level":3},
	}

	ipDict[ip] = playerDict

	colsChosen[ip] = d['col']

	colsDict = {'red':0,'blu':0,'gre':0,'yel':0}
	for val in colsChosen.values():
		# c = colsDict.get(val, 0)
		colsDict[val] += 1

	print(colsDict)

	print(ipDict.keys())
	globalHeadip = min(ipDict.keys())
	# print(globalHeadip)


	msg = "Player {uid} chose {col} wizard.".format(uid=ip,col=d['col'])
	emit('playerChoosePush', {"msg":msg, 'colsDict':colsDict}, broadcast=True,) 





@socketio.on('refreshGlobalsRequest', namespace='/test')
def refreshGlobalsFunc(d):

	refreshGlobals()
	msg = "Global variables refreshed."
	emit('refreshGlobalsPush', {"msg":msg}, broadcast=True,) 






@socketio.on('popPlayerRequest', namespace='/test')
def popPlayerFunc(d):

	# try:

	global ipDict
	global globalHeadip
	
	try:
		ip = session['uid']
	except:
		ip = -1

	if ip in ipDict and ipDict:

		ipDict.pop(session['uid'])
		
		if not ipDict:
			refreshGlobals()
		else:
			globalHeadip = min(ipDict.keys())

		msg = "Player popped"
		emit('popPlayerPush', {"msg":msg}, broadcast=True,) 

	# except:
	# 	pass




@socketio.on('createCanvasRequest', namespace='/test')
def createCanvasFunc(d):

	# global ipDict
	global rectList
	global prizeList
	global baddieList
	global canvasDim
	global bonesList

	#need to restart these vars each time someone joins
	rectList = []
	prizeList = []
	baddieList = []
	bonesList = []

	ip = session['uid']
	canvasDim['w'] = d['w']
	canvasDim['h'] = d['h']

	#select level and colors
	#push most of this to browser
	# googleColorList = ['#0266C8', '#F90101', '#F2B50F', '#00933B']
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
			{"x":randint(100,d['w']-100),
			"y":randint(000,d['h']-100),
			"w":randint(50,d['w']/2),
			"h":randint(50,d['h']/2),
			"c":colorList[randint(0,len(colorList)-1)],
			}
		)

	#create prizes
	prizeNum = d['w']*d['h']/32768
	success = 0
	while len(prizeList) < prizeNum:

		prizeType = 'coin'
		if success % 7 == 0:
			prizeType = 'ruby'

		temp = {"x":randint(100,d['w']-100),
			"y":randint(100,d['h']-100),
			"w":25,
			"h":25,
			"prizeType":prizeType,
			}

		c = 0
		for rect in rectList:
			if sqOnSqCollision(temp, rect):
				c += 1
				break
		if c==0:
			success += 1
			prizeList.append(temp)
				
	baddieNum = d['w']*d['h']/100960
	baddieDirList = [1,-1]
	while len(baddieList) < baddieNum:

		temp = {"x":randint(100,d['w']-100),
			"y":randint(100,d['h']-100),
			"w":35,
			"h":35,
			"c":baddieColor,
			"dir":baddieDirList[randint(0,1)],
			"action": 'patrol',
			}

		c = 0
		for rect in rectList:
			if sqOnSqCollision(temp, rect):
				c += 1
				break
		if c==0:
			baddieList.append(temp)

	emit('createCanvasPush', {"rectList":rectList, "prizeList":prizeList, "baddieList":baddieList, 'bgcolor':bgcolor}, broadcast=True,) 



@socketio.on('keypressRequest', namespace='/test')
def keypressFunc(d):

	# try:
	# if 

	global ipDict
	global baddieList
	# global prizeList

	try:
		ip = session['uid']
	except:
		ip = -1


	# print(ip)
	# print(ipDict)

	if ip in ipDict and ipDict:

		# print('a')

		# #restart level if all coins obtained
		# if not prizeList:
		# 	refreshGlobals()
		# 	msg = "Global variables refreshed."
		# 	emit('refreshGlobalsPush', {"msg":msg}, broadcast=True,) 

		#incrememnt move
		ipDict[ip]['x'] += d['dx']
		ipDict[ip]['y'] += d['dy']
		ipDict[ip]['dx'] = d['dx']
		ipDict[ip]['dy'] = d['dy']



		#control for collisions with canvas boundaries
		ipDict[ip] = collisionWithCanvasBounds(ipDict[ip])

		#control for collisions with rectangles
		ipDict[ip] = collisionWithRect(ipDict[ip])

		#control for collisions with prizes
		ipDict[ip] = collisionWithPrize(ipDict[ip])

		#control for collisions with baddies
		# for i, baddie in enumerate(baddieList):
			# collisionWithBaddie(ipDict[ip], baddie, i, ip)

		emit('keypressPush', {"ipDict":ipDict, "prizeList":prizeList, "baddieList":baddieList, "bonesList":bonesList}, broadcast=True,) 

	# except KeyError:
	# 	pass


	




@socketio.on('attackRequest', namespace='/test')
def attackFunc(d):

	global ipDict
	# global prizeList
	global baddieList
	global bonesList

	try:
		ip = session['uid']
	except:
		ip = -1

	if ip in ipDict and ipDict:

		ipDict[ip]['state'] = 'attack'
		ipDict[ip]['r'] = 40

		auraDict = {'x':ipDict[ip]['x'] + ipDict[ip]['w']/2, 
					'y':ipDict[ip]['y'] + ipDict[ip]['h']/2, 
					'r': ipDict[ip]['r']}

		for index, baddie in enumerate(baddieList):
			if collision(auraDict, baddie) and ipDict[ip]['state'] == 'attack':
				bonesList.append({'x':baddie['x'],'y':baddie['y']})
				baddieList.pop(index)


		for index, eachip in enumerate(ipDict.keys()):

			if eachip != ip:

				if collision(auraDict, ipDict[eachip]) and ipDict[ip]['state'] == 'attack':

					getHurt(ipDict[eachip], eachip)



		emit('keypressPush', {"ipDict":ipDict, "ip":ip, "prizeList":prizeList, "baddieList":baddieList, "bonesList":bonesList}, broadcast=True,) 



@socketio.on('incrementBagGuysPositionRequest', namespace='/test')
def incrementBagGuysPositionFunc(d):

	# while True:	

		global baddieList
		global ipDict
		global bonesList
		global prizeList


		if not ipDict:
			refreshGlobals()

		try:
			ip = session['uid']	
		except:
			ip = -1

		#restart level if all coins obtained
		if not prizeList:
			refreshGlobals()
			msg = "Global variables refreshed."
			emit('refreshGlobalsPush', {"msg":msg}, broadcast=True,) 

		# print(ip)
		# print(ipDict.keys())

		if ip in ipDict and ipDict:
			# globalHeadip = min(ipDict.keys())

			# print('a')

				# print(ipDict)
			if ipDict[ip]['r'] > 0 and ipDict[ip]['state'] == 'attack':

				ipDict[ip]['r'] -=  10

			else:

				ipDict[ip]['r'] = 0

				ipDict[ip]['state'] = 'rest'

			for i, baddie in enumerate(baddieList):

				#check for collisions
				# ipDict[ip] = collisionWithBaddie(ipDict[ip], baddie, i, ip)
				collisionWithBaddie(ipDict[ip], baddie, i, ip)

				# print(ip)
				# print(ipDict.keys())
				# print(globalHeadip)
				# print(ip)
				if ipDict and ip == globalHeadip:
				# if True:

					#get chase direction if players nearby
					ddx, ddy = getChaseDirection(baddie)
					

					#increment baddie position accordingly
					baddie['x'] += ddx
					baddie['y'] += ddy
					baddie['dx'] = ddx
					baddie['dy'] = ddy

					if (baddie['x'] < 0 or baddie['x']+baddie['w'] > canvasDim['w']):
						baddie['dir'] = baddie['dir']*-1
					# if (baddie['y'] < 0 or baddie['y']+baddie['h'] > canvasDim['h']):
					# 	baddie['dir'] = baddie['dir']*-1

					for rect in rectList:
						if sqOnSqCollision(baddie, rect):
							baddie['dir'] = baddie['dir']*-1

					#control for collisions with canvas boundaries
					baddie = collisionWithCanvasBounds(baddie)

					#control for collisions with rectangles
			
					baddie = collisionWithRect(baddie)
				
			# if ipDict and ip == globalHeadip:
			if True:
				emit('incrementBagGuysPositionPush', {"ipDict": ipDict, "baddieList":baddieList, "bonesList": bonesList}, broadcast=True,) 
				# incrementBagGuysPositionFunc(1)
				# except KeyError:
				# 	pass


		












def getChaseDirection(baddie):

	global ipDict

	targetList = []
	for _ip in ipDict.keys():

		xdif = baddie['x'] - ipDict[_ip]['x']
		ydif = baddie['y'] - ipDict[_ip]['y']
		eucDist = (xdif**2 + ydif**2)**0.5
		if eucDist < 200:
			targetList.append(_ip)

	if targetList:
		targetList.sort()
		target_ip = targetList[0]

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

		if baddie['action'] == 'patrol':

			#patrol
			ddx = baddie['dir']*4
			ddy = randint(-1,1)

		else:

			dx = randint(0,5)
			dy = randint(0,5)

			ddx = randint(-dx,dx)
			ddy = randint(-dy,dy)

			# if ddx == 0: 
			# 	ddx += 1
			# if ddy == 0:
			# 	ddy += 1

		# if baddie['x'] != collisionWithCanvasBounds(baddie)['x']


		# if baddie['x'] != collisionWithRect(baddie)['x'] or \
		# 	baddie['y'] != collisionWithRect(baddie)['y']:
		# 	print('c')
		# 	baddie['dir'] = baddie['dir']*-1

		# baddie = collisionWithRect(baddie)



	return ddx, ddy



def refreshGlobals():

	global ipDict
	global rectList
	global prizeList
	global baddieList
	global uidCount
	global bonesList
	global colsChosen

	ipDict = {}
	rectList = []
	prizeList = []
	baddieList = []
	uidCount = 0
	bonesList = []
	colsChosen = {}


def sqOnSqCollision(rect1, rect2):

	return rect1['x'] < rect2['x'] + rect2['w'] and \
	   rect1['x'] + rect1['w'] > rect2['x'] and \
	   rect1['y'] < rect2['y'] + rect2['h'] and \
	   rect1['h'] + rect1['y'] > rect2['y']

def circleOncircleCollision(circle1,circle2):

	dx = (circle1['x']) - (circle2['x'])
	dy = (circle1['y']) - (circle2['y'])
	distance = ((dx ** 2) + (dy ** 2))**0.5

	if distance < circle1['r'] + circle2['r']: 

	    return True

def collisionWithCanvasBounds(specificObjectDict):
	
	global canvasDim

	#create boundaries for player on canvas
	if (specificObjectDict['x'] < 0 or specificObjectDict['x']+specificObjectDict['w'] > canvasDim['w']):
		while (specificObjectDict['x'] < 0 or specificObjectDict['x']+specificObjectDict['w'] > canvasDim['w']):
			sign = specificObjectDict['dx']/abs(specificObjectDict['dx'])
			specificObjectDict['x'] -= sign

	if (specificObjectDict['y'] < 0 or specificObjectDict['y']+specificObjectDict['h'] > canvasDim['h']):
		while (specificObjectDict['y'] < 0 or specificObjectDict['y']+specificObjectDict['h'] > canvasDim['h']):
			sign = specificObjectDict['dy']/abs(specificObjectDict['dy'])
			specificObjectDict['y'] -= sign

	return specificObjectDict


def collisionWithRect(specificObjectDict):

	global rectList

	for rect in rectList:
		if sqOnSqCollision(specificObjectDict, rect):

					# #allow sliding on edges of rectangles
					tempDict = specificObjectDict.copy()


					tempDict['y'] -= specificObjectDict['dy']
					if not sqOnSqCollision(tempDict, rect): #then we kno y is a problem
						while sqOnSqCollision(specificObjectDict, rect):

							if specificObjectDict['dy'] == 0:
								signy = 0
							else:
								signy = specificObjectDict['dy']/abs(specificObjectDict['dy'])
							specificObjectDict['y'] -= signy
					tempDict['y'] += specificObjectDict['dy']




					tempDict['x'] -= specificObjectDict['dx']
					if not sqOnSqCollision(tempDict, rect): #x is a problem

						while sqOnSqCollision(specificObjectDict, rect):

							if specificObjectDict['dx'] == 0:
								signx = 0
							else:
								signx = specificObjectDict['dx']/abs(specificObjectDict['dx'])

							specificObjectDict['x'] -= signx
					tempDict['x'] += specificObjectDict['dy']


	return specificObjectDict

def collisionWithPrize(specificObjectDict):
	
	#create collison for prizes
	global prizeList

	for index, prize in enumerate(prizeList):
		if sqOnSqCollision(specificObjectDict, prize):
			
			c = specificObjectDict.get('score', 0)
			if prize['prizeType'] == 'coin':
				specificObjectDict['score'] = c + 1
			elif prize['prizeType'] == 'ruby':
				specificObjectDict['score'] = c + 5
			prizeList.pop(index)
			
	return specificObjectDict

def collisionWithBaddie(specificObjectDict, baddie, i, ip):

	global bonesList

	# create collison for baddies
	if sqOnSqCollision(specificObjectDict, baddie) and specificObjectDict['state'] == 'rest':
		baddieList.pop(i)
		bonesList.append({'x':baddie['x'],'y':baddie['y']})
		# specificObjectDict = getHurt(specificObjectDict, ip)
		getHurt(specificObjectDict, ip)

	return specificObjectDict


def getHurt(specificObjectDict, ip):

	global ipDict
	global globalHeadip

	# specificObjectDict['w'] -= 10
	# specificObjectDict['h'] -= 10

	specificObjectDict['health']['hearts'] = specificObjectDict['health']['hearts'].replace(u'♥',u'♡',1)
	specificObjectDict['health']['level'] -= 1


	if specificObjectDict['health']['level'] <= 0: 
	# if specificObjectDict['w'] <= 0:
			ipDict.pop(ip, None)
			


			if not ipDict:
				refreshGlobals()
				msg = "Global variables refreshed."
				emit('refreshGlobalsPush', {"msg":msg}, broadcast=True,) 
			else:
				globalHeadip = min(ipDict.keys())
				
			# globalHeadip = min(ipDict.keys())

	return specificObjectDict




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






if __name__ == '__main__':
	# socketio.run(app, host= '0.0.0.0', port=6020)
	socketio.run(app, host= '127.0.0.1', port=6020)