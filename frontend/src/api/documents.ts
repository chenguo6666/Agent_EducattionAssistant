/**
 * 文档相关 API 模块
 * 
 * 功能说明：
 * - uploadDocument: 上传学习资料（txt/md/pdf/docx），后端自动抽取文本并分块
 * - fetchSessionDocuments: 获取某个会话关联的所有文档列表
 * 
 * 支持的文件格式：.txt, .md, .pdf, .docx
 */

import { request } from "@/api/http";
import type { DocumentListResponse, DocumentSummary } from "@/types/chat";

/**
 * 上传学习资料
 * @param file - 要上传的文件对象（来自 <input type="file">）
 * @param token - JWT 认证令牌
 * @param sessionId - 可选，指定关联的会话 ID
 * @returns 上传成功后的文档摘要信息（ID、文件名、抽取状态等）
 */
export function uploadDocument(file: File, token: string, sessionId?: string) {
  // 使用 FormData 封装文件，Content-Type 由浏览器自动设置（multipart/form-data）
  const formData = new FormData();
  formData.append("file", file);
  if (sessionId) {
    formData.append("sessionId", sessionId);
  }
  return request<DocumentSummary>("/api/documents/upload", "POST", formData, token, { timeoutMs: 45000 });
}

/**
 * 获取会话关联的文档列表
 * @param sessionId - 会话 ID
 * @param token - JWT 认证令牌
 * @returns 会话关联的所有文档摘要列表
 */
export function fetchSessionDocuments(sessionId: string, token: string) {
  return request<DocumentListResponse>(`/api/documents/sessions/${sessionId}`, "GET", undefined, token);
}
