export type ScriptBackup = {
  name: string;
  path: string;
  created_at: string;
  size: number;
};

export type EtlScriptPayload = {
  path: string;
  content: string;
  updated_at: string;
  size: number;
  backups: ScriptBackup[];
};
