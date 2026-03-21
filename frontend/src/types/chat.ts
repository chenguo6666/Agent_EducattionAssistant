export type TaskStatus = "submitted" | "analyzing" | "executing" | "completed" | "failed";
export type TraceStatus = "pending" | "running" | "completed" | "failed";

export interface TaskStage {
  status: TaskStatus;
  label: string;
}

export interface AgentTraceItem {
  type: "analysis" | "tool" | "final";
  label: string;
  status: TraceStatus;
  summary?: string | null;
}

export interface ToolCallItem {
  toolName: string;
  displayName: string;
  status: TraceStatus;
  inputSummary?: string | null;
  outputSummary?: string | null;
}

export interface QuizItem {
  question: string;
  options: string[];
  answer: string;
}

export interface ChatResult {
  summary?: string;
  quiz?: QuizItem[];
  answer?: string;
}

export interface DocumentSummary {
  documentId: string;
  sessionId: string;
  fileName: string;
  fileType: string;
  fileSize: number;
  extractionStatus: string;
  snippet: string;
  createdAt: string;
}

export interface RetrievedChunk {
  chunkId: number;
  documentId: string;
  fileName: string;
  content: string;
  score: number;
}

export interface MistakeItem {
  id: number;
  sessionId: string;
  taskRecordId: number;
  question: string;
  options: string[];
  correctAnswer: string;
  userAnswer: string;
  sourceExcerpt?: string | null;
  createdAt: string;
}

export interface ExportResponse {
  fileName: string;
  content: string;
}

export interface QuizAttemptResponse {
  savedMistakes: number;
  totalQuestions: number;
  correctCount: number;
  message: string;
}

export interface MistakeListResponse {
  items: MistakeItem[];
}

export interface DocumentListResponse {
  sessionId: string;
  documents: DocumentSummary[];
}

export interface ChatResponse {
  taskId: string;
  recordId: number;
  sessionId: string;
  intent: string;
  status: TaskStatus;
  steps: string[];
  timeline: TaskStage[];
  result: ChatResult;
  agentTrace: AgentTraceItem[];
  toolCalls: ToolCallItem[];
  usedDocuments: DocumentSummary[];
  retrievedChunks: RetrievedChunk[];
}

export interface TaskRecord {
  id: number;
  message: string;
  intent: string;
  status: TaskStatus;
  steps: string[];
  timeline: TaskStage[];
  result: ChatResult;
  agentTrace: AgentTraceItem[];
  toolCalls: ToolCallItem[];
  retrievedChunks: RetrievedChunk[];
  errorMessage?: string | null;
  createdAt: string;
}

export interface ChatSessionSummary {
  sessionId: string;
  title: string;
  lastMessage: string;
  lastStatus?: TaskStatus | null;
  createdAt: string;
  updatedAt: string;
}

export interface ChatSessionListResponse {
  sessions: ChatSessionSummary[];
}

export interface ChatSessionDetailResponse {
  sessionId: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  tasks: TaskRecord[];
  documents: DocumentSummary[];
}
