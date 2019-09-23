<template>
  <v-container>
    <v-layout wrap>
      <v-flex xs4 style="margin-top:25px">
        <v-text-field style="max-width:200px;display:inline" label="Bot IP" v-model="botIp" />
        <v-btn
          dark
          color="blue"
          @click="connect()"
          :loading="connectionInProgress"
        >Connect</v-btn>
      </v-flex>
    </v-layout>
    <v-layout wrap>
      <v-flex xs4 style="margin-top:50px; max-height:600px; min-height:600px; overflow-y:scroll">
        <v-card
          class="mx-auto"
          max-width="400"
          tile
        >
          <v-list-item two-line v-for="event in events" :key="event.timestamp" @click="selectedEvent = event">
            <v-list-item-content>
              <v-list-item-title>{{event.type}}</v-list-item-title>
              <v-list-item-subtitle>{{event.timestamp}}</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </v-card>
      </v-flex>
      <v-flex v-if="selectedEvent" xs8 style="margin-top:50px">
        {{selectedEvent}}
      </v-flex>
      <v-snackbar
        v-model="showingSnackbar"
      >
        {{ snackbarText }}
      </v-snackbar>
    </v-layout>
  </v-container>
</template>

<script>
import LightSocket from "../../public/deps/lightSocket";

export default {
  data: () => ({
    events: [{ timestamp: "10:10am", type: "TimeOfFlight" }],
    botIp: "",
    socket: null,
    headers: [
      { text: "Time Stamp", value: "timestamp" },
      { text: "Message Type", value: "type" }
    ],
    logEnable: {
      timeOfFlight: true,
      haltCommand: true,
      faceRecognition: true,
      haltCommand: true
    },
    selectedEvent: null,
    connectionSuccess: false,
    connectionInProgress: false,
    showingSnackbar: false,
    snackbarText: ""
  }),
  mounted () {
    // let addEvent = () => {
    //   this.events.unshift({ timestamp: "10:10am", type: "TimeOfFlight" });
    //   setTimeout(addEvent, 500);
    // }
    // addEvent()
  },
  methods: {
    selectEvent(event) {
      this.selectedEvent = JSON.stringify(selectedEvent);
    },
    connect() {
      if (!this.botIp) {
        this.showSnackbarMessage('Please provide an ip address for the bot');
        return;
      }
      this.connectionInProgress = true;
      this.socket = new LightSocket(this.botIp, this.openCallback, this.closeCallback, this.errorCallback);
      this.socket.Connect();
    },
    showSnackbarMessage(message) {
      this.snackbarText = message;
      this.showingSnackbar = true;
      setTimeout(() => this.snackbar = false, 2000);
    },
    closeCallback(msg) {
      this.connectionInProgress = false;
      this.showSnackbarMessage(`Connection to ip ${this.botIp} closed. Check the console for more info.`)
      console.log(msg);
    },
    errorCallback(err) {
      this.connectionInProgress = false;
      this.showSnackbarMessage(`Connection to ip ${this.botIp} failed. Check the console for more info.`);
      console.log(err);
    },
    websocketSubscribe(customEventName, eventType, callback) {
      this.socket.Subscribe(
        customEventName,
        eventType,
        null,
        null,
        null,
        null,
        null,
        callback
      );
    },
    openCallback() {
      console.log("Socket successfuly opened!");
      this.showSnackbarMessage(`Connection to ${this.botIp} established!`);
      this.connectionInProgress = false;
      this.connectionSuccess = true;

      this.websocketSubscribe("TimeOfFlight", "TimeOfFlight", this.timeOfFlight);
      this.websocketSubscribe("FaceRecognition", "FaceRecognition", this.faceRecognition);
      this.websocketSubscribe("LocomotionCommand", "LocomotionCommand", this.locomotionCommand);
      this.websocketSubscribe("HaltCommand", "HaltCommand", this.haltCommand);
    },
    websocketEvent(data) {
      try {
        console.log(data);
        this.events.unshift(data);
      } catch (e) {
        console.log(e);
      }
    },
    timeOfFlight(data) {
      try {
        if (this.logEnable.timeOfFlight) {
          console.log(data);
          this.events.unshift(data);
        }
      } catch (e) {
        console.log(e);
      }
    },
    faceRecognition(data) {
      try {
        if (this.logEnable.faceRecognition) {
          console.log(data);
          this.events.unshift(data);
        }
      } catch (e) {
        console.log(e);
      }
    },
    locomotionCommand(data) {
      //   LocomotionCommand{
      //     "EventName":"LocomotionCommand",
      //     "Message":{
      //         "ActionId":0,
      //         "AngularVelocity":0,
      //         "Created":"2018-04-02T22:59:39.3350238Z",
      //         "LinearVelocity":0.30000000000000004,
      //         "UsePid":true,
      //         "UseTrapezoidalDrive":true,
      //         "ValueIndex":0
      //     },
      //     "Type":"LocomotionCommand"
      // }
      try {
        if (this.logEnable.locomotionCommand) {
          console.log(data);
          this.events.unshift(data);
        }
      } catch (e) {
        console.log(e);
      }
    },
    haltCommand(data) {
      try {
        if (this.logEnable.haltCommand) {
          console.log(data);
        }
      } catch (e) {
        console.log(e);
      }
    },
    selectEvent(event) {}
  }
};
</script>