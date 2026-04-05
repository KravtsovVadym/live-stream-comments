// ---- Initialize Vue 3 app with Bootstrap and custom styles
import { createApp } from 'vue'
import App from './App.vue'
import 'bootstrap/dist/css/bootstrap.min.css'
import './assets/styles/app.scss'

// ---- Mount root component to DOM
createApp(App).mount('#app')
