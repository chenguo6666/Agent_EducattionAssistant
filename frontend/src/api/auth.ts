/**
 * 认证相关 API 模块
 * 
 * 功能说明：
 * - login: 用户登录，返回 JWT token 和用户信息
 * - register: 用户注册
 * - fetchMe: 获取当前登录用户信息
 * 
 * 这些 API 都需要与后端 /api/auth/* 端点交互
 */

import { request } from "@/api/http";
import type { LoginRequest, LoginResponse, MessageResponse, RegisterRequest, UserProfile } from "@/types/auth";

/**
 * 用户登录
 * @param payload - 登录请求体，包含账号(account)和密码(password)
 * @returns 包含 JWT token 和用户信息的响应
 */
export function login(payload: LoginRequest) {
  return request<LoginResponse>("/api/auth/login", "POST", payload);
}

/**
 * 用户注册
 * @param payload - 注册请求体，包含用户名(username)、手机号(phone)和密码(password)
 * @returns 注册成功消息
 */
export function register(payload: RegisterRequest) {
  return request<MessageResponse>("/api/auth/register", "POST", payload);
}

/**
 * 获取当前登录用户信息
 * @param token - JWT 认证令牌
 * @returns 当前用户信息（id 和 username）
 */
export function fetchMe(token: string) {
  return request<UserProfile>("/api/auth/me", "GET", undefined, token);
}
