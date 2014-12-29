$(document).ready(function(){





var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');

socket.on('connectPush', function(d) {
    console.log(d.msg);
});

socket.on('refreshGlobalsPush', function(d) {
    console.log(d.msg);
    location.reload();
});

socket.emit('createCanvasRequest', {"w":document.body.clientWidth, "h":document.body.clientHeight});

var ipDict;

socket.on('createCanvasPush', function(d) {
    // console.log(d.msg);
    $("body").css({"backgroundColor":d['bgcolor']});
    createCanvas(d.rectList, d.prizeList, d.baddieList, d.ipDict, d.ip);

});




var canvas;
var ctx;
var rectList;
var prizeList; 
var baddieList; 


// function badGuysMove() {
// 	socket.emit('incrementBagGuysPositionRequest', {});
// 	var loopTimer = setTimeout(badGuysMove, 100);
// }

socket.on('incrementBagGuysPositionPush', function(d) {
    baddieList = d.baddieList;
    draw(d.ipDict);
});



function createCanvas(rL,pL,bL,ipDict,ip) {

	//create full screen canvas
	canvas = document.getElementById("canvas");
	canvas.width = document.body.clientWidth;
	canvas.height = document.body.clientHeight;
	ctx = canvas.getContext("2d");
	rectList = rL
	prizeList = pL
	baddieList = bL
	// circle = cD

	draw(ipDict);
	// socket.emit('incrementBagGuysPositionRequest');
	
}




// badGuysMove();



socket.on('keypressPush', function(d) {

	prizeList = d.prizeList;
	baddieList = d.baddieList;
    x = d.ipDict[d.ip]['x']//['playerDict']['x'];
    y = d.ipDict[d.ip]['y']//['playerDict']['y'];
    draw(d.ipDict);

});





// function draw(x,y,ipDict,ip) {
function draw(ipDict) {


	//clear canvas
	ctx.clearRect(0, 0, canvas.width, canvas.height);

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


	wizColorDict = {"red":[wizard_red_left,wizard_red_right],
					"blu":[wizard_blu_left,wizard_blu_right],
					"gre":[wizard_gre_left,wizard_gre_right],
					"yel":[wizard_yel_right,wizard_yel_right],
					}

	// coin.onload = function() {
		
	// }

	for (i = 0; i < rectList.length; i++) { 
		ctx.fillStyle = rectList[i].c;
		ctx.fillRect(rectList[i].x, rectList[i].y, rectList[i].w, rectList[i].h);
	}

	for (i = 0; i < prizeList.length; i++) { 
		// ctx.fillStyle = prizeList[i].c;
		// ctx.fillRect(prizeList[i].x, prizeList[i].y, prizeList[i].w, prizeList[i].h);

		if (i % 7 == 0) {
			ctx.drawImage(ruby, prizeList[i].x, prizeList[i].y, prizeList[i].w, prizeList[i].h);
		}
		else{
			ctx.drawImage(coin, prizeList[i].x, prizeList[i].y, prizeList[i].w, prizeList[i].h);
		}
	
	}

	for (i = 0; i < baddieList.length; i++) { 
		// ctx.fillStyle = baddieList[i].c;
		// ctx.fillRect(baddieList[i].x, baddieList[i].y, baddieList[i].w, baddieList[i].h);
		if (baddieList[i]['dx']>=0){
			image = goblin_right;
		}
		else{
			image = goblin_left;
		}

		ctx.drawImage(image, baddieList[i].x, baddieList[i].y, baddieList[i].w, baddieList[i].h);
	}

	offset = 0
	for (i = 0; i < Object.keys(ipDict).length; i++) { 




		ip = Object.keys(ipDict)[i]
		circle = ipDict[Object.keys(ipDict)[i]]//['playerDict']
		dx = circle['dx']
		dy = circle['dy']
		x = circle['x']
		y = circle['y']
		// r = circle['r']
		w = circle['w']
		h = circle['h']

		// w = ipDict[Object.keys(ipDict)[i]]['radius']
		// h = ipDict[Object.keys(ipDict)[i]]['radius']

		// c = circle['c']
		state = circle['state']
		r = circle['r']

		cx = x + w/2
		cy = y + h/2

		// console.log(circle['id']);
		// var col;
		if (circle['id'] == 0){
			col = 'blu';
		}
		if (circle['id'] == 1){
			col = 'red';
		}
		if (circle['id'] == 2){
			col = 'gre';
		}
		if (circle['id'] == 3){
			col = 'yel';
		}

		// console.log(col);


		textColor = ipDict[Object.keys(ipDict)[i]]['c']//['playerDict']['c']

			ctx.fillStyle = '#CD96CD';
			ctx.beginPath();
			ctx.arc(
				cx,
				cy,
				r,
				0, 
				Math.PI * 2
			);
			ctx.closePath();
			ctx.fill();

			if (dx>=0){
				// console.log(dx);
				wiz_image = wizColorDict[col][1];
			}
			else if (dx<0){
				// console.log(dx);
				wiz_image = wizColorDict[col][0];
			}
			else {
				wiz_image = wizColorDict[col][0];
			}


			ctx.drawImage(wiz_image, x, y, w, h);

			
			// textToPrint = Object.keys(ipDict)[i] + ": " + ipDict[Object.keys(ipDict)[i]]['score'] + ", "
			
			
			if (ipDict[Object.keys(ipDict)[i]]['score'] == undefined) {
				score = 0
			}
			else{
				score = ipDict[Object.keys(ipDict)[i]]['score']
			}


			textToPrint = score + " "
	    	ctx.fillStyle = textColor;
		  	ctx.font = "bold 50px Arial";
		  	ctx.fillText(textToPrint, 20 + offset, canvas.height - 20);
		  	offset += 100
		
	}

	// textToPrint = ''
	// ipList = Object.keys(ipDict);
 //    for (i = 0; i < ipList.length; i++) { 
    	

    // }

	


}





// var timer = null;

// function doStuff(x,y) {
//     socket.emit('keypressRequest', {"dx": x, "dy": y});
//     // console.log(x);
// }


var keyState = {};    
window.addEventListener('keydown',function(e){
	// console.log(e.which);
    keyState[e.keyCode || e.which] = true;
},true);    
window.addEventListener('keyup',function(e){
    keyState[e.keyCode || e.which] = false;
},true);

// x = 100;



var mult;
var gameCount=1;
// $(document).keydown(function(e) {
function gameLoop() {
	

		

		//n 110
		if(keyState[78]) {
			socket.emit('refreshGlobalsRequest', {});
		}
		//l 76 space 32
		if(keyState[32]) {

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
					y -= stepSize
				}
				//a 97
				if(keyState[65]) {
					x -= stepSize
				}
				// s 115
				if(keyState[83]){
					y += stepSize
				}
				// d 100
				if(keyState[68]) {
					x += stepSize
				}

				socket.emit('keypressRequest', {"dx": x, "dy": y});

		}

		setTimeout(gameLoop, 20);

		gameCount = gameCount + 1;

		if (gameCount == 5){
			socket.emit('incrementBagGuysPositionRequest', {});
			gameCount = 1
		}


		// socket.emit('incrementBagGuysPositionRequest', {});
		// var loopTimer = setTimeout(badGuysMove, 100);
}
// });

gameLoop();


// 	// $('#form').submit(function(event) {

// 		// $.post('/endpoint', JSON.stringify({"a":$("#formData").val()}), function(d) {

// 		//     $("body").append("<div>"+d["result"]+"</div>");

// 		// });
 
// 	//     return false;

// 	// });


});







	
//   	var canvas = document.getElementById("canvas");
// 	canvas.width = document.body.clientWidth;
// 	canvas.height = document.body.clientHeight;
//     var context = canvas.getContext("2d");


