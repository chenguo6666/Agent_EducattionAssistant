/**
 * 认证状态管理模块
 * 
 * 使用 Pinia 管理用户登录状态：
 * - token: JWT 认证令牌
 * - user: 当前登录用户信息
 * 
 * 关键功能：
 * - 从 localStorage 恢复登录状态（页面刷新后保持登录）
 * - 登录成功后保存 token 和 user 到 localStorage
 * - 退出登录时清除所有认证信息
 */

import { defineStore } from "pinia";
import type { LoginResponse, UserProfile } from "@/types/auth";

// localStorage 存储键名
const TOKEN_KEY = "education-agent-token";
const USER_KEY = "education-agent-user";

/**
 * 从 localStorage 读取存储的 JWT token
 * @returns 存储的 token 字符串，无则返回空字符串
 */
function readToken(): string {
  return window.localStorage.getItem(TOKEN_KEY) ?? "";
}

/**
 * 从 localStorage 读取存储的用户信息
 * @returns 用户对象，解析失败或无数据返回 null
 */
function readUser(): UserProfile | null {
  const raw = window.localStorage.getItem(USER_KEY);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw) as UserProfile;
  } catch {
    return null;
  }
}

/**
 * 认证状态 Store
 * 
 * 管理用户登录状态，支持页面刷新后自动恢复登录态
 */
export const useAuthStore = defineStore("auth", {
  // 响应式状态：从 localStorage 初始化
  state: () => ({
    token: readToken(),
    user: readUser() as UserProfile | null,
  }),
  
  // 计算属性
  getters: {
    /** 是否已认证（token 存在） */
    isAuthenticated: (state) => Boolean(state.token),
    /** 用户名（快捷访问） */
    username: (state) => state.user?.username ?? "",
  },
  
  // 修改状态的方法
  actions: {
    /**
     * 设置登录会话（登录成功时调用）
     * @param payload - 包含 token 和 user 的登录响应
     */
    setSession(payload: LoginResponse) {
      this.token = payload.token;
      this.user = payload.user;
      // 同步写入 localStorage 持久化
      window.localStorage.setItem(TOKEN_KEY, payload.token);
      window.localStorage.setItem(USER_KEY, JSON.stringify(payload.user));
    },
    
    /**
     * 更新用户信息（获取最新用户资料时调用）
     * @param user - 用户信息对象
     */
    setUser(user: UserProfile) {
      this.user = user;
      window.localStorage.setItem(USER_KEY, JSON.stringify(user));
    },
    
    /**
     * 清除登录会话（退出登录时调用）
     */
    clearSession() {
      this.token = "";
      this.user = null;
      window.localStorage.removeItem(TOKEN_KEY);
      window.localStorage.removeItem(USER_KEY);
    },
  },
});
