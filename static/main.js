

var goblin_left = new Image();
var goblin_right = new Image();
goblin_left.src = "https://i.imgur.com/gB7lEU5.png";
goblin_right.src = "https://i.imgur.com/WYwdG3Z.png";


var rat_left = new Image();
var rat_right = new Image();
rat_left.src = "https://i.imgur.com/GqhYJ7I.png";
rat_right.src = "https://i.imgur.com/rg33icE.png";

var wizard_blu_left = new Image();
var wizard_blu_right = new Image();
wizard_blu_left.src = "https://i.imgur.com/k2ob4Wl.png";
wizard_blu_right.src = "https://i.imgur.com/HLY8Ipk.png";





var canvas
var ctx
var width_ratio
var height_ratio
function create_canvas(world_width, world_height) {

    canvas = document.getElementById("canvas");
    canvas.width = document.body.clientWidth;
    canvas.height = document.body.clientHeight;
    ctx = canvas.getContext("2d");

    width_ratio = canvas.width / world_width
    height_ratio = canvas.height / world_height

}


function clear_canvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#659D32";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
}



function update_canvas(badguy_json, rect_json, player_json) {

    clear_canvas()
    draw_rects(rect_json)
    draw_badguys(badguy_json)
    draw_players(player_json)

}


function draw_rects(rect_json){

    //rectangles
    for (i = 0; i < rect_json.length; i++) { 

        rect_width = width_ratio*rect_json[i].width
        rect_height = height_ratio*rect_json[i].height
        rect_x = width_ratio*rect_json[i].x
        rect_y = height_ratio*rect_json[i].y

        ctx.fillStyle = rect_json[i].color;
        ctx.fillRect(rect_x, rect_y, rect_width, rect_height);
    }

}


function draw_character(character_json, image){

        character_width = width_ratio*character_json[i].width
        character_height = height_ratio*character_json[i].height
        character_x = width_ratio*character_json[i].x
        character_y = height_ratio*character_json[i].y

        cx = character_x + character_width/2
        cy = character_y + character_height/2

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

        ctx.drawImage(image, character_x, character_y, character_width, character_height);

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

        draw_character(badguy_json, image)

    }
}




function draw_players(player_json){

    for (i = 0; i < player_json.length; i++) { 

        if (player_json[i]['dx']>=0){
            image = wizard_blu_right;
        }
        else{
            image = wizard_blu_left;
        }

        draw_character(player_json, image)

    }

}




//keypresses
var keyState = {};
var mult;

window.addEventListener('keydown',function(e){
    keyState[e.keyCode || e.which] = true;
},true);    
window.addEventListener('keyup',function(e){
    keyState[e.keyCode || e.which] = false;
},true);

















