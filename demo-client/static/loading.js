document.addEventListener("DOMContentLoaded", function () {
    var socket = io();
    socket.on("connect", function () {
        console.log("Connected to WebSocket");
    });

    socket.on("new_data", function (data) {
        window.location.href = "/topic";
    });
});