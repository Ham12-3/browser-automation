export type TaskStatus = "pending" | "running" | "paused" | "waiting_for_human" | "completed" | "failed" | "blocked" | "stopped";

export type Task = {
  id: number;
  title: string;
  user_prompt: string;
  status: TaskStatus;
  created_at: string;
  updated_at: string;
};

