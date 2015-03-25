
$(document).ready(function(){


//connection
var socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('connect', function() {
    socket.emit('connect');
});




//create canvas
socket.on('connection_response', function(d) {

    console.log(d.msg);
    console.log("Creating canvas.")
    create_canvas(d.world_width, d.world_height)

});




//update canvas
socket.on('get_game_state_response', function(d) {

    console.log(d.msg);
    update_canvas(d.badguy_json, d.rect_json, d.player_json)

});


//key press response
socket.on('key_press_response', function(d) {

    // console.log(d.msg);

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


        if (keyState[37] || keyState[38] || keyState[39] || keyState[40]) {

                x = 0;
                y = 0;

                //w 119
                if(keyState[38]) {
                    y -= 1;
                }
                //a 97
                if(keyState[37]) {
                    x -= 1;
                }
                // s 115
                if(keyState[40]){
                    y += 1;
                }
                // d 100
                if(keyState[39]) {
                    x += 1;
                }

                socket.emit('keypress_request', {"type":"attack", "attack_x_direction": x, "attack_y_direction": y});

        }

        timer  = setTimeout(listenForKeypressLoop, 20);

}





});