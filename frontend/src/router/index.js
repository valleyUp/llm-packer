import { createRouter, createWebHistory } from 'vue-router';

// 导入视图组件
import ModelDownload from '@/views/ModelDownload.vue';
import ArchiveModel from '@/views/ArchiveModel.vue';
import TaskHistory from '@/views/TaskHistory.vue';
import About from '@/views/About.vue';

// 创建路由配置
const routes = [
  {
    path: '/',
    name: 'Home',
    component: ModelDownload,
  },
  {
    path: '/archive',
    name: 'Archive',
    component: ArchiveModel,
  },
  {
    path: '/history',
    name: 'History',
    component: TaskHistory,
  },
  {
    path: '/about',
    name: 'About',
    component: About,
  },
];

// 创建路由实例
const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router; 