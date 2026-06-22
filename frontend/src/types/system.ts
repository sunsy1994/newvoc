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