// 	function drawFractalTree(context, x, y){

// 		drawTree(context, x, y, -90, 11);
// 	}

// 	function drawTree(context, x1, y1, angle, depth){

// 		var BRANCH_LENGTH = random(0, 3);

// 		if (depth != 0){
// 			var x2 = x1 + (cos(angle) * depth * BRANCH_LENGTH);
// 			var y2 = y1 + (sin(angle) * depth * BRANCH_LENGTH);
			
// 			drawLine(context, x1, y1, x2, y2, depth);
// 			drawTree(context, x2, y2, angle - random(15,20), depth - 1);
// 			drawTree(context, x2, y2, angle + random(15,20), depth - 1);
// 		}
// 	}

// 	function drawLine(context, x1, y1, x2, y2, thickness){
// 		context.fillStyle   = '#000';
// 		// if(thickness > 6)	
// 			context.strokeStyle = 'rgb(139,126, 102)'; //Brown		
// 		// else
// 			// context.strokeStyle = 'rgb(34,139,34)'; //Green

// 		context.lineWidth = thickness * 0.3;
// 		context.beginPath();

// 		context.moveTo(x1,y1);
// 		context.lineTo(x2, y2);

// 		context.closePath();
// 		context.stroke();
// 	}


// 	function cos (angle) {
// 		return Math.cos(deg_to_rad(angle));
// 	}

// 	function sin (angle) {
// 		return Math.sin(deg_to_rad(angle));
// 	}

// 	function deg_to_rad(angle){
// 		return angle*(Math.PI/180.0);
// 	}

// 	function random(min, max){
// 		return min + Math.floor(Math.random()*(max+1-min));
// 	}



// drawFractalTree(context, 500, 500); 
// drawFractalTree(context, 300, 400); 





