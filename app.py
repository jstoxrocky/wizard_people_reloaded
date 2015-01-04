# -*- coding: utf-8 -*- 


#needed for debug mode to work!
from gevent import monkey
monkey.patch_all()

#do some imports!
from flask import Flask, render_template, request, jsonify, session
from flask.ext.socketio import SocketIO, emit
import urllib, json
from random import randint


#start me up!
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

uidDict = {}
rectList = []
prizeList = []
bonesList = []
baddieList = []
canvasDim = {}
uidCount = 0
colsChosen = {}
globalHeaduid = -1 #specific id that will cause the game loop to execute
					#if not game loop executes more times with more players

#FLASK
@app.route('/')
def index():
	return render_template('main.html')


@socketio.on('connect', namespace='/test')
def connectFunc():

	global uidCount
	global rectList
	global uidDict

	if rectList:
		msg = "Game in progress. Try again later."
		emit('gameInProgressPush', {"msg":msg}, broadcast=False,) 
	else:

		#give an id to this session
		session['uid'] = uidCount
		uidCount += 1
		msg = "New connection"

		#get a dictionary of colors that players play
		colsDict = getColsDict()

		emit('connectPush', {"msg":msg, 'colsDict':colsDict}, broadcast=True,) 







@socketio.on('playerChooseRequest', namespace='/test')
def playerChooseFunc(d):

	global uidDict
	global colsChosen
	global globalHeaduid

	try:
		uid = session['uid']
	except:
		# uid = -1
		return None
	
	playerDict = {
		"x": 10,
		"y": 10,
		"w": 29,
		"h": 29,
		"c": d['col'],
		"cc": "#CD96CD",
		"r": 0,
		"id": uid,
		"state": 'rest',
		"health": {"hearts":u'♥♥♥',"level":3},
	}

	uidDict[uid] = playerDict

	colsChosen[uid] = d['col']

	colsDict = getColsDict()

	globalHeaduid = min(uidDict.keys())

	msg = "Player {uid} chose {col} wizard.".format(uid=uid,col=d['col'])
	emit('assignUIDPush', {'uid':uid}, broadcast=False,) 
	emit('playerChoosePush', {"msg":msg, 'colsDict':colsDict}, broadcast=True,) 





@socketio.on('refreshGlobalsRequest', namespace='/test')
def refreshGlobalsFunc(d):

	refreshGlobals()

	msg = "Global variables refreshed."
	emit('refreshGlobalsPush', {"msg":msg}, broadcast=True,) 






@socketio.on('popPlayerRequest', namespace='/test')
def popPlayerFunc(d):


	global uidDict
	global globalHeaduid
	
	# if True:
	try:
		uid = session['uid']
	except:
		# uid = -1
		return None

	if uid in uidDict and uidDict:

		uidDict.pop(session['uid'])
		
		if not uidDict:
			refreshGlobals()
		else:
			globalHeaduid = min(uidDict.keys())

		msg = "Player popped"
		emit('popPlayerPush', {"msg":msg}, broadcast=True,) 




