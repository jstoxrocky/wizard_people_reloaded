$(document).ready(function(){

var goblin_left = new Image();
var goblin_right = new Image();
goblin_left.src = "https://i.imgur.com/gB7lEU5.png";
goblin_right.src = "https://i.imgur.com/WYwdG3Z.png";
var rat_left = new Image();
var rat_right = new Image();
rat_left.src = "https://i.imgur.com/GqhYJ7I.png";
rat_right.src = "https://i.imgur.com/rg33icE.png";






var canvas
var ctx
function create_canvas() {

    canvas = document.getElementById("canvas");
    canvas.width = document.body.clientWidth;
    canvas.height = document.body.clientHeight;
    ctx = canvas.getContext("2d");
}

function clear_canvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#659D32";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
}



function update_canvas(badguy_json) {

    clear_canvas()
    draw_badguys(badguy_json)

}


function draw_badguys(badguy_json){


    for (i = 0; i < badguy_json.length; i++) { 

            if (badguy_json[i]['type'] == 'goblin'){
                img_right = goblin_right;
                img_left = goblin_left;
            }
            else if (badguy_json[i]['type'] == 'rat'){
                img_right = rat_right;
                img_left = rat_left;
            }

            if (badguy_json[i]['dx']>=0){
                image = img_right;
            }
            else{
                image = img_left;
            }


            cx = badguy_json[i]['x'] + badguy_json[i]['width']/2
            cy = badguy_json[i]['y'] + badguy_json[i]['height']/2


            ctx.fillStyle = "#CC1100";
            ctx.beginPath();
            ctx.arc(
                cx,
                cy,
                0,
                0, 
                Math.PI * 2
            );
            ctx.closePath();
            ctx.fill();


        ctx.drawImage(image, badguy_json[i].x, badguy_json[i].y, badguy_json[i].width, badguy_json[i].height);

    }
}


















//connection 
// var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');


    var socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.on('connect', function() {
        socket.emit('connect');
    });



//connection
socket.on('connection_response', function(d) {

    console.log(d.msg);
    socket.emit('create_canvas_request', {});

});


//create canvas
socket.on('create_canvas_response', function(d) {

    console.log(d.msg);
    create_canvas()

});




//update canvas
socket.on('get_game_state_response', function(d) {

    console.log(d.msg);

    update_canvas(d.badguy_json)

});











});





