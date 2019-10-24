import Vue from 'vue'
import Router from 'vue-router'
import Logging from './views/Logging.vue'
import TakePicture from './views/TakePicture'
import TakeDepthPicture from './views/TakeDepthPicture'
import Routine from './views/Routine'

Vue.use(Router)

export default new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      name: 'Logging',
      component: Logging
    },
    {
      path: '/routine',
      name: 'Routine',
      component: Routine
    },
    {
      path: '/takepicture',
      name: 'Take Picture',
      component: TakePicture
    },  
    {
      path: '/takedepthpicture',
      name: 'Take Depth Picture',
      component: TakeDepthPicture
    }
  ]
})
