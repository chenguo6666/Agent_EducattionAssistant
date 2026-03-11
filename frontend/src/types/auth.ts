export interface UserProfile {
  id: number;
  username: string;
}

export interface LoginRequest {
  account: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  phone: string;
  password: string;
}

export interface MessageResponse {
  message: string;
}

export interface LoginResponse {
  token: string;
  user: UserProfile;
}
