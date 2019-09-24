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
              <v-list-item-title>{{event.eventName}}</v-list-item-title>
              <v-list-item-subtitle>{{event.timestamp}}</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </v-card>
      </v-flex>
      <v-flex v-if="selectedEvent" xs8 style="margin-top:50px">
        <!-- {{selectedEvent}} -->
        <v-list disabled>
          <v-list-item-group color="primary">
            <v-list-item>
              <v-list-item-icon>
                <v-icon>mdi-clock</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title v-text="selectedEvent.timestamp"></v-list-item-title>
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-icon>
                <v-icon>mdi-tag</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title v-text="selectedEvent.eventName"></v-list-item-title>
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-icon>
                <v-icon>mdi-message</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title v-text="JSON.stringify(selectedEvent.message)"></v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list-item-group>
        </v-list>
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
import moment from "moment";

export default {
  data: () => ({
    events: [],
    botIp: "",
    socket: null,
    headers: [
      { text: "Time Stamp", value: "timestamp" },
      { text: "Event Name", value: "eventName" }
    ],
    logEnable: {
      timeOfFlight: true,
      haltCommand: true,
      faceRecognition: true,
      locomotionCommand: true
    },
    selectedEvent: null,
    connectionSuccess: false,
    connectionInProgress: false,
    showingSnackbar: false,
    snackbarText: ""
  }),
  mounted () {
    // let addEvent = () => {
    //   this.events.unshift({ timestamp: this.formatDate(moment().toISOString()), eventName: "TimeOfFlight", message: {bloo: 'blah'} });
    //   setTimeout(addEvent, 500);
    // }
    // addEvent()
  },
  methods: {
    selectEvent(event) {
      this.selectedEvent = selectedEvent;
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

      this.websocketSubscribe("TimeOfFlight", "TimeOfFlight", this.logEvent);
      this.websocketSubscribe("FaceRecognition", "FaceRecognition", this.logEvent);
      this.websocketSubscribe("LocomotionCommand", "LocomotionCommand", this.logEvent);
      this.websocketSubscribe("HaltCommand", "HaltCommand", this.logEvent);
    },
    formatDate(dateString) {
      return moment(dateString).format("HH:MM:SS:ss MM/DD");
    },
    logEvent(data) {
      const timestamp = this.formatDate(data.message.created)
      try {
        console.log(data);
        this.events.unshift({ timestamp, eventName: data.eventName, message: data.message});
      } catch (e) {
        this.events.unshift({ timestamp, eventName: "Error", message: e });
        console.log(e);
      }
    }
  }
};
</script>