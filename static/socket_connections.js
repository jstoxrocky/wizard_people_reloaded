
$(document).ready(function(){


// $("black_box").append("<p class='startText' id='title'>WIZARD PEOPLE</p>")
// $("black_box").append("<p class='startText' id='instructions'>CLICK TO SELECT A WIZARD</p>")
// $("black_box").append("<p class='startText' id='instructions2'>WAIT FOR OTHER PLAYERS</p>")
// $("black_box").append("<p class='startText' id='instructions3'>PRESS ENTER TO BEGIN</p>")

// $("black_box").append("<p class='startText' id='instructions4'>A,S,W,D TO MOVE</p>")
// $("black_box").append("<p class='startText' id='instructions5'>ARROW KEYS TO CAST SPELLS</p>")
$(".startText").show()


//connection
var socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('connect', function() {
    socket.emit('connect');
});




//create canvas
socket.on('connection_response', function(d) {


        console.log(d.msg);
        initialize_canvas()
        drawstartScreen();
        updatestartScreen(d.player_chosen_colors_dict.red, d.player_chosen_colors_dict.blu, d.player_chosen_colors_dict.gre, d.player_chosen_colors_dict.yel)
        clicker();

});


//create canvas
socket.on('start_game_response', function(d) {

    console.log(d.msg);
    create_map(d.world_width, d.world_height)


});




//update canvas
socket.on('get_game_state_response', function(d) {

    update_canvas(d.badguy_json, d.rect_json, d.player_json, d.orb_json, d.room_json, d.bone_json)

    if (d.game_json > 0) {
        console.log("game over")
        $( ".bdiv").fadeIn( "slow", function() {
            $( "#title").fadeIn( "slow", function() {


            });
        });
    }

});


//player choose response
socket.on('player_choose_response', function(d) {

    console.log(d.msg);
    updatestartScreen(d.player_chosen_colors_dict.red, d.player_chosen_colors_dict.blu, d.player_chosen_colors_dict.gre, d.player_chosen_colors_dict.yel)

});


listenForKeypressLoop();



function listenForKeypressLoop() {
    

            
        if (keyState[87] || keyState[65] || keyState[83] || keyState[68]) {

                x = 0;
                y = 0;

                //w 119
                if(keyState[87]) {
                    y -= 1;
                }
                //a 97
                if(keyState[65]) {
                    x -= 1;
                }
                // s 115
                if(keyState[83]){
                    y += 1;
                }
                // d 100
                if(keyState[68]) {
                    x += 1;
                }

                socket.emit('keypress_request', {"type":"player_movement", "dx": x, "dy": y});

        }


        timer  = setTimeout(listenForKeypressLoop, 20);

}



$(document).keydown(function(e) {

    x = 0;
    y = 0;

    if (e.which == 37 || e.which == 38 || e.which == 39 || e.which == 40) {

        if (e.which == 37) {
            // console.log("left")
            x -= 1;
        }
            if (e.which == 38) {
            // console.log("left")
            y -= 1;
        }
            if (e.which == 39) {
            // console.log("left")
            x += 1;
        }
            if (e.which == 40) {
            // console.log("left")
            y += 1;
        }

        socket.emit('keypress_request', {"type":"attack", "attack_x_direction": x, "attack_y_direction": y});

    }

    if(e.which == 13) {
        socket.emit('start_game_request',{});
    }
    
    if(e.which == 82) {
        socket.emit('reset_game_request',{});
    }


});





function clicker(){

    $("body").click(function(event){  

        $( ".startText" ).fadeOut( "slow", function() {
        // Animation complete.
        });

        $( ".bdiv" ).fadeOut( "slow", function() {
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

        // if (uidDict == undefined){
        socket.emit('player_choose_request', {"col":col});
    // }
    
    });

}




});