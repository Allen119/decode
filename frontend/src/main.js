import './index.css'

import { createApp } from 'vue'
import router from './router'
import App from './App.vue'
import io from 'socket.io-client'


window.frappe = {
  socketio_port: 9000, // Update this with your Frappe socket port
  realtime: {
      on: (event, callback) => {
          if (!window.socket) {
              initSocket()
          }
          window.socket.on(event, callback)
      },
      off: (event, callback) => {
          if (window.socket) {
              window.socket.off(event, callback)
          }
      }
  }
}

function initSocket() {
  const socket = io(`${window.location.hostname}:${window.frappe.socketio_port}`)
  window.socket = socket

  socket.on('connect', () => {
      console.log('Socket connected')
  })

  socket.on('disconnect', () => {
      console.log('Socket disconnected')
  })
}

import {
  Button,
  Card,
  Input,
  setConfig,
  frappeRequest,
  resourcesPlugin,
} from 'frappe-ui'

let app = createApp(App)

setConfig('resourceFetcher', frappeRequest)

app.use(router)
app.use(resourcesPlugin)

app.component('Button', Button)
app.component('Card', Card)
app.component('Input', Input)

app.mount('#app')