@socketio.on('createCanvasRequest', namespace='/test')
def createCanvasFunc(d):

	# global uidDict
	global rectList
	global prizeList
	global baddieList
	global canvasDim
	global bonesList
	global globalHeaduid

	#need to restart these vars each time someone joins
	rectList = []
	prizeList = []
	baddieList = []
	bonesList = []

	uid = session['uid']

	canvasDim['w'] = canvasDim.get('w',d['w'])
	canvasDim['h'] = canvasDim.get('h',d['h'])

	if d['w'] < canvasDim['w']:
		canvasDim['w'] = d['w']

	if d['h'] < canvasDim['h']:
		canvasDim['h'] = d['h']

	#select level and colors
	levelList = ['cave', 'grassy', 'icy', 'sand']
	levelNum = randint(0,len(levelList)-1)

	if levelList[levelNum] == 'grassy':
		colorList = ['#999999','#35373b', '#8C8C8C', '#212121', "#4f4f4f"]
		bgcolor = '#86C67C'
	elif levelList[levelNum] == 'cave':
		colorList = ['#42526C','#35373b', '#2F4F4F', '#212121', "#4f4f4f"]
		bgcolor = '#8C8C8C'
	elif levelList[levelNum] == 'icy':
		colorList = ['#BFEFFF','#35373b', '#82CFFD', '#212121', "#4f4f4f"]
		bgcolor = '#FFFAFA'
	elif levelList[levelNum] == 'sand':
		colorList = ['#956c4b','#905120', '#502d12', '#d4803f', "#b08563"]
		bgcolor = '#edd9af'

	#create rectangles
	rectNum = canvasDim['w']*canvasDim['h']/91022
	for i in range(0,rectNum):
		rectList.append(
			{"x":randint(100,canvasDim['w']-100),
			"y":randint(000,canvasDim['h']-100),
			"w":randint(50,canvasDim['w']/2),
			"h":randint(50,canvasDim['h']/2),
			"c":colorList[randint(0,len(colorList)-1)],
			}
		)

	#create prizes
	prizeNum = canvasDim['w']*canvasDim['h']/32768
	success = 0


	rubySpecs = {"type":'ruby',"value":5,"func":"addValue"}
	coinSpecs = {"type":'coin',"value":1,"func":"addValue"}
	potionSpecs = {"type":'potion',"value":1,"func":"addHealth"}

	prizeBreakownDict = {'ruby': {'specs':rubySpecs, 'quant':int(0.35*prizeNum)}, 
							 'coin':{'specs':coinSpecs, 'quant':int(0.6*prizeNum)}, 
							 'potion':{'specs':potionSpecs, 'quant':int(0.05*prizeNum)}}

	prizeBreakdownList =[]
	for name, nameDict in prizeBreakownDict.iteritems():
		for i in range(0,nameDict['quant']):
			prizeBreakdownList.append(nameDict['specs'])

	prizeCount = 0
	while len(prizeList) < len(prizeBreakdownList):

		prizeSpecs = prizeBreakdownList[prizeCount]

		temp = {"x":randint(100,canvasDim['w']-100),
			"y":randint(100,canvasDim['h']-100),
			"w":25,
			"h":25,
			"type":prizeSpecs['type'],
			"value":prizeSpecs['value'],
			"func":prizeSpecs['func'],
			}


		goodToPlace = True
		for rect in rectList:
			if sqOnSqCollision(temp, rect):
				goodToPlace = False
				break
		if goodToPlace:
			prizeCount += 1
			prizeList.append(temp)
				
	baddieNum = canvasDim['w']*canvasDim['h']/100960
	baddieDirList = [1,-1]
	
	goblinSpecs = {"type":"goblin", "speed":4, "action":"patrol", "w":35, "h":35, "lives":1, "attack":0}
	ratSpecs = {"type":"rat", "speed":8, "action":"random","w":104*0.4,"h":50*0.4, "lives":1, "attack":0}
	gobkingSpecs = {"type":"gobking", "speed":2, "action":"patrol","w":60,"h":60, "lives":3, "attack":1}


	creaturesBreakownDict = {'goblin': {'specs':goblinSpecs, 'quant':int(0.5*baddieNum)}, 
							 'rat':{'specs':ratSpecs, 'quant':int(0.35*baddieNum)}, 
							 'gobking':{'specs':gobkingSpecs, 'quant':int(0.15*baddieNum)}}

	baddieBreakdownList =[]
	for name, nameDict in creaturesBreakownDict.iteritems():
		for i in range(0,nameDict['quant']):
			baddieBreakdownList.append(nameDict['specs'])

	creatureCount = 0
	# while len(baddieList) < baddieNum-1:
	while len(baddieList) < len(baddieBreakdownList):

		baddieSpecs = baddieBreakdownList[creatureCount]

		temp = {
			"x":randint(200,canvasDim['w']-100),
			"y":randint(200,canvasDim['h']-100),
			"w":baddieSpecs["w"],
			"h":baddieSpecs["h"],
			"dir":baddieDirList[randint(0,1)],
			"action": baddieSpecs["action"],
			"speed": baddieSpecs["speed"],
			"type": baddieSpecs["type"],
			"lives": baddieSpecs["lives"],
			"r":0,
			"attack": baddieSpecs["attack"],
			}

		# c = 0
		goodToPlace = True
		for rect in rectList:
			if sqOnSqCollision(temp, rect):
				# c += 1
				goodToPlace = False
				break
		# if c==0:
		if goodToPlace:
			creatureCount += 1
			baddieList.append(temp)

	emit('createCanvasPush', {"rectList":rectList, "prizeList":prizeList, "baddieList":baddieList, 'bgcolor':bgcolor, 'canvasDim':canvasDim, 'globalHeaduid':globalHeaduid}, broadcast=True,) 



