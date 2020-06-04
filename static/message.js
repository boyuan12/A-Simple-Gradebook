window.onload = function(e){
    $("#messageForm").submit(function(e) {
        e.preventDefault();
    });

    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    socket.on('connect', () => {
        button = document.getElementById('sendMessageButton');
        button.onclick = () => {
            console.log('clicked');
            var message = document.getElementById("message").value;
            socket.emit('broadcast message', {'message': message});
        };
    });

    socket.on('show message', data => {
        console.log(data.message)
    })

};