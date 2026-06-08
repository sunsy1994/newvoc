export type EtlFlowNode = {
  id: string;
  order: number;
  title: string;
  desc: string;
  function_name: string;
  input_tables: string[];
  output_tables: string[];
  rules: string[];
  metrics: Record<string, number>;
};

export type EtlFlowPayload = {
  nodes: EtlFlowNode[];
};
