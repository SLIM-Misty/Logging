<template>
  <v-app>
    <v-app-bar app>
      <v-toolbar-title class="headline text-uppercase">
        <span style="margin-right:15px">CS481 Misty Project</span>
        <router-link to="/" style="margin-left:15px">Logging</router-link>
        <router-link to="routine" style="margin-left:15px">Routine</router-link>
        <router-link to="takepicture" style="margin-left:15px">Pictures</router-link>
      </v-toolbar-title>
    </v-app-bar>

    <v-content>
      <router-view />
    </v-content>
  </v-app>
</template>

<script>

export default {
  name: 'App',
  data: () => ({
    //
  }),
};
</script>
