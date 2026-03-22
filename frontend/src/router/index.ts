/**
 * Vue Router 路由配置模块
 * 
 * 功能说明：
 * - 定义应用的路由规则
 * - 实现导航守卫（路由守卫）
 * 
 * 路由规则：
 * - /: 根路径重定向到 /chat
 * - /login: 登录/注册页面（无需认证）
 * - /chat: 聊天工作台页面（需要认证）
 * 
 * 导航守卫逻辑：
 * - 访问 /chat 时未登录 → 跳转到 /login
 * - 已登录访问 /login → 跳转到 /chat
 */

import { createRouter, createWebHistory } from "vue-router";
import LoginPage from "@/pages/LoginPage.vue";
import ChatPage from "@/pages/ChatPage.vue";
import { useAuthStore } from "@/stores/auth";

// 创建路由实例
const router = createRouter({
  // 使用 HTML5 History 模式（URL 不带 #）
  history: createWebHistory(),
  
  // 路由规则定义
  routes: [
    // 根路径重定向
    { path: "/", redirect: "/chat" },
    // 登录页
    { path: "/login", component: LoginPage },
    // 聊天页，需要认证
    { path: "/chat", component: ChatPage, meta: { requiresAuth: true } },
  ],
});

/**
 * 导航守卫：在路由跳转前执行
 * 
 * 判断逻辑：
 * 1. 如果目标路由需要认证（meta.requiresAuth）且用户未登录 → 跳转登录页
 * 2. 如果已登录用户访问登录页 → 跳转聊天页
 * 3. 其他情况放行
 */
router.beforeEach((to) => {
  const authStore = useAuthStore();

  // 需要认证但未登录 → 跳转登录
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return "/login";
  }

  // 已登录访问登录页 → 跳转聊天
  if (to.path === "/login" && authStore.isAuthenticated) {
    return "/chat";
  }

  // 其他情况放行
  return true;
});

export default router;
