import { request } from "@/api/http";
import type { LoginRequest, LoginResponse, MessageResponse, RegisterRequest, UserProfile } from "@/types/auth";

export function login(payload: LoginRequest) {
  return request<LoginResponse>("/api/auth/login", "POST", payload);
}

export function register(payload: RegisterRequest) {
  return request<MessageResponse>("/api/auth/register", "POST", payload);
}

export function fetchMe(token: string) {
  return request<UserProfile>("/api/auth/me", "GET", undefined, token);
}
