export type AiConfigPayload = {
  ai_config_id?: number;
  config_name: string;
  base_url: string;
  model_name: string;
  timeout_seconds: number;
  is_enabled: boolean;
  is_default: boolean;
  api_key_configured: boolean;
  api_key_masked: string;
};

export type PromptTemplate = {
  prompt_id?: number;
  prompt_name: string;
  prompt_scene: string;
  prompt_version: string;
  prompt_content: string;
  is_default: boolean;
  is_enabled: boolean;
  updated_time?: string;
};

export type PromptListPayload = {
  prompts: PromptTemplate[];
};

export type EmojiMapping = {
  emoji_id?: number;
  emoji_code: string;
  emoji_type: "emoji" | "image";
  emoji_value: string;
  display_name?: string | null;
  is_enabled: boolean;
  updated_time?: string;
};

export type EmojiListPayload = {
  emojis: EmojiMapping[];
};

export type AgentErrorQuestionRecord = {
  record_id: string;
  created_at: string;
  capability: string;
  question: string;
  error_reason: string;
  history_size: number;
};

export type AgentErrorQuestionListPayload = {
  records: AgentErrorQuestionRecord[];
};

export type LineageNode = {
  lineage_id?: number;
  lineage_code: string;
  lineage_name: string;
  node_kind: string;
  generation_type: string;
  business_domain: string;
  business_definition: string;
  calculation_logic: string;
  implementation_ref: string;
  prompt_scene: string;
  owner: string;
  status: string;
  is_system: boolean;
  uses_llm: boolean;
  upstream_count: number;
  downstream_count: number;
};

export type LineageSummary = {
  node_count: number;
  metric_count: number;
  rule_count: number;
  llm_label_count: number;
  ai_summary_count: number;
  incomplete_definition_count: number;
};

export type LineageRelation = {
  edge_id: number;
  upstream_code: string;
  downstream_code: string;
  relation_type: string;
  relation_description: string;
  lineage_name: string;
  node_kind: string;
  generation_type: string;
  business_domain: string;
  status: string;
  is_system: boolean;
};

export type LineageListPayload = { summary: LineageSummary; nodes: LineageNode[] };
export type LineageDetailPayload = {
  node: LineageNode;
  upstream: LineageRelation[];
  downstream: LineageRelation[];
  available_nodes: Pick<LineageNode, "lineage_code" | "lineage_name" | "node_kind" | "business_domain">[];
};
