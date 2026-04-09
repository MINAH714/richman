import { createApp } from 'vue'
import App from './App.vue'

// 1. App.vue를 가져와서 Vue 앱 인스턴스를 만듭니다.
const app = createApp(App)

// 2. index.html에 있는 <div id="app"> 태그에 이 앱을 끼워 넣습니다.
app.mount('#app')