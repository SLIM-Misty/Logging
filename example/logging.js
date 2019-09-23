// /deps/lightSocket.js required

// Misty's IP address
const BOT_IP = "10.10.0.7";

// Establish a websocket connection to Misty
let socket = new LightSocket(BOT_IP, openCallback);

const LOG_ENABLE = {
    TIME_OF_FLIGHT: false,
    FACE_RECOGNITION: false,
    LOCOMOTION_COMMAND: true,
    HALT_COMMAND: true
}

/* COMMANDS */
let _timeOfFlight = function (data) {
    try {
        if (LOG_ENABLE.TIME_OF_FLIGHT) {
            console.log(data);
        }
    }
    catch(e) {
        console.log(e);
    }
}

let _faceRecognition = function (data) {
    try {
        if (LOG_ENABLE.FACE_RECOGNITION) {
            console.log(data);
        }
    }
    catch(e) { 
        console.log(e);
    }
};

let _locomotionCommand = function (data) {
    try {
        if (LOG_ENABLE.LOCOMOTION_COMMAND) {
            document.getElementById('logging-pane').append(JSON.stringify(data.message));
            console.log(data);
        }
    }
    catch(e) { 
        console.log(e);
    }
};

let _haltCommand = function (data) {
    try {
        if (LOG_ENABLE.HALT_COMMAND) {
            console.log(data);
        }
    }
    catch(e) { 
        console.log(e);
    }
};

function openCallback() {
    console.log("Socket successfuly opened!");

    socket.Subscribe(
        "TimeOfFlightData", 
        "TimeOfFlight", 
        null, 
        null, null, null,
        null, 
        _timeOfFlight
    );

    socket.Subscribe(
        "FaceRecognitionData",
        "FaceRecognition",
        null, 
        null, null, null, 
        null, 
        _faceRecognition);

    socket.Subscribe(
        "LocomotionCommandData",
        "LocomotionCommand",
        null,
        null, null, null,
        null,
        _locomotionCommand);

    socket.Subscribe(
        "HaltCommandData",
        "HaltCommand", 
        null, 
        null, null, null, 
        null, 
        _haltCommand);

}

socket.Connect();