@socketio.on('keypressRequest', namespace='/test')
def keypressFunc(d):

	global uidDict
	global baddieList

	# if True:
	try:
		uid = session['uid']
	except:
		# uid = -1
		return None

	if uid in uidDict and uidDict:

		#incrememnt move
		uidDict[uid]['x'] += d['dx']
		uidDict[uid]['y'] += d['dy']
		uidDict[uid]['dx'] = d['dx']
		uidDict[uid]['dy'] = d['dy']

		#control for collisions with canvas boundaries
		uidDict[uid] = collisionWithCanvasBounds(uidDict[uid])

		#control for collisions with rectangles
		uidDict[uid] = collisionWithRect(uidDict[uid])

		#control for collisions with prizes
		uidDict[uid] = collisionWithPrize(uidDict[uid])

		emit('keypressPush', {"uidDict":uidDict, "prizeList":prizeList, "baddieList":baddieList, "bonesList":bonesList}, broadcast=True,) 



@socketio.on('attackRequest', namespace='/test')
def attackFunc(d):

	global uidDict
	global baddieList
	global bonesList

	# if True:
	try:
		uid = session['uid']
	except:
		# uid = -1
		return None

	if uid in uidDict and uidDict:

		uidDict[uid]['state'] = 'attack'
		uidDict[uid]['r'] = 40

		auraDict = {'x':uidDict[uid]['x'] + uidDict[uid]['w']/2, 
					'y':uidDict[uid]['y'] + uidDict[uid]['h']/2, 
					'r': uidDict[uid]['r']}

		for index, baddie in enumerate(baddieList):
			if collision(auraDict, baddie) and uidDict[uid]['state'] == 'attack':
				baddie['lives'] -= 1
				baddie['r'] = 50
				if baddie['lives'] <= 0:
					bonesList.append({'x':baddie['x'],'y':baddie['y'], 'h':baddie['h']})
					baddieList.pop(index)


		for index, eachuid in enumerate(uidDict.keys()):

			if eachuid != uid:

				if collision(auraDict, uidDict[eachuid]) and uidDict[uid]['state'] == 'attack':

					getHurt(uidDict[eachuid], eachuid)



		emit('keypressPush', {"uidDict":uidDict, "uid":uid, "prizeList":prizeList, "baddieList":baddieList, "bonesList":bonesList}, broadcast=True,) 



# @socketio.on('gameLoopRequest', namespace='/test')
# def gameLoopFunc(d):

# 		global baddieList
# 		global uidDict
# 		global bonesList
# 		global prizeList

# 		# if not uidDict:
# 		# 	refreshGlobals()

# 		#This needed as sometimes the game loop continues ofter sessions are removed
# 		try:
# 			uid = session['uid']	
# 		except:
# 			uid = -1

# 		#restart level if all coins obtained
# 		if not prizeList:
# 			refreshGlobals()
# 			msg = "Global variables refreshed."
# 			emit('refreshGlobalsPush', {"msg":msg}, broadcast=True,) 

# 		if uid in uidDict and uidDict:

# 			if uidDict[uid]['r'] > 0 and uidDict[uid]['state'] == 'attack':
# 				uidDict[uid]['cc'] = '#CD96CD'
# 				uidDict[uid]['r'] -=  10

# 			else:

# 				uidDict[uid]['r'] = 0
# 				uidDict[uid]['cc'] = '#CD96CD'
# 				uidDict[uid]['state'] = 'rest'

# 			for i, baddie in enumerate(baddieList):
				
# 				#check for collisions
# 				collisionWithBaddie(uidDict[uid], baddie, i, uid)

# 				#if loop continues checking for baddies after a baddie in the loop
# 				#got rid of the last player
# 				if not uid in uidDict:
# 					break

# 				if uidDict and uid == globalHeaduid:
# 				# if True:

# 					#get chase direction if players nearby
# 					ddx, ddy = getChaseDirection(baddie)
					
# 					#increment baddie position accordingly
# 					baddie['x'] += ddx
# 					baddie['y'] += ddy
# 					baddie['dx'] = ddx
# 					baddie['dy'] = ddy

# 					if (baddie['x'] < 0 or baddie['x']+baddie['w'] > canvasDim['w']):
# 						baddie['dir'] = baddie['dir']*-1

# 					for rect in rectList:
# 						if sqOnSqCollision(baddie, rect):
# 							baddie['dir'] = baddie['dir']*-1

# 					#control for collisions with canvas boundaries
# 					baddie = collisionWithCanvasBounds(baddie)

# 					#control for collisions with rectangles
# 					baddie = collisionWithRect(baddie)
				
