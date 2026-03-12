import { request } from "@/api/http";
import type {
  ChatResponse,
  ChatSessionDetailResponse,
  ChatSessionListResponse,
  ExportResponse,
  MistakeListResponse,
  QuizAttemptResponse,
} from "@/types/chat";

export function executeTask(message: string, token: string, sessionId?: string) {
  return request<ChatResponse>("/api/chat/execute", "POST", { message, sessionId }, token);
}

export function fetchSessions(token: string) {
  return request<ChatSessionListResponse>("/api/chat/sessions", "GET", undefined, token);
}

export function fetchSessionDetail(sessionId: string, token: string) {
  return request<ChatSessionDetailResponse>(`/api/chat/sessions/${sessionId}`, "GET", undefined, token);
}

export function exportTaskResult(recordId: number, token: string) {
  return request<ExportResponse>(`/api/chat/records/${recordId}/export`, "GET", undefined, token);
}

export function submitQuizAttempt(
  recordId: number,
  answers: Array<{ questionIndex: number; userAnswer: string }>,
  token: string,
) {
  return request<QuizAttemptResponse>(`/api/chat/records/${recordId}/quiz-attempt`, "POST", { answers }, token);
}

export function fetchMistakes(token: string) {
  return request<MistakeListResponse>("/api/chat/mistakes", "GET", undefined, token);
}
