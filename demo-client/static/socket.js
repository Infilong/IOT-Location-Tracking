document.addEventListener("DOMContentLoaded", function () {
  var socket = io();
  var table = document.getElementById("data-table");
  var tbody = table.getElementsByTagName("tbody")[0];

  // Function to update the table with new data
  function updateTable(data) {
    // Clear the table content
    tbody.innerHTML = "";
    {
      for (var i = 0; i < data.length; i++) {
        var tr = document.createElement("tr");

        for (var key in data[i]) {
          var td = document.createElement("td");
          if (key === "Latitude" || key === "Longitude") {
            // Handle None values for Latitude and Longitude
            td.innerHTML = data[i][key] === null ? "None" : data[i][key];
          } else {
            td.innerHTML = data[i][key];
          }
          tr.appendChild(td);
        }
        tbody.appendChild(tr);
      }
    }
  }

  // When the WebSocket connection is established, get the initial data
  socket.on("connect", function () {
    console.log("Connected to WebSocket");
  });

  // When new_data event is received, update the table
  socket.on("new_data", function (data) {
    updateTable(data);
  });

  // Handle any errors that occur with the WebSocket connection
  socket.on("connect_error", function (error) {
    console.error("WebSocket connection error:", error);
  });
});
