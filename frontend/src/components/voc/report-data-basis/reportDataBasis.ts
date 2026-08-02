export type DataBasisProcessType = "direct" | "rule" | "llm_label" | "llm_summary";

export type DataBasisSection = {
  chapterId: string;
  title: string;
  dataItems: string[];
  sources: string[];
  processingSteps: Array<{ type: DataBasisProcessType; description: string }>;
  metricDefinitions: string[];
  supports: string;
  availabilityNote: string;
};

const AVAILABILITY_NOTE = "本章节说明系统标准口径；本次没有相应数据时，报告不会补造结论。";

const DEPARTMENT_DATA_BASIS: Record<string, DataBasisSection[]> = {
  "市场部": [
    {
      chapterId: "rhythm",
      title: "传播结果与节奏",
      dataItems: ["内容发布日期与评论日期", "每日内容数、评论数与互动量", "传播趋势与峰值日期"],
      sources: ["当前事件关联的内容库", "当前事件关联的评论库", "事件趋势聚合结果"],
      processingSteps: [
        { type: "direct", description: "按日期汇总内容数、评论数和现有互动字段。" },
        { type: "rule", description: "依据日趋势识别传播峰值与阶段变化。" },
        { type: "llm_summary", description: "只解释已计算的传播规模和节奏，不重新计算指标。" },
      ],
      metricDefinitions: ["内容数和评论数按当前事件关联记录去重统计。", "互动量沿用系统现有互动字段累计口径。"],
      supports: "支撑传播规模、峰值日期、传播阶段和节奏判断。",
      availabilityNote: AVAILABILITY_NOTE,
    },
    {
      chapterId: "topics",
      title: "话题驱动",
      dataItems: ["标题或正文中的话题", "话题关联内容数与评论数", "话题累计互动量"],
      sources: ["当前事件关联内容", "内容关联评论"],
      processingSteps: [
        { type: "rule", description: "按现有规则从内容标题或正文抽取话题。" },
        { type: "direct", description: "按话题聚合内容、评论和互动数据。" },
        { type: "llm_summary", description: "解释主要话题对传播结果的作用。" },
      ],
      metricDefinitions: ["话题热度使用关联内容的现有互动量累计。", "同一内容可关联多个真实出现的话题。"],
      supports: "支撑主要话题、话题热度及传播贡献判断。",
      availabilityNote: AVAILABILITY_NOTE,
    },
    {
      chapterId: "subjects",
      title: "传播主体",
      dataItems: ["作者与 KOL", "主体发布内容数", "主体带来的评论量与互动量"],
      sources: ["作者库", "KOL 画像", "事件内容关联结果"],
      processingSteps: [
        { type: "direct", description: "按主体聚合其关联内容、评论和互动数据。" },
        { type: "rule", description: "主体身份沿用系统已有作者与 KOL 识别结果。" },
        { type: "llm_summary", description: "解释不同传播主体的贡献差异。" },
      ],
      metricDefinitions: ["发布量按事件内关联内容统计。", "评论量与互动量按主体关联内容汇总。"],
      supports: "支撑主要传播者、主体结构和贡献差异判断。",
      availabilityNote: AVAILABILITY_NOTE,
    },
    {
      chapterId: "channels",
      title: "渠道效率",
      dataItems: ["内容所属平台", "各平台内容数与评论数", "各平台互动量及现有效率指标"],
      sources: ["事件内容的平台字段", "事件评论的平台字段"],
      processingSteps: [
        { type: "direct", description: "按平台聚合内容、评论和互动数据。" },
        { type: "rule", description: "渠道效率沿用系统已有计算口径。" },
        { type: "llm_summary", description: "解释渠道覆盖和效率差异。" },
      ],
      metricDefinitions: ["平台分布按当前事件关联内容和评论统计。", "效率指标不由 LLM 重新计算。"],
      supports: "支撑主要渠道、渠道覆盖与效率判断。",
      availabilityNote: AVAILABILITY_NOTE,
    },
  ],
  "产品部": [
    {
      chapterId: "focus",
      title: "用户关注",
      dataItems: ["产品点", "产品点提及次数与提及占比", "关联评论"],
      sources: ["当前事件关联评论", "评论中的产品点标签"],
      processingSteps: [
        { type: "llm_label", description: "从评论中识别产品点标签。" },
        { type: "direct", description: "统计各产品点的提及次数和占比。" },
        { type: "llm_summary", description: "解释用户关注结构。" },
      ],
      metricDefinitions: ["提及次数按带有对应产品点标签的评论统计。", "提及占比沿用系统现有产品点口径。"],
      supports: "支撑用户主要关注的产品维度。",
      availabilityNote: AVAILABILITY_NOTE,
    },
    {
      chapterId: "attitude",
      title: "评价态度",
      dataItems: ["产品点正向、中性与负向评论数", "各情感方向占比"],
      sources: ["评论库中的产品点标签", "评论库中的情感标签"],
      processingSteps: [
        { type: "llm_label", description: "识别评论的产品点与情感方向。" },
        { type: "direct", description: "按产品点统计正向、中性、负向数量和比例。" },
        { type: "llm_summary", description: "解释认可、争议与负面反馈结构。" },
      ],
      metricDefinitions: ["情感比例以该产品点的有效情感评论为统计基础。", "缺失情感标签的评论不补判方向。"],
      supports: "支撑各产品点的认可、争议和负面反馈判断。",
      availabilityNote: AVAILABILITY_NOTE,
    },
    {
      chapterId: "comparison",
      title: "竞品比较",
      dataItems: ["对比车系", "对比维度与比较方向", "PKO 评论次数"],
      sources: ["评论库中的 PKO 关系标签", "当前事件车型信息"],
      processingSteps: [
        { type: "llm_label", description: "识别对比对象、对比维度和比较方向。" },
        { type: "direct", description: "统计真实 PKO 评论次数与占比。" },
        { type: "llm_summary", description: "解释用户比较关系和结果结构。" },
      ],
      metricDefinitions: ["每次比较必须来自真实评论中的 PKO 标签。", "次数和占比由系统基于有效 PKO 评论统计。"],
      supports: "支撑用户在和谁比较、比较什么以及结果如何。",
      availabilityNote: AVAILABILITY_NOTE,
    },
    {
      chapterId: "evidence",
      title: "证据支撑",
      dataItems: ["真实评论文本与评论标识", "关联产品点或 PKO 标签"],
      sources: ["当前事件关联评论"],
      processingSteps: [
        { type: "rule", description: "按系统现有排序与筛选规则选择代表证据。" },
        { type: "llm_label", description: "沿用评论已有的产品点、情感和 PKO 标签。" },
        { type: "llm_summary", description: "只能引用输入中的真实评论标识解释结论。" },
      ],
      metricDefinitions: ["证据必须保留可追溯的真实评论标识。", "没有证据时不生成替代评论。"],
      supports: "支撑产品机会点、风险点、惊喜点及比较结论。",
      availabilityNote: AVAILABILITY_NOTE,
    },
  ],
  "销售部": [
    {
      chapterId: "output",
      title: "线索产出",
      dataItems: ["已打标评论", "车相关与销售意图评论", "中、强购买信号"],
      sources: ["当前事件关联评论", "评论中的销售标签"],
      processingSteps: [
        { type: "llm_label", description: "识别车相关、销售意图和购买信号。" },
        { type: "direct", description: "统计各阶段数量与转化比例。" },
        { type: "llm_summary", description: "解释线索规模与质量。" },
      ],
      metricDefinitions: ["漏斗阶段沿用系统固定销售标签口径。", "转化比例以已打标评论为统一统计基础。"],
      supports: "支撑线索规模、线索质量和漏斗结果。",
      availabilityNote: AVAILABILITY_NOTE,
    },
    {
      chapterId: "needs",
      title: "用户需求",
      dataItems: ["销售意图分布", "购买信号分布", "各类对应评论数"],
      sources: ["评论库中的销售意图标签", "评论库中的购买信号标签"],
      processingSteps: [
        { type: "llm_label", description: "识别询价、优惠、配置、购买等销售意图与信号。" },
        { type: "direct", description: "统计各类数量和占比。" },
        { type: "llm_summary", description: "解释用户需求重点。" },
      ],
      metricDefinitions: ["意图与购买信号分别按已有标签统计。", "未标注数据保留为未标注，不补造分类。"],
      supports: "支撑用户询价、优惠、配置和购买等需求重点。",
      availabilityNote: AVAILABILITY_NOTE,
    },
    {
      chapterId: "sources",
      title: "线索来源",
      dataItems: ["内容、作者与平台", "评论数与高意向评论数", "强购买信号数"],
      sources: ["事件内容", "作者信息", "内容关联评论"],
      processingSteps: [
        { type: "direct", description: "按内容和平台聚合销售标签与评论数据。" },
        { type: "rule", description: "按现有口径计算内容和平台的线索贡献。" },
        { type: "llm_summary", description: "解释主要线索来源。" },
      ],
      metricDefinitions: ["高意向线索使用中、强购买信号的现有定义。", "内容贡献只统计当前事件关联评论。"],
      supports: "支撑哪些内容、作者和渠道带来了销售线索。",
      availabilityNote: AVAILABILITY_NOTE,
    },
    {
      chapterId: "follow_up",
      title: "承接对象",
      dataItems: ["真实用户标识、昵称与平台", "购买信号与画像标签", "代表评论"],
      sources: ["评论用户库", "用户画像", "用户关联评论"],
      processingSteps: [
        { type: "rule", description: "按强、中购买信号分组并按真实用户标识去重。" },
        { type: "llm_label", description: "沿用现有画像、销售意图和购买信号标签。" },
        { type: "llm_summary", description: "解释用户梯队，不生成成交判断或营销承诺。" },
      ],
      metricDefinitions: ["同一用户在同一梯队只展示一次。", "承接对象只来自本次报告输入中的真实用户。"],
      supports: "支撑当前数据中可进一步关注的用户梯队及其公开表达。",
      availabilityNote: AVAILABILITY_NOTE,
    },
  ],
};

export function resolveDepartmentDataBasis(departmentName: string): DataBasisSection[] {
  return DEPARTMENT_DATA_BASIS[departmentName] ?? [];
}
