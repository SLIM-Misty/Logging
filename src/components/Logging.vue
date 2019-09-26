<template>
  <v-container>
    <v-layout wrap>
      <v-flex xs4 style="margin-top:25px">
        <v-text-field style="max-width:200px;display:inline" label="Bot IP" v-model="botIp" />
        <v-btn
          dark
          color="blue"
          @click="connect()"
          v-if="!connectionSuccess"
          :loading="connectionInProgress"
        >Connect</v-btn>
        <v-btn
          dark
          color="blue"
          @click="disconnect()"
          v-if="connectionSuccess"
        >Disconnect</v-btn>
      </v-flex>
      <v-flex xs8>
        <v-btn
          dark
          color="blue"
          @click="saveLog()"
        >Save Log</v-btn>
        <v-btn
          dark
          color="blue"
          @click="events = []"
        >Clear Log</v-btn>
      </v-flex>
    </v-layout>
    <v-layout wrap>
      <v-flex xs4 style="margin-top:50px; max-height:600px; min-height:600px; overflow-y:scroll">
        <v-card
          class="mx-auto"
          max-width="400"
          tile
        >
          <v-list-item two-line v-for="event in events" :key="event.id" @click="selectedEvent = event">
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
              <v-list-item-content v-if="typeof selectedEvent.message === 'Object'">
                <v-list-item-title 
                  v-for="key in Object.keys(selectedEvent.message)" :key="key">
                  {{key}}: {{selectedEvent.message[key]}}
                </v-list-item-title>
              </v-list-item-content>
              <v-list-item-content v-else>
                <v-list-item-title>
                  {{selectedEvent.message}}
                </v-list-item-title>
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
import uuid from "uuid/v4";
import papa from "papaparse";

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
    // Use this to test the logger without needing to 
    // connect to Misty
    // let addEvent = () => {
    //   const mockEvent = {
    //     timestamp: this.formatDate(moment().toISOString()),
    //     eventName: "event", 
    //     message: this.flattenObject({bloo: 'blah', da: { fuq: 'brah'}})
    //   };
    //   this.events.unshift(mockEvent);
    //   setTimeout(addEvent, 500);
    // }
    // addEvent();
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
    disconnect() {
      this.socket.Disconnect();
      this.showSnackbarMessage('Disconnected from ip ' + this.botIp);
      this.connectionSuccess = false;
    },
    saveLog() {
      let formattedEvents = this.events.slice(0);
      formattedEvents.forEach(e => e.message = JSON.stringify(e.message));
      let csv = papa.unparse(JSON.stringify(formattedEvents));
      this.saveFile(csv);
    },
    showSnackbarMessage(message) {
      this.snackbarText = message;
      this.showingSnackbar = true;
      setTimeout(() => this.snackbar = false, 2000);
    },
    closeCallback(msg) {
      this.connectionInProgress = false;
      this.connectionSuccess = false;
      this.showSnackbarMessage(`Connection to ip ${this.botIp} closed. Check the console for more info.`)
      console.log(msg);
    },
    errorCallback(err) {
      this.connectionInProgress = false;
      this.connectionSuccess = false;
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

      // this.websocketSubscribe("TimeOfFlight", "TimeOfFlight", this.logEvent);
      this.websocketSubscribe("FaceRecognitionData", "FaceRecognition", this.logEvent);
      this.websocketSubscribe("LocomotionCommandData", "LocomotionCommand", this.logEvent);
      this.websocketSubscribe("HaltCommandData", "HaltCommand", this.logEvent);
    },
    formatDate(dateString) {
      return moment(dateString).format("HH:MM:SS:ss MM/DD");
    },
    logEvent(data) {
      const timestamp = this.formatDate(data.message.created)
      try {
        console.log(data);
        const event = { 
          timestamp,
          eventName: data.eventName,
          message: this.flattenObject(data.message),
          id: uuid()
        };
        this.events.unshift(event);
      } catch (e) {
        const event = {
          timestamp, 
          eventName: "Error",
          message: e,
          id: uuid()
        }
        this.events.unshift(this.flattenObject(event));
        console.log(e);
      }
    },
    saveFile(data) {
      let filename = "misty_log_" + moment().format("HH:MM:SS MM/DD/YYYY") + ".csv";
      var file = new Blob([data], {type: 'text/csv'});
      if (window.navigator.msSaveOrOpenBlob) // IE10+
          window.navigator.msSaveOrOpenBlob(file, filename);
      else { // Others
          var a = document.createElement("a"),
                  url = URL.createObjectURL(file);
          a.href = url;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          setTimeout(function() {
              document.body.removeChild(a);
              window.URL.revokeObjectURL(url);  
          }, 0); 
      }
    },
    flattenObject(obj) {
      const flattened = {}

      Object.keys(obj).forEach((key) => {
        if (typeof obj[key] === 'object' && obj[key] !== null) {
          Object.assign(flattened, this.flattenObject(obj[key]))
        } else {
          flattened[key] = obj[key]
        }
      })

      return flattened
    }
  }
};
</script>