# 			emit('gameLoopPush', {"uidDict": uidDict, "baddieList":baddieList, "bonesList": bonesList}, broadcast=True,) 


		


@socketio.on('gameLoopRequest', namespace='/test')
def gameLoopFunc(d):

	global baddieList
	global uidDict
	global bonesList
	global prizeList

	#This needed as sometimes the game loop continues after sessions are removed
	try:
		uid = session['uid']	
	except:
		# uid = -1
		return None

	#restart level if all coins obtained
	if not prizeList:
		refreshGlobals()
		msg = "Global variables refreshed."
		emit('refreshGlobalsPush', {"msg":msg}, broadcast=True,) 

	#for each uid
	#we need to change its state and attack circle size
	for uid in uidDict:

		if uidDict[uid]['r'] > 0 and uidDict[uid]['state'] == 'attack':
			uidDict[uid]['cc'] = '#CD96CD'
			uidDict[uid]['r'] -=  10

		else:

			uidDict[uid]['r'] = 0
			uidDict[uid]['cc'] = '#CD96CD'
			uidDict[uid]['state'] = 'rest'


	#check for collisions between each baddie and player
	for i, baddie in enumerate(baddieList):
		for uid in uidDict:
			
			#check for collisions
			if checkCollisionWithBaddie(uidDict[uid], baddie, i, uid):
				baddie['lives'] -= 1
				baddie['r'] = 50


				# zx = baddie['x'] - uidDict[uid]['x']
				# zy = baddie['y'] - uidDict[uid]['y']
				# uidDict[uid]['x'] -= zx
				# uidDict[uid]['y'] -= zy
				# uidDict[uid] = collisionWithCanvasBounds(uidDict[uid])

				#control for collisions with rectangles
				uidDict[uid] = collisionWithRect(uidDict[uid])

				if baddie['lives'] <= 0:
					bonesList.append({'x':baddie['x'],'y':baddie['y'], 'h':baddie['h']})
					baddieList.pop(i)


				
				# sign = 0
				# while checkCollisionWithBaddie(uidDict[uid], baddie, i, uid):
				# 	if uidDict[uid]['dx'] != 0:
				# 		sign = uidDict[uid]['dx']/abs(uidDict[uid]['dx'])
				# 		uidDict[uid]['x'] -= sign

				# sign = 0
				# while checkCollisionWithBaddie(uidDict[uid], baddie, i, uid):
				# 	if uidDict[uid]['dy'] != 0:
				# 		sign = uidDict[uid]['dy']/abs(uidDict[uid]['dy'])
				# 		uidDict[uid]['y'] -= sign


				getHurt(uidDict[uid], uid)

				#break beacuse if we remove uid from uidDict the loop changs
				break

		#if loop continues checking for baddies after a baddie in the loop
		#got rid of the last player
		if not uid in uidDict:
			break


	#check for baddie bounds and move baddies
	for i, baddie in enumerate(baddieList):

		if baddie['r'] > 0:
			baddie['r'] -= 10

		#get chase direction if players nearby
		ddx, ddy = getChaseDirection(baddie)
		
		#increment baddie position accordingly
		baddie['x'] += ddx
		baddie['y'] += ddy
		baddie['dx'] = ddx
		baddie['dy'] = ddy

		if (baddie['x'] < 0 or baddie['x']+baddie['w'] > canvasDim['w']):
			baddie['dir'] = baddie['dir']*-1

		for rect in rectList:
			if sqOnSqCollision(baddie, rect):
				baddie['dir'] = baddie['dir']*-1

		#control for collisions with canvas boundaries
		baddie = collisionWithCanvasBounds(baddie)

		#control for collisions with rectangles
		baddie = collisionWithRect(baddie)
			


	emit('gameLoopPush', {"uidDict": uidDict, "baddieList":baddieList, "bonesList": bonesList}, broadcast=True,) 











def getColsDict():

	global colsChosen

	colsDict = {'red':0,'blu':0,'gre':0,'yel':0}
	for val in colsChosen.values():
		colsDict[val] += 1
	return colsDict


