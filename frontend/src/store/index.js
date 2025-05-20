import { createStore } from 'vuex';
import modelModule from './modules/model';
import taskModule from './modules/task';
import uiModule from './modules/ui';

// 创建Vuex存储
export default createStore({
  modules: {
    model: modelModule,
    task: taskModule,
    ui: uiModule,
  },
}); 