/**
 * 认证相关类型定义
 * 
 * 本模块定义了用户认证涉及的所有数据结构：
 * - 用户信息：id, username
 * - 登录请求/响应
 * - 注册请求/响应
 */

export interface UserProfile {
  /** 用户唯一标识 ID */
  id: number;
  /** 用户名 */
  username: string;
}

export interface LoginRequest {
  /** 登录账号（支持用户名或手机号） */
  account: string;
  /** 登录密码 */
  password: string;
}

export interface RegisterRequest {
  /** 用户名 */
  username: string;
  /** 手机号 */
  phone: string;
  /** 密码 */
  password: string;
}

export interface MessageResponse {
  /** 响应消息文本 */
  message: string;
}

export interface LoginResponse {
  /** JWT 认证令牌，后续请求需在 Header 中携带 */
  token: string;
  /** 当前登录用户信息 */
  user: UserProfile;
}
