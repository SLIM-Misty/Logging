// /deps/lightSocket.js required

// Misty's IP address
const BOT_IP = "10.10.0.7";

// Establish a websocket connection to Misty
let socket = new LightSocket(BOT_IP, openCallback);

/* COMMANDS */

let _centerTimeOfFlight = function (data) {
    try {
        let distance = data.message.distanceInMeters;
        console.log(data);
        // Write an if statement to check 
        // if the distance is smaller than 0.2 meters.
        if (distance < 0.2) {
            // If the instance is less than 0.2 meters, send
            // a request to endpoint for the Stop command.  
            axios.post("http://" + BOT_IP + "/api/drive/stop")
                .then(function (response) {
                    // Print the results
                    console.log(`Stop was a ${response.data.status}`);
                })
                .catch(function (error) {
                    // Print any errors
                    console.log(`There was an error with the request ${error}`);
                });
            }
    }
    catch(e) { 
        console.log(e);
    }
}

let _locomotionCommand = function (data) {
    try {
        console.log(data);
        if (data.message.linearVelocity === 0) {
            // Print a message to the console to aid in debugging
            console.log("LocomotionCommand received linear velocity as", data.message.linearVelocity);
            // Unsubscribe from the CenterTimeOfFlight 
            // and LocomotionCommand events
            socket.Unsubscribe("CenterTimeOfFlight");
            socket.Unsubscribe("LocomotionCommand");                
        }
    }
    catch(e) { 
        console.log(e);
    }
};

// Define the function passed as the callback 
// to the new instance of LightSocket. This is 
// the code that executes when socket opens a 
// connection to your robot.
function openCallback() {

    // Print a message when the connection is opened.
    console.log("socket opened");

    // Subscribe to an event called CenterTimeOfFlight
    // that returns TimeOfFlight data. Pass arguments 
    // to make sure this event returns data for the 
    // front center time-of-flight sensor every 100 
    // milliseconds. Pass the callback function 
    // _centerTimeOfFlight() as the final argument.
    socket.Subscribe(
        "CenterTimeOfFlight", 
        "TimeOfFlight", 
        100, 
        "SensorPosition", "==", "Center", 
        null, 
        _centerTimeOfFlight
    );


    socket.Subscribe("LocomotionCommand", "LocomotionCommand", null, null, null, null, null, _locomotionCommand);

    let driveTimeData = {
        LinearVelocity: 100,
        AngularVelocity: 0,
        TimeMS: 2000
    };

    axios.post("http://" + BOT_IP + "/api/drive/time", driveTimeData)
        // Use .then() to handle a successful response.
        .then(function (response) {
            // Print the results
            console.log(`DriveTime was a ${response.data.status}`);
        })
        // Use .catch() to handle errors
        .catch(function (error) {
            // Print any errors
            console.log(`There was an error with the request ${error}`);
        });
}

socket.Connect();