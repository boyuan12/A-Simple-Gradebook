window.onload = function(e){
    $("#messageForm").submit(function(e) {
        e.preventDefault();
    });

    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    socket.on('connect', () => {
        button = document.getElementById('sendMessageButton');
        button.onclick = () => {
            // MM/DD/YY at HH:SS
            var month = new Date().getMonth();
            var day = new Date().getDay();
            var year = new Date().getFullYear();
            var h = new Date().getHours();
            var m = new Date().getMinutes();

            var _time = (h > 12) ? (h-12 + ':' + m +' PM') : (h + ':' + m +' AM')

            var timestamp = `${month}/${day}/${year} at ${_time}`
            var message = document.getElementById("message").value;
            socket.emit('broadcast message', {'message': message, "timestamp": timestamp});
        };
    });

    socket.on('show message', data => {
        console.log(data.message);
        console.log(data.name);
        console.log(data.timestamp);
        $(".container").append(`<small>${data.timestamp}</small><h4>${data.name}:</h4><p>${data.message}</p>`);
    })

};