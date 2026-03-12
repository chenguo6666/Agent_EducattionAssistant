import { request } from "@/api/http";
import type { DocumentListResponse, DocumentSummary } from "@/types/chat";

export function uploadDocument(file: File, token: string, sessionId?: string) {
  const formData = new FormData();
  formData.append("file", file);
  if (sessionId) {
    formData.append("sessionId", sessionId);
  }
  return request<DocumentSummary>("/api/documents/upload", "POST", formData, token);
}

export function fetchSessionDocuments(sessionId: string, token: string) {
  return request<DocumentListResponse>(`/api/documents/sessions/${sessionId}`, "GET", undefined, token);
}
