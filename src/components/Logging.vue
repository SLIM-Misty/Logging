<template>
  <v-container>
    <v-layout wrap>
      <v-flex xs4 style="margin-top:50px">
        <v-text-field style="max-width:200px;display:inline" label="Bot IP" v-model="botIp" />
        <v-btn dark color="blue" @click="connect()">Connect</v-btn>
        <v-data-table
          style="margin-top:20px"
          :headers="headers"
          :items="events"
          class="elevation-1"
        ></v-data-table>
      </v-flex>
      <v-flex v-if="selectedEvent" xs12 style="margin-top:50px">
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import LightSocket from "../../deps/lightSocket";

export default {
  data: () => ({
    events: [
      {timestamp: 'asdf', type: 'TimeOfFlight'}
    ],
    botIp: "",
    socket: null,
    headers: [
      { text: 'Time Stamp', value: 'timestamp' },
      { text: 'Message Type', value: 'type' },
    ],
    logEnable: {
      timeOfFlight: true,
      haltCommand: true,
      faceRecognition: true,
      haltCommand: true
    },
    selectedEvent: {}
  }),
  methods: {
    connect() {
      if (!this.botIp) {
        return;
      }
      this.socket = new LightSocket(this.botIp, this.openCallback);
      this.socket.Connect();
    },
    openCallback() {
      console.log("Socket successfuly opened!");

      socket.Subscribe(
        "TimeOfFlightData", 
        "TimeOfFlight", 
        null, 
        null, null, null,
        null, 
        this.timeOfFlight
      );

      socket.Subscribe(
        "FaceRecognitionData",
        "FaceRecognition",
        null, 
        null, null, null, 
        null, 
        this.faceRecognition
      );

      socket.Subscribe(
        "LocomotionCommandData",
        "LocomotionCommand",
        null,
        null, null, null,
        null,
        this.locomotionCommand
      );

      socket.Subscribe(
        "HaltCommandData",
        "HaltCommand", 
        null, 
        null, null, null, 
        null, 
        this.haltCommand
      );
    },
    websocketEvent (data) {
      try {
        console.log(data);
        this.events.push(data);
      }
      catch(e) {
        console.log(e);
      }
    },
    timeOfFlight (data) {
      try {
        if (this.logEnable.timeOfFlight) {
            console.log(data);
            this.events.push(data);
        }
      }
      catch(e) {
        console.log(e);
      }
    },
    faceRecognition (data) {
      try {
        if (this.logEnable.faceRecognition) {
            console.log(data);
            this.events.push(data);
        }
      }
      catch(e) { 
        console.log(e);
      }
    },
    locomotionCommand (data) {
      try {
        if (this.logEnable.locomotionCommand) {
            console.log(data);
            this.events.push(data);
        }
      }
      catch(e) { 
          console.log(e);
      }
    },
    haltCommand (data) {
      try {
          if (this.logEnable.haltCommand) {
              console.log(data);
          }
      }
      catch(e) { 
          console.log(e);
      }
    },
    selectEvent (event) {

    }
  }
}
</script>