<<<<<<< HEAD
﻿export type TaskStatus = "submitted" | "analyzing" | "executing" | "completed" | "failed";
=======
/**
 * 聊天与任务相关类型定义
 * 
 * 本模块定义了教育助手核心功能的所有数据结构：
 * - 任务状态与轨迹
 * - 聊天消息与结果
 * - 文档与检索
 * - 错题与导出
 */

/** 任务执行状态枚举 */
export type TaskStatus = "submitted" | "analyzing" | "executing" | "completed" | "failed";

/** Agent 轨迹项状态枚举 */
export type TraceStatus = "pending" | "running" | "completed" | "failed";
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)

/** 任务阶段（用于时间线展示） */
export interface TaskStage {
  /** 阶段状态 */
  status: TaskStatus;
  /** 阶段标签文本 */
  label: string;
}

<<<<<<< HEAD
=======
/** Agent 执行轨迹项
 * 
 * 记录 Agent 执行过程中的每个步骤：
 * - analysis: 分析任务意图
 * - tool: 调用工具
 * - final: 返回最终结果
 */
export interface AgentTraceItem {
  /** 轨迹类型 */
  type: "analysis" | "tool" | "final";
  /** 步骤名称 */
  label: string;
  /** 执行状态 */
  status: TraceStatus;
  /** 步骤摘要/结果（可选） */
  summary?: string | null;
}

/** 工具调用记录项 */
export interface ToolCallItem {
  /** 工具函数名称（英文） */
  toolName: string;
  /** 工具显示名称（中文） */
  displayName: string;
  /** 调用状态 */
  status: TraceStatus;
  /** 输入参数摘要 */
  inputSummary?: string | null;
  /** 输出结果摘要 */
  outputSummary?: string | null;
}

/** 题目项（选择题） */
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
export interface QuizItem {
  /** 题目文本 */
  question: string;
  /** 选项数组 */
  options: string[];
  /** 正确答案（字母 A/B/C/D） */
  answer: string;
}

/** 聊天结果内容
 * 
 * 根据任务类型不同，结果可能包含：
 * - summary: 摘要文本
 * - quiz: 生成的选择题数组
 * - answer: 问答回答
 */
export interface ChatResult {
  /** 摘要内容（摘要任务/综合任务） */
  summary?: string;
  /** 生成的练习题（出题任务/综合任务） */
  quiz?: QuizItem[];
<<<<<<< HEAD
  translation?: string;
  polish?: string;
  explanation?: string;
  comparison?: string;
=======
  /** 问答回答（资料追问任务） */
  answer?: string;
}

/** 文档摘要信息
 * 
 * 上传文档后返回的文档元数据
 */
export interface DocumentSummary {
  /** 文档唯一标识 */
  documentId: string;
  /** 所属会话 ID */
  sessionId: string;
  /** 文件名 */
  fileName: string;
  /** 文件类型（如 pdf, docx, txt） */
  fileType: string;
  /** 文件大小（字节） */
  fileSize: number;
  /** 文本抽取状态 */
  extractionStatus: string;
  /** 文本开头片段（预览用） */
  snippet: string;
  /** 创建时间 ISO 字符串 */
  createdAt: string;
}

/** 检索到的文档片段
 * 
 * RAG 检索返回的相关内容块
 */
export interface RetrievedChunk {
  /** 片段 ID */
  chunkId: number;
  /** 所属文档 ID */
  documentId: string;
  /** 来源文件名 */
  fileName: string;
  /** 片段内容 */
  content: string;
  /** 相似度分数（0-1，越高越相关） */
  score: number;
}

/** 错题记录项 */
export interface MistakeItem {
  /** 错题记录 ID */
  id: number;
  /** 所属会话 ID */
  sessionId: string;
  /** 关联的任务记录 ID */
  taskRecordId: number;
  /** 题目文本 */
  question: string;
  /** 选项数组 */
  options: string[];
  /** 正确答案 */
  correctAnswer: string;
  /** 用户提交的答案 */
  userAnswer: string;
  /** 来源资料片段（可选） */
  sourceExcerpt?: string | null;
  /** 记录时间 */
  createdAt: string;
}

