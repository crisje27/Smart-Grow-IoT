import { createApp } from 'vue'
import App from './App.vue'
import './assets/main.css'

// Registrar Service Worker para PWA
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then(registration => {
        console.log('SW registered:', registration)
      })
      .catch(error => {
        console.log('SW registration failed:', error)
      })
  })
}

const app = createApp(App)
app.mount('#app')
