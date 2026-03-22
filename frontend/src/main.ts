/**
 * Vue 应用入口文件
 * 
 * 功能说明：
 * - 创建 Vue 应用实例
 * - 注册 Pinia 状态管理
 * - 注册 Vue Router
 * - 挂载应用到 #app 元素
 */

import { createApp } from "vue";
import { createPinia } from "pinia";

import App from "./App.vue";
import router from "./router";
import "./styles.css";

// 创建 Vue 应用实例
const app = createApp(App);

// 注册 Pinia 状态管理插件
app.use(createPinia());

// 注册 Vue Router 插件
app.use(router);

// 挂载到 DOM
app.mount("#app");
