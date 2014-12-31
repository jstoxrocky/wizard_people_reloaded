$(document).ready(function(){

var ipDict;
var canvas;
var ctx;
var rectList;
var prizeList; 
var baddieList; 

var coin = new Image();
var ruby = new Image();
var goblin_left = new Image();
var goblin_right = new Image();
var wizard_red_left = new Image();
var wizard_red_right = new Image();
var wizard_blu_left = new Image();
var wizard_blu_right = new Image();
var wizard_gre_left = new Image();
var wizard_gre_right = new Image();
var wizard_yel_left = new Image();
var wizard_yel_right = new Image();

coin.src = "static/images/coin.png";
ruby.src = "static/images/ruby.png";
goblin_left.src = "static/images/goblin_left.png";
goblin_right.src = "static/images/goblin_right.png";
wizard_red_left.src = "static/images/wiz_red_left.png";
wizard_red_right.src = "static/images/wiz_red_right.png";
wizard_blu_left.src = "static/images/wiz_blu_left.png";
wizard_blu_right.src = "static/images/wiz_blu_right.png";
wizard_gre_left.src = "static/images/wiz_gre_left.png";
wizard_gre_right.src = "static/images/wiz_gre_right.png";
wizard_yel_left.src = "static/images/wiz_yel_left.png";
wizard_yel_right.src = "static/images/wiz_yel_right.png";

var wizColorDict = {"red":[wizard_red_left,wizard_red_right],
					"blu":[wizard_blu_left,wizard_blu_right],
					"gre":[wizard_gre_left,wizard_gre_right],
					"yel":[wizard_yel_right,wizard_yel_right],
					}

var prizeTypeDict = {"coin":coin,
					"ruby":ruby,
					}

var googleColorDict = {'blu':'#0266C8', 'red':'#F90101', 'yel':'#F2B50F', 'gre':'#00933B'}


function drawstartScreen(){

	canvas = document.getElementById("canvas");
	canvas.width = document.body.clientWidth;
	canvas.height = document.body.clientHeight;
	ctx = canvas.getContext("2d");
	// ctx.clearRect(0, 0, canvas.width, canvas.height);

	wizard_yel_right.onload = function() {
  		ctx.drawImage(wizard_red_right, 0, 0, canvas.width/2, canvas.height/2);
  		ctx.drawImage(wizard_blu_right, canvas.width-canvas.width/2, 0, canvas.width/2, canvas.height/2);
  		ctx.drawImage(wizard_yel_right, 0, canvas.height-canvas.height/2, canvas.width/2, canvas.height/2);
  		ctx.drawImage(wizard_gre_right, canvas.width-canvas.width/2, canvas.height-canvas.height/2, canvas.width/2, canvas.height/2);

  // 		textToPrint = "click on wizard to start game"
		// ctx.fillStyle = "#ffffff";
	 //  	ctx.font = "bold 50px Arial";
	 //  	ctx.fillText(textToPrint, 0, canvas.height/2);
  	}



	
	

  	

}



$("body").click(function(event){    
	x = event.pageX;
	y = event.pageY;

	if (x >= canvas.width/2){
		if (y >= canvas.height/2) {
			col = "gre"
		}
		else {
			col = "blu"
		}
	}
	else {
		if (y >= canvas.height/2) {
			col = "yel"
		}
		else {
			col = "red"
		}
	}

	// console.log("player X chose wizard " + col);
	if (ipDict == undefined){
		socket.emit('playerChooseRequest', {"col":col});
	}
	//socket.emit('createCanvasRequest', {"w":document.body.clientWidth, "h":document.body.clientHeight, "col":col});

});




$(document).keypress(function(e) {
    if(e.which == 13) {
		socket.emit('createCanvasRequest', {"w":document.body.clientWidth, "h":document.body.clientHeight});
    }
});



//connection Request
var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');



socket.on('playerChoosePush', function(d) {
    console.log(d.msg);
    alert(d.msg);
    // drawstartScreen();
    // socket.emit('createCanvasRequest', {"w":document.body.clientWidth, "h":document.body.clientHeight});

});




window.onbeforeunload = function() {
    // return "Are you sure you wish to leave the page?";
    // console.log("hi");
    socket.emit('popPlayerRequest', {});

}






//connection Push
socket.on('connectPush', function(d) {
    console.log(d.msg);
    // drawstartScreen();
    return false;
});

drawstartScreen();


//refresh global variables Push
socket.on('refreshGlobalsPush', function(d) {
    console.log(d.msg);
    location.reload();
});



//refresh global variables Push
socket.on('gameInProgressPush', function(d) {
    alert(d.msg);
});




socket.on('popPlayerPush', function(d) {
    console.log(d.msg);
});


//on document load  create Canvas request
//socket.emit('createCanvasRequest', {"w":document.body.clientWidth, "h":document.body.clientHeight});

//create canvas Push
socket.on('createCanvasPush', function(d) {
    $("body").css({"backgroundColor":d['bgcolor']});
    createCanvas(d.rectList, d.prizeList, d.baddieList);
    // gameLoop();
});

//game loop Push
socket.on('incrementBagGuysPositionPush', function(d) {
    baddieList = d.baddieList;
    ipDict = d.ipDict;
    draw();
});

//keypress Push
socket.on('keypressPush', function(d) {

	prizeList = d.prizeList;
	baddieList = d.baddieList;
    ipDict = d.ipDict;
    draw();

});






function createCanvas(rL,pL,bL) {

	rectList = rL;
	prizeList = pL;
	baddieList = bL;
	gameLoop();

}








function draw() {

	ctx.clearRect(0, 0, canvas.width, canvas.height);

	//rectangles
	for (i = 0; i < rectList.length; i++) { 
		ctx.fillStyle = rectList[i].c;
		ctx.fillRect(rectList[i].x, rectList[i].y, rectList[i].w, rectList[i].h);
	}

	//prizes
	for (i = 0; i < prizeList.length; i++) { 

		ctx.drawImage(prizeTypeDict[prizeList[i].prizeType], prizeList[i].x, prizeList[i].y, prizeList[i].w, prizeList[i].h);
	
	}

	//baddies
	for (i = 0; i < baddieList.length; i++) { 
		
		if (baddieList[i]['dx']>=0){
			image = goblin_right;
		}
		else{
			image = goblin_left;
		}

		ctx.drawImage(image, baddieList[i].x, baddieList[i].y, baddieList[i].w, baddieList[i].h);
	}

	//players
	offset = 0
	ipList = Object.keys(ipDict)
	for (i = 0; i < ipList.length; i++) { 

		p = ipDict[ipList[i]]

		cx = p['x'] + p['w']/2
		cy = p['y'] + p['h']/2

		textColor = googleColorDict[p['c']]

			ctx.fillStyle = '#CD96CD';
			ctx.beginPath();
			ctx.arc(
				cx,
				cy,
				p['r'],
				0, 
				Math.PI * 2
			);
			ctx.closePath();
			ctx.fill();

			if (p['dx']>=0){
				wiz_image = wizColorDict[p['c']][1];
			}
			else if (p['dx']<0){
				wiz_image = wizColorDict[p['c']][0];
			}
			else {
				wiz_image = wizColorDict[p['c']][0];
			}

			ctx.drawImage(wiz_image, p['x'], p['y'], p['w'], p['h']);

			
			if (p['score'] == undefined) {
				score = 0
			}
			else{
				score = p['score']
			}

			textToPrint = score + " " + reverse(p['health']['hearts']) + " "
	    	ctx.fillStyle = textColor;
		  	ctx.font = "bold 50px Arial";
		  	ctx.fillText(textToPrint, 20 + offset, canvas.height - 20);
		  	offset += 300
		
	}
}


//keypresses
var keyState = {};
var mult;
var gameCount=1;

window.addEventListener('keydown',function(e){
    keyState[e.keyCode || e.which] = true;
},true);    
window.addEventListener('keyup',function(e){
    keyState[e.keyCode || e.which] = false;
},true);

function gameLoop() {
	
		// draw();

		//n 110
		if(keyState[78]) {
			socket.emit('refreshGlobalsRequest', {});
		}

		//l 76 space 32
		else if(keyState[32]) {

			if (!mult) {
		        mult = true;
		        setTimeout(function() {
		            mult = false;
		        }, 500)
		        socket.emit('attackRequest', {});
		    }
    	}
			
		else {

				x = 0;
				y = 0;
				stepSize = 4;

				//w 119
				if(keyState[87]) {
					y -= stepSize;
					// socket.emit('keypressRequest', {"dx": x, "dy": y});
				}
				//a 97
				if(keyState[65]) {
					x -= stepSize;
					// socket.emit('keypressRequest', {"dx": x, "dy": y});
				}
				// s 115
				if(keyState[83]){
					y += stepSize;
					// socket.emit('keypressRequest', {"dx": x, "dy": y});
				}
				// d 100
				if(keyState[68]) {
					x += stepSize;
					// socket.emit('keypressRequest', {"dx": x, "dy": y});
				}

				// socket.emit('keypressRequest', {"dx": x, "dy": y});
				
				//speed up uni-diectional movement 
				//since you travel farther in diagnola
				if (x == 0){
					y = y*1.42
				}
				if (y == 0){
					x = x*1.42
				}

				socket.emit('keypressRequest', {"dx": x, "dy": y});


		}

		setTimeout(gameLoop, 20);

		gameCount = gameCount + 1;

		if (gameCount == 5){
			socket.emit('incrementBagGuysPositionRequest', {});
			gameCount = 1
		}

}


// gameLoop();



});



function reverse(s){
    return s.split("").reverse().join("");
}





