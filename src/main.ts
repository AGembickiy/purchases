import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'

// Создаем Vue приложение
const app = createApp(App)

// Подключаем Pinia для управления состоянием
app.use(createPinia())

// Подключаем Vue Router
app.use(router)

// Монтируем приложение
app.mount('#app')
