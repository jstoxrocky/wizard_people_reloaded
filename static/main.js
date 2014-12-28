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
    console.log(d.msg);
    $("body").css({"backgroundColor":d['bgcolor']});
    createCanvas(d.rectList, d.prizeList, d.baddieList, d.ipDict, d.ip);

});




var canvas;
var ctx;
var rectList;
var prizeList; 
var baddieList; 


function badGuysMove() {
	socket.emit('incrementBagGuysPositionRequest', {});
	var loopTimer = setTimeout(badGuysMove, 100);
}

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




badGuysMove();



socket.on('keypressPush', function(d) {

	prizeList = d.prizeList;
	baddieList = d.baddieList;
    x = d.ipDict[d.ip]['circleDict']['x'];
    y = d.ipDict[d.ip]['circleDict']['y'];
    draw(d.ipDict);

});





// function draw(x,y,ipDict,ip) {
function draw(ipDict) {


	//clear canvas
	ctx.clearRect(0, 0, canvas.width, canvas.height);

	for (i = 0; i < rectList.length; i++) { 
		ctx.fillStyle = rectList[i].c;
		ctx.fillRect(rectList[i].x, rectList[i].y, rectList[i].w, rectList[i].h);
	}

	for (i = 0; i < prizeList.length; i++) { 
		ctx.fillStyle = prizeList[i].c;
		ctx.fillRect(prizeList[i].x, prizeList[i].y, prizeList[i].w, prizeList[i].h);
	}

	for (i = 0; i < baddieList.length; i++) { 
		ctx.fillStyle = baddieList[i].c;
		ctx.fillRect(baddieList[i].x, baddieList[i].y, baddieList[i].w, baddieList[i].h);
	}

	offset = 0
	for (i = 0; i < Object.keys(ipDict).length; i++) { 

		ip = Object.keys(ipDict)[i]
		circle = ipDict[Object.keys(ipDict)[i]]['circleDict']
		dx = circle['dx']
		dy = circle['dy']
		x = circle['x']
		y = circle['y']
		r = circle['r']
		c = circle['c']
		textColor = ipDict[Object.keys(ipDict)[i]]['color']

			ctx.fillStyle = c;
			ctx.beginPath();
			ctx.arc(
				x,
				y,
				r,
				0, 
				Math.PI * 2
			);
			ctx.closePath();
			ctx.fill();

			
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

		setTimeout(gameLoop, 10);
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





