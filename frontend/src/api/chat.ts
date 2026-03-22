<<<<<<< HEAD
﻿import { request } from "@/api/http";
import type { ChatResponse } from "@/types/chat";

export function executeTask(message: string, token: string) {
  return request<ChatResponse>("/api/chat/execute", "POST", { message }, token);
=======
/**
 * 聊天相关 API 模块
 * 
 * 功能说明：
 * - executeTask: 发送用户消息，执行 AI 教育任务（总结、出题、问答等）
 * - fetchSessions: 获取用户的所有历史会话列表
 * - fetchSessionDetail: 获取某个会话的详细信息（包含所有任务记录）
 * - exportTaskResult: 导出任务结果为 Markdown 文件
 * - submitQuizAttempt: 提交选择题答案，获取答题反馈并记录错题
 * - fetchMistakes: 获取用户的错题本列表
 */

import { request } from "@/api/http";
import type {
  ChatResponse,
  ChatSessionDetailResponse,
  ChatSessionListResponse,
  ExportResponse,
  MistakeListResponse,
  QuizAttemptResponse,
} from "@/types/chat";

/**
 * 执行教育任务
 * @param message - 用户输入的消息/任务描述
 * @param token - JWT 认证令牌
 * @param sessionId - 可选，指定会话 ID，不提供则创建新会话
 * @returns 任务执行响应，包含状态、结果、轨迹等信息
 * 
 * 后端会根据消息内容识别任务意图（摘要/出题/问答等）并执行相应逻辑
 */
export function executeTask(message: string, token: string, sessionId?: string) {
  return request<ChatResponse>("/api/chat/execute", "POST", { message, sessionId }, token, { timeoutMs: 45000 });
}

/**
 * 获取会话列表
 * @param token - JWT 认证令牌
 * @returns 用户的所有会话摘要列表（标题、最近消息、时间等）
 */
export function fetchSessions(token: string) {
  return request<ChatSessionListResponse>("/api/chat/sessions", "GET", undefined, token);
}

/**
 * 获取会话详情
 * @param sessionId - 会话 ID
 * @param token - JWT 认证令牌
 * @returns 会话详细信息，包含所有任务记录和关联的文档
 */
export function fetchSessionDetail(sessionId: string, token: string) {
  return request<ChatSessionDetailResponse>(`/api/chat/sessions/${sessionId}`, "GET", undefined, token);
}

/**
 * 导出任务结果
 * @param recordId - 任务记录 ID
 * @param token - JWT 认证令牌
 * @returns 导出文件信息（文件名和 Markdown 内容）
 */
export function exportTaskResult(recordId: number, token: string) {
  return request<ExportResponse>(`/api/chat/records/${recordId}/export`, "GET", undefined, token);
}

/**
 * 提交选择题答案
 * @param recordId - 任务记录 ID（包含生成的题目）
 * @param answers - 用户答案数组，每项包含题目索引和用户选择的答案
 * @param token - JWT 认证令牌
 * @returns 答题反馈：正确率、错题数量等
 */
export function submitQuizAttempt(
  recordId: number,
  answers: Array<{ questionIndex: number; userAnswer: string }>,
  token: string,
) {
  return request<QuizAttemptResponse>(`/api/chat/records/${recordId}/quiz-attempt`, "POST", { answers }, token, { timeoutMs: 20000 });
}

/**
 * 获取错题本
 * @param token - JWT 认证令牌
 * @returns 用户的所有错题列表
 */
export function fetchMistakes(token: string) {
  return request<MistakeListResponse>("/api/chat/mistakes", "GET", undefined, token);
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
}
