import { request } from "@/api/http";
import type { ChatResponse } from "@/types/chat";

export function executeTask(message: string, token: string) {
  return request<ChatResponse>("/api/chat/execute", "POST", { message }, token);
}
