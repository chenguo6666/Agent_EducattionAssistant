export type TaskStatus = "submitted" | "analyzing" | "executing" | "completed" | "failed";

export interface TaskStage {
  status: TaskStatus;
  label: string;
}

export interface QuizItem {
  question: string;
  options: string[];
  answer: string;
}

export interface ChatResult {
  summary?: string;
  quiz?: QuizItem[];
  translation?: string;
  polish?: string;
  explanation?: string;
  comparison?: string;
}

export interface ChatResponse {
  taskId: string;
  intent: string;
  status: TaskStatus;
  steps: string[];
  timeline: TaskStage[];
  result: ChatResult;
}