/** 导出响应内容 */
export interface ExportResponse {
  /** 导出文件名 */
  fileName: string;
  /** Markdown 格式的内容 */
  content: string;
}

/** 答题提交响应 */
export interface QuizAttemptResponse {
  /** 答错的题目数量（已保存到错题本） */
  savedMistakes: number;
  /** 总题目数 */
  totalQuestions: number;
  /** 答对的题目数 */
  correctCount: number;
  /** 反馈消息 */
  message: string;
}

/** 错题列表响应 */
export interface MistakeListResponse {
  /** 错题数组 */
  items: MistakeItem[];
}

/** 文档列表响应 */
export interface DocumentListResponse {
  /** 会话 ID */
  sessionId: string;
  /** 文档数组 */
  documents: DocumentSummary[];
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
}

/** 执行任务 API 响应
 * 
 * 这是 executeTask 接口返回的完整数据结构
 */
export interface ChatResponse {
  /** 任务 ID（用于追踪） */
  taskId: string;
<<<<<<< HEAD
=======
  /** 任务记录 ID（持久化 ID） */
  recordId: number;
  /** 所属会话 ID */
  sessionId: string;
  /** 识别的任务意图 */
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
  intent: string;
  /** 当前执行状态 */
  status: TaskStatus;
  /** 执行步骤描述数组 */
  steps: string[];
  /** 任务时间线（用于 UI 展示进度） */
  timeline: TaskStage[];
  /** 任务结果内容 */
  result: ChatResult;
<<<<<<< HEAD
=======
  /** Agent 执行轨迹 */
  agentTrace: AgentTraceItem[];
  /** 工具调用详情 */
  toolCalls: ToolCallItem[];
  /** 任务使用的文档列表 */
  usedDocuments: DocumentSummary[];
  /** RAG 检索到的相关片段 */
  retrievedChunks: RetrievedChunk[];
}

/** 任务记录（从历史加载）
 * 
 * 与 ChatResponse 类似，但不包含即时执行状态
 */
export interface TaskRecord {
  /** 任务记录 ID */
  id: number;
  /** 用户提交的消息 */
  message: string;
  /** 任务意图 */
  intent: string;
  /** 最终状态 */
  status: TaskStatus;
  /** 执行步骤 */
  steps: string[];
  /** 时间线 */
  timeline: TaskStage[];
  /** 结果内容 */
  result: ChatResult;
  /** 执行轨迹 */
  agentTrace: AgentTraceItem[];
  /** 工具调用 */
  toolCalls: ToolCallItem[];
  /** 检索片段 */
  retrievedChunks: RetrievedChunk[];
  /** 错误信息（如果失败） */
  errorMessage?: string | null;
  /** 创建时间 */
  createdAt: string;
}

/** 会话摘要信息（列表展示用） */
export interface ChatSessionSummary {
  /** 会话 ID */
  sessionId: string;
  /** 会话标题（自动生成或用户设置） */
  title: string;
  /** 最近一条消息内容 */
  lastMessage: string;
  /** 最近任务状态 */
  lastStatus?: TaskStatus | null;
  /** 创建时间 */
  createdAt: string;
  /** 更新时间 */
  updatedAt: string;
}

/** 会话列表响应 */
export interface ChatSessionListResponse {
  /** 会话数组 */
  sessions: ChatSessionSummary[];
}

/** 会话详情响应
 * 
 * 包含会话的所有任务记录和关联文档
 */
export interface ChatSessionDetailResponse {
  /** 会话 ID */
  sessionId: string;
  /** 会话标题 */
  title: string;
  /** 创建时间 */
  createdAt: string;
  /** 更新时间 */
  updatedAt: string;
  /** 任务记录数组（按时间排序） */
  tasks: TaskRecord[];
  /** 关联的文档数组 */
  documents: DocumentSummary[];
>>>>>>> 11d2122 (feat(frontend): 添加前端代码中文注释)
}
