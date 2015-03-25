

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


    tile_size = Math.min(canvas.width / world_width, canvas.height / world_height)
    canvas.width = tile_size * world_width
    canvas.height = tile_size * world_height

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
    draw_walls(rect_json)
    draw_badguys(badguy_json)
    draw_players(player_json)
    attack(player_json)

}


function scale_x_y_w_h(x, y, w, h){
    return {"x":width_ratio*x, "y":height_ratio*y, "w":width_ratio*w, "h":height_ratio*h}
}


function draw_circle(color,x,y,r){

    ctx.fillStyle = color;
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

}


function draw_rect(color, x, y, w, h){

    ctx.fillStyle = color;
    ctx.fillRect(x, y, w, h);

}


function draw_walls(rect_json){

    for (i = 0; i < rect_json.length; i++) { 
        r_dict = scale_x_y_w_h(rect_json[i].x, rect_json[i].y, rect_json[i].width, rect_json[i].height)
        draw_rect(rect_json[i].color, r_dict['x'], r_dict['y'], r_dict['w'], r_dict['h'])
    }

}


function draw_character(character_json, image){
        c_dict = scale_x_y_w_h(character_json[i].x, character_json[i].y, character_json[i].width, character_json[i].height)
        ctx.drawImage(image, c_dict['x'], c_dict['y'], c_dict['w'], c_dict['h']);
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


function attack(player_json){


    for (i = 0; i < player_json.length; i++) { 


        p_dict = scale_x_y_w_h(player_json[i]['x'], player_json[i]['y'], player_json[i]['width'], player_json[i]['height'])

        player_y_center = (p_dict['y'] + p_dict['y'] + p_dict['h'] ) / 2.0
        player_x_center = (p_dict['x'] + p_dict['x'] + p_dict['w']) / 2.0

        attack_x_center = player_x_center + player_json[i]['attack_x_direction']*p_dict['w']
        attack_y_center = player_y_center + player_json[i]['attack_y_direction']*p_dict['h']

        draw_circle("#C1F0F6", attack_x_center, attack_y_center, p_dict['w'])

 
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

















