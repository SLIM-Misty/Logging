<template>
  <div>
    <v-layout wrap>
      <v-flex xs4 style="margin-top:50px; max-height:600px; min-height:600px; overflow-y:scroll">
        <v-card class="mx-auto" max-width="400" tile>
          <v-list-item two-line v-for="event in log" :key="event.id" @click="selectedEvent = event">
            <v-list-item-content>
              <v-list-item-title>{{event.eventName}}</v-list-item-title>
              <v-list-item-subtitle>{{event.timestamp}}</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </v-card>
      </v-flex>
      <v-flex v-if="selectedEvent" xs8 style="margin-top:50px">
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
                  v-for="key in Object.keys(selectedEvent.message)"
                  :key="key"
                >{{key}}: {{selectedEvent.message[key]}}</v-list-item-title>
              </v-list-item-content>
              <v-list-item-content v-else>
                <v-list-item-title>{{selectedEvent.message}}</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list-item-group>
        </v-list>
      </v-flex>
    </v-layout>
  </div>
</template>

<script>
export default {
  data() {
    return {
      selectedEvent: {}
    };
  },
  mounted() {
    //load the log from somewhere
  },
  props: {
    log: Array
  }
};
</script>