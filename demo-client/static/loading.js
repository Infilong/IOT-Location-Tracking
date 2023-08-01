document.addEventListener("DOMContentLoaded", function () {
  var socket = io();
  // Function to show the alert box when the 'new_data' event is not triggered
  function showAlert() {
    const alertMessage =
      "No new data received. Click 'OK' to return to the subscribe page.";
    if (confirm(alertMessage)) {
      // Redirect the user to the subscribe page when they click 'OK'
      window.location.href = "/subscribe";
    }
  }

  // Set a timer for 10 seconds
  const timer = setTimeout(showAlert, 20000);

  // Event listener for the 'new_data' event
  socket.on("connect", function () {
    console.log("Connected to WebSocket");
  });

  socket.on("new_data", function (data) {
    window.location.href = "/topic";
  });
});
