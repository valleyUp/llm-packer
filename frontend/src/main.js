import { createApp } from 'vue';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
import App from './App.vue';
import router from './router';
import store from './store';

// 创建Vue应用
const app = createApp(App);

// 注册全局组件和插件
app.use(ElementPlus);
app.use(router);
app.use(store);

// 挂载应用
app.mount('#app'); 