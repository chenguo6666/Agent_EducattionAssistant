import { defineStore } from "pinia";
import type { LoginResponse, UserProfile } from "@/types/auth";

const TOKEN_KEY = "education-agent-token";
const USER_KEY = "education-agent-user";

function readToken(): string {
  return window.localStorage.getItem(TOKEN_KEY) ?? "";
}

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

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: readToken(),
    user: readUser() as UserProfile | null,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token),
    username: (state) => state.user?.username ?? "",
  },
  actions: {
    setSession(payload: LoginResponse) {
      this.token = payload.token;
      this.user = payload.user;
      window.localStorage.setItem(TOKEN_KEY, payload.token);
      window.localStorage.setItem(USER_KEY, JSON.stringify(payload.user));
    },
    setUser(user: UserProfile) {
      this.user = user;
      window.localStorage.setItem(USER_KEY, JSON.stringify(user));
    },
    clearSession() {
      this.token = "";
      this.user = null;
      window.localStorage.removeItem(TOKEN_KEY);
      window.localStorage.removeItem(USER_KEY);
    },
  },
});
