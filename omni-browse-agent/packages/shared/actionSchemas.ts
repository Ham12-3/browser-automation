export type RiskLevel = "low" | "medium" | "high" | "blocked";

export type AgentAction = {
  type: "navigate" | "click" | "type" | "press" | "scroll" | "wait" | "extract" | "screenshot" | "ask_user" | "pause" | "stop" | "resume";
  target?: { kind: string; value: string };
  payload?: Record<string, unknown>;
  reason: string;
  risk_level: RiskLevel;
};

