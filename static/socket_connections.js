
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
    
        //n 110
        // if(keyState[78]) {
        //     socket.emit('refreshGlobalsRequest', {});
        // }

        //l 76 space 32
        // else if(keyState[32]) {

        //     if (!mult) {
        //         mult = true;
        //         setTimeout(function() {
        //             mult = false;
        //         }, 500)
        //         socket.emit('attackRequest', {});
        //     }
        // }
            
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

                //speed up uni-diectional movement 
                //since you travel farther in diagnola
                // if (x == 0){
                //     y = y*1.35
                // }
                // if (y == 0){
                //     x = x*1.35
                // }

                socket.emit('keypress_request', {"type":"player_movement", "dx": x, "dy": y});

        }

        timer  = setTimeout(listenForKeypressLoop, 20);

}





});