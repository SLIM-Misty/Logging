<template>
  <v-app>
    <v-app-bar app>
      <v-toolbar-title class="headline text-uppercase">
        <span style="margin-right:15px">MISTY</span>
        <span class="font-weight-light">LOGGER</span>
      </v-toolbar-title>
    </v-app-bar>

    <v-content>
      <router-view />
    </v-content>
  </v-app>
</template>

<script>

import Home from '@/views/Home'
export default {
  name: 'App',
  components: {
    Home,
  },
  data: () => ({
    //
  }),
};
</script>
