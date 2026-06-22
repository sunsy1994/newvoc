export type AiProfileFlowNodeStatus = "ready" | "waiting" | "blocked";

export type AiProfileFlowNode = {
  id: string;
  order: number;
  title: string;
  desc: string;
  function_name: string;
  input_tables: string[];
  output_tables: string[];
  rules: string[];
  metrics: Record<string, number>;
  status: AiProfileFlowNodeStatus;
};

export type AiProfileFlowPayload = {
  nodes: AiProfileFlowNode[];
  summary: Record<string, number>;
};
