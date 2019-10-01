<template>
  <div>
    <v-container v-if="!showingViewLog">
      <v-layout wrap>
        <v-flex xs4 style="margin-top:25px">
          <v-btn dark color="blue" @click="enableAllEvents()">Enable All</v-btn>
          <v-btn dark color="gray" @click="disableAllEvents()">Disable All</v-btn>
          <div v-for="event in Object.keys(allWebsocketEvents)" :key="event">
            <v-switch v-model="allWebsocketEvents[event]" :label="event"></v-switch>
          </div>
        </v-flex>
        <v-flex xs8 style="margin-top:25px">
          <v-text-field label="Bot IP" v-model="botIp" />
          <div style="margin-top:5px">
            <v-btn
              dark
              color="red"
              @click="connect()"
              v-if="!connectionSuccess"
              :loading="connectionInProgress"
            >Connect</v-btn>
            <v-btn dark color="orange" @click="disconnect()" v-if="connectionSuccess">Disconnect</v-btn>
          </div>
          <div style="margin-top:5px">
            <v-btn color="yellow" @click="saveLog()">Save Log</v-btn>
            <v-btn dark color="green" @click="clearLog()">Clear Log</v-btn>
            <v-btn dark color="blue" @click="viewLog()">View Log</v-btn>
          </div>
          <div style="margin-top:5px">
            <h1>{{eventCount}} Events Logged</h1>
          </div>
          <br />
        </v-flex>
      </v-layout>
      <v-layout wrap>
        <v-snackbar v-model="showingSnackbar">{{ snackbarText }}</v-snackbar>
      </v-layout>
    </v-container>
    <v-container v-if="showingViewLog">
      <view-log :log="events" />
    </v-container>
  </div>
</template>

<script>
// LightSocket is a websocket wrapper provided by the misty developers
import LightSocket from "../../public/deps/lightSocket";
import moment from "moment";
import uuid from "uuid/v4";
import papa from "papaparse";
import ViewLog from "@/components/ViewLog";

let events = [];
export default {
  components: {
    "view-log": ViewLog
  },
  data: () => ({
    events: [],
    showingViewLog: false,
    eventCount: 0,
    botIp: "10.10.0.7",
    socket: null,
    headers: [
      { text: "Time Stamp", value: "timestamp" },
      { text: "Event Name", value: "eventName" }
    ],
    allWebsocketEvents: {
      ActuatorPosition: false,
      AudioPlayComplete: false,
      BatteryCharge: false,
      BumpSensor: false,
      DriveEncoders: false,
      FaceRecognition: false,
      FaceTraining: false,
      HaltCommand: false,
      IMU: false,
      LocomotionCommand: false,
      SerialMessage: false,
      SkillData: false,
      TimeOfFlight: false,
      TouchSensor: false,
      // these events are in BETA
      KeyPhraseRecognized: false,
      SourceTrackDataMessage: false,
      SourceFocusConfigMessage: false,
      // these events are in ALPHA
      HazardNotification: false,
      SlamStatus: false,
      SelfState: false,
      WorldState: false
    },
    selectedEvent: null,
    connectionSuccess: false,
    connectionInProgress: false,
    showingSnackbar: false,
    snackbarText: ""
  }),
  mounted() {
    // Use this to test the logger without needing to
    // connect to Misty
    // let addEvent = () => {
    //   const mockEvent = {
    //     timestamp: this.formatDate(moment().toISOString()),
    //     eventName: "event",
    //     message: this.flattenObject({bloo: 'blah', ayy: { lmao: 'sup'}})
    //   };
    //   events.unshift(mockEvent);
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
        this.showSnackbarMessage("Please provide an ip address for the bot");
        return;
      }
      this.connectionInProgress = true;
      this.socket = new LightSocket(
        this.botIp,
        this.openCallback,
        this.closeCallback,
        this.errorCallback
      );
      this.socket.Connect();
    },
    disconnect() {
      this.socket.Disconnect();
      this.showSnackbarMessage("Disconnected from ip " + this.botIp);
      this.connectionSuccess = false;
    },
    showSnackbarMessage(message) {
      this.snackbarText = message;
      this.showingSnackbar = true;
      setTimeout(() => (this.snackbar = false), 2000);
    },
    openCallback() {
      console.log("Socket successfuly opened!");
      this.showSnackbarMessage(`Connection to ${this.botIp} established!`);
      this.connectionInProgress = false;
      this.connectionSuccess = true;

      Object.keys(this.allWebsocketEvents).forEach(event => {
        if (this.allWebsocketEvents[event]) {
          // each event name is assigned a uuid so there are no collisions
          // TODO find a better way to avoid websocket collisions. Maybe
          // we need to tear down the websocket connections on disconnect? 
          this.websocketSubscribe(event + "-" + uuid(), event, this.logEvent);
        }
      });
    },
    closeCallback(msg) {
      this.connectionInProgress = false;
      this.connectionSuccess = false;
      this.showSnackbarMessage(
        `Connection to ip ${this.botIp} closed. Check the console for more info.`
      );
      console.log(msg);
    },
    errorCallback(err) {
      this.connectionInProgress = false;
      this.connectionSuccess = false;
      this.showSnackbarMessage(
        `Connection to ip ${this.botIp} failed. Check the console for more info.`
      );
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
    formatDate(dateString) {
      return moment(dateString).format("HH:MM:SS:ss MM/DD");
    },
    logEvent(data) {
      this.eventCount++;
      const timestamp = this.formatDate(data.message.created);
      try {
        console.log(data);
        const event = {
          timestamp,
          eventName: data.eventName,
          message: this.flattenObject(data.message),
          id: uuid()
        };
        events.unshift(event);
      } catch (e) {
        const event = {
          timestamp,
          eventName: "Error",
          message: e,
          id: uuid()
        };
        events.unshift(this.flattenObject(event));
        console.log(e);
      }
    },
    saveLog() {
      let formattedEvents = events.slice(0);
      formattedEvents.forEach(e => (e.message = JSON.stringify(e.message)));
      let csv = papa.unparse(JSON.stringify(formattedEvents));
      this.saveFile(csv);
    },
    clearLog() {
      this.eventCount = 0;
      events = [];
    },
    viewLog() {
      this.showingViewLog = true;
      this.events = events;
    },
    saveFile(data) {
      let filename =
        "misty_log_" + moment().format("HH:MM:SS MM/DD/YYYY") + ".csv";
      var file = new Blob([data], { type: "text/csv" });
      if (window.navigator.msSaveOrOpenBlob)
        // IE10+
        window.navigator.msSaveOrOpenBlob(file, filename);
      else {
        // Others
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
      const flattened = {};

      Object.keys(obj).forEach(key => {
        if (typeof obj[key] === "object" && obj[key] !== null) {
          Object.assign(flattened, this.flattenObject(obj[key]));
        } else {
          flattened[key] = obj[key];
        }
      });

      return flattened;
    },
    enableAllEvents() {
      Object.keys(this.allWebsocketEvents).forEach(event => {
        this.allWebsocketEvents[event] = true;
      });
    },
    disableAllEvents() {
      Object.keys(this.allWebsocketEvents).forEach(event => {
        this.allWebsocketEvents[event] = false;
      });
    }
  }
};
</script>