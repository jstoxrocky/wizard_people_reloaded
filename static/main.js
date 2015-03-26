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
var bones = new Image();
var rat_left = new Image();
var rat_right = new Image();
var gobking_left = new Image();
var gobking_right = new Image();
var potion = new Image();

gobking_left.src = "http://i.imgur.com/alUMAKk.png";
gobking_right.src = "http://i.imgur.com/9Bwvh9H.png";
potion.src = "http://i.imgur.com/zLS5Tqf.png";
coin.src = "https://i.imgur.com/wOxaRHq.png";
ruby.src = "https://i.imgur.com/bAsFNAZ.png"
goblin_left.src = "https://i.imgur.com/gB7lEU5.png";
goblin_right.src = "https://i.imgur.com/WYwdG3Z.png";
wizard_red_left.src = "https://i.imgur.com/ZDSfndn.png";
wizard_red_right.src = "https://i.imgur.com/wkONQZ8.png";
wizard_blu_left.src = "https://i.imgur.com/k2ob4Wl.png";
wizard_blu_right.src = "https://i.imgur.com/HLY8Ipk.png";
wizard_gre_left.src = "https://i.imgur.com/HsyJz43.png";
wizard_gre_right.src = "https://i.imgur.com/QvhDDL5.png";
wizard_yel_left.src = "https://i.imgur.com/b3oV1mG.png";
wizard_yel_right.src = "https://i.imgur.com/ICC5ViR.png";
bones.src = "https://i.imgur.com/cXrOQAK.png";
rat_left.src = "https://i.imgur.com/GqhYJ7I.png";
rat_right.src = "https://i.imgur.com/rg33icE.png";



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



function update_canvas(badguy_json, rect_json, player_json, orb_json) {

    clear_canvas()
    draw_walls(rect_json)
    draw_badguys(badguy_json)
    draw_players(player_json)
    draw_orbs(orb_json)
    draw_health(player_json)

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

        c_dict = scale_x_y_w_h(character_json.x, character_json.y, character_json.width, character_json.height)
        ctx.drawImage(image, c_dict['x'], c_dict['y'], c_dict['w'], c_dict['h']);
        

        if (character_json.is_mortal==false){

            center_x = c_dict.x + (c_dict.w/2)
            center_y = c_dict.y + (c_dict.h/2)


            ctx.save();
            ctx.globalAlpha = 0.4;
            draw_circle("#FFCCCC", center_x, center_y, c_dict.w/1.5)
            ctx.restore();
        }

        
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

        draw_character(badguy_json[i], image)

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

        draw_character(player_json[i], image)

    }

}


function draw_orbs(orb_json){


    for (i = 0; i < orb_json.length; i++) { 


        o_dict = scale_x_y_w_h(orb_json[i]['x'], orb_json[i]['y'], orb_json[i]['width'], orb_json[i]['width'])

        draw_circle("#C1F0F6", o_dict['x'], o_dict['y'], o_dict['w'])


    }



}




function draw_health(player_json){

    offset = 0
    for (i = 0; i < player_json.length; i++) { 

        textToPrint = player_json[i]['hearts'] 
        ctx.fillStyle = "#104E8B";
        ctx.font = "bold 50px Arial";
        ctx.fillText(textToPrint, 20 + offset, canvas.height - 20);
        offset += 300

    }

}



function drawstartScreen(){

    wizard_yel_right.onload = function() {
        ctx.drawImage(wizard_red_right, 0, 0, canvas.width/2, canvas.height/2);
        ctx.drawImage(wizard_blu_right, canvas.width-canvas.width/2, 0, canvas.width/2, canvas.height/2);
        ctx.drawImage(wizard_yel_right, 0, canvas.height-canvas.height/2, canvas.width/2, canvas.height/2);
        ctx.drawImage(wizard_gre_right, canvas.width-canvas.width/2, canvas.height-canvas.height/2, canvas.width/2, canvas.height/2);

    }


}




function updatestartScreen(){

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    ctx.drawImage(wizard_red_right, 0, 0, canvas.width/2, canvas.height/2);
    ctx.drawImage(wizard_blu_right, canvas.width-canvas.width/2, 0, canvas.width/2, canvas.height/2);
    ctx.drawImage(wizard_yel_right, 0, canvas.height-canvas.height/2, canvas.width/2, canvas.height/2);
    ctx.drawImage(wizard_gre_right, canvas.width-canvas.width/2, canvas.height-canvas.height/2, canvas.width/2, canvas.height/2);


    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 50px Arial";
    ctx.fillText(redTextToPrint, 0, canvas.height/2);

    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 50px Arial";
    ctx.fillText(bluTextToPrint, canvas.width/2, canvas.height/2);

    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 50px Arial";
    ctx.fillText(greTextToPrint, canvas.width/2, canvas.height);

    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 50px Arial";
    ctx.fillText(yelTextToPrint, 0, canvas.height);

}





function clicker(){

    $("body").click(function(event){  

    $( ".startText" ).fadeOut( "slow", function() {
    // Animation complete.
    });



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

    if (uidDict == undefined){
        socket.emit('player_choose_request', {"col":col});
    }
    
});

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

