def getChaseDirection(baddie):

	global uidDict

	targetList = []
	for _uid in uidDict.keys():

		xdif = baddie['x'] - uidDict[_uid]['x']
		ydif = baddie['y'] - uidDict[_uid]['y']
		eucDist = (xdif**2 + ydif**2)**0.5
		if eucDist < 200:
			targetList.append(_uid)

	if targetList:
		targetList.sort()
		target_uid = targetList[0]

		xdif = baddie['x'] - uidDict[target_uid]['x']
		ydif = baddie['y'] - uidDict[target_uid]['y']
		if xdif > 0:
			ddx = -(baddie['speed'] + randint(0,2))
		else:
			ddx = (baddie['speed'] + randint(0,2))

		if ydif > 0:
			ddy = -(baddie['speed'] + randint(0,2))
		else:
			ddy = (baddie['speed'] + randint(0,2))


			
		# if baddie['attack'] > 0:
		# 	baddie['w'] = baddie['w']*3.0

		# if baddie['attack'] < 0:
		# 	baddie['w'] = baddie['w']/3.0

		# baddie['attack'] = baddie['attack']*-1
	
	else:

		if baddie['action'] == 'patrol':

			#patrol
			ddx = baddie['dir']*baddie['speed']
			ddy = randint(-1,1)

		if baddie['action'] == 'random':

			dx = randint(0,baddie['speed'])
			dy = randint(0,baddie['speed'])

			ddx = randint(-dx,dx)
			ddy = randint(-dy,dy)

	return ddx, ddy



def refreshGlobals():

	global uidDict
	global rectList
	global prizeList
	global baddieList
	global uidCount
	global bonesList
	global colsChosen
	global canvasDim

	uidDict = {}
	rectList = []
	prizeList = []
	baddieList = []
	uidCount = 0
	bonesList = []
	colsChosen = {}
	canvasDim = {}


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
			
			# print(prize['func'])

			funcDict = {"addValue":addValue, "addHealth":addHealth}
			specificObjectDict = funcDict[prize['func']](specificObjectDict, prize, index)

			# c = specificObjectDict.get('score', 0)
			# specificObjectDict['score'] = c + prize['value']
			# prizeList.pop(index)
			
	return specificObjectDict

def addValue(specificObjectDict, prize, index):

	global prizeList
	c = specificObjectDict.get('score', 0)
	specificObjectDict['score'] = c + prize['value']
	prizeList.pop(index)
	return specificObjectDict

def addHealth(specificObjectDict, prize, index):

	global prizeList
	specificObjectDict['health']['hearts'] = specificObjectDict['health']['hearts'][::-1].replace(u'♡',u'♥',1)[::-1]
	specificObjectDict['health']['level'] += 1
	prizeList.pop(index)
	return specificObjectDict

# def collisionWithBaddie(specificObjectDict, baddie, i, uid):

# 	global bonesList

# 	# create collison for baddies
# 	if sqOnSqCollision(specificObjectDict, baddie) and specificObjectDict['state'] == 'rest':
# 		baddieList.pop(i)
# 		bonesList.append({'x':baddie['x'],'y':baddie['y']})
# 		# specificObjectDict = getHurt(specificObjectDict, uid)
# 		getHurt(specificObjectDict, uid)

# 	return specificObjectDict

def collisionWithBaddie(specificObjectDict, baddie, i, uid):

	global bonesList

	# create collison for baddies
	if sqOnSqCollision(specificObjectDict, baddie) and specificObjectDict['state'] == 'rest':
		baddieList.pop(i)
		bonesList.append({'x':baddie['x'],'y':baddie['y']})
		# specificObjectDict = getHurt(specificObjectDict, uid)

		getHurt(specificObjectDict, uid)

	return specificObjectDict

def checkCollisionWithBaddie(specificObjectDict, baddie, i, uid):
	return sqOnSqCollision(specificObjectDict, baddie) and specificObjectDict['state'] == 'rest'


def getHurt(specificObjectDict, uid):

	global uidDict
	global globalHeaduid

	# specificObjectDict['w'] -= 10
	# specificObjectDict['h'] -= 10

	specificObjectDict['health']['hearts'] = specificObjectDict['health']['hearts'].replace(u'♥',u'♡',1)
	specificObjectDict['health']['level'] -= 1
	specificObjectDict['r'] = 25
	specificObjectDict['cc'] = "#CC1100"

	if specificObjectDict['health']['level'] <= 0: 
	# if specificObjectDict['w'] <= 0:
			uidDict.pop(uid, None)

			if not uidDict:
				refreshGlobals()
				msg = "Global variables refreshed."
				emit('refreshGlobalsPush', {"msg":msg}, broadcast=True,) 
			else:
				globalHeaduid = min(uidDict.keys())
				
			# globalHeaduid = min(uidDict.keys())

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
	socketio.run(app, host= '0.0.0.0', port=6020)
	# socketio.run(app, host= '127.0.0.1', port=6020)