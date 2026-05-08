export type EventScenario = '营销事件' | '产品舆情事件';
export type DataPriority = 'P0' | 'P1' | 'P2';

export interface EventStoryFocus {
  scenario: EventScenario;
  coreQuestion: string;
  businessOutput: string;
  analysisPath: string[];
}

export interface EventMetricSet {
  scenario: EventScenario;
  primaryMetrics: string[];
  decisionSignals: string[];
}

export interface DataReadinessGroup {
  priority: DataPriority;
  title: string;
  items: string[];
}

export interface DepartmentStorySupport {
  department: '市场部' | '产品部' | '销售部' | '售后部' | '公关部';
  stories: string[];
  requiredData: string[];
  deferred: string[];
}

const marketingTypes = new Set(['新品上市', '品牌传播', '上市', '发布会', '试驾会', '权益政策', '区域活动']);

export function classifyEventScenario(eventType: string): EventScenario {
  return marketingTypes.has(eventType) ? '营销事件' : '产品舆情事件';
}

export function getEventStoryFocus(eventType: string): EventStoryFocus {
  const scenario = classifyEventScenario(eventType);

  if (scenario === '营销事件') {
    return {
      scenario,
      coreQuestion: '这次传播有没有打到目标人群？',
      businessOutput: '沉淀可复用的内容形式、KOL/KOC组合和目标用户心智，为下一次精准投放服务。',
      analysisPath: ['传播热度与平台结构', '主命题与用户记忆点', '内容/KOL有效性', '目标心智用户匹配度'],
    };
  }

  return {
    scenario,
    coreQuestion: '这个问题是真风险，还是局部噪音？',
    businessOutput: '判断问题是否需要产品、售后或公关响应，并沉淀高置信用户原声证据。',
    analysisPath: ['负面扩散趋势', '问题集中度', '证据强度与高置信样本', '业务响应优先级'],
  };
}

export function getEventMetricSet(eventType: string): EventMetricSet {
  const scenario = classifyEventScenario(eventType);

  if (scenario === '营销事件') {
    return {
      scenario,
      primaryMetrics: ['热度', '增速', '平台结构', '来源结构', '主命题Top', '有效互动率', '目标人群匹配度', '误伤率'],
      decisionSignals: ['用户记住了什么卖点', '哪个KOL带来有效兴趣', '哪类内容值得复用', '哪类表达容易引发误解'],
    };
  }

  return {
    scenario,
    primaryMetrics: ['负面率', '质疑率', '问题集中度', '证据强度', '高置信样本数', '扩散速度', '风险等级'],
    decisionSignals: ['问题是否真实存在', '是否来自真实车主/试驾用户', '是否需要官方回应', '是否需要产品或售后动作'],
  };
}

export function getDataReadinessChecklist(): DataReadinessGroup[] {
  return [
    {
      priority: 'P0',
      title: '最小闭环数据',
      items: ['事件表', '内容表', '评论表', '账号表', '事件-内容关系', '内容-评论关系', '作者统一ID', '评论情绪标签', '评论阶段标签', '评论心智标签', '评论意向标签'],
    },
    {
      priority: 'P1',
      title: '精准营销判断数据',
      items: ['KOL/KOC识别', 'KOL受众心智分布', 'KOL受众阶段分布', '有效互动率', '目标人群匹配度', '内容误伤率', '内容价值等级', '作者证据强度', '价格感知标签'],
    },
    {
      priority: 'P2',
      title: '长期资产增强',
      items: ['跨事件KOL历史表现', '跨事件用户心智变化', 'KOL-车型卖点匹配', '竞品对比命题', '区域差异', '历史投放复盘', '投放建议自动生成'],
    },
  ];
}

export function getSupportedDepartmentStories(): DepartmentStorySupport[] {
  return [
    {
      department: '市场部',
      stories: ['传播效果总览', '平台有效性', 'KOL有效性评估'],
      requiredData: ['事件内容评论规模', '平台字段', '作者类型', '心智标签', '阶段标签', '意向标签'],
      deferred: ['投放ROI', '破圈率', 'KOL信任度指数'],
    },
    {
      department: '产品部',
      stories: ['产品正负反馈Top', '配置/功能纠结点', '质量问题预警'],
      requiredData: ['命题标签', '问题标签', '情绪标签', '证据标签', '高置信评论'],
      deferred: ['NPS估算', '具体OTA方案建议', '首批用户真实批次识别'],
    },
    {
      department: '销售部',
      stories: ['价格感知', '购买决策障碍表达'],
      requiredData: ['价格问题标签', '意向标签', '阶段标签', '竞品对比标签', '代表性评论'],
      deferred: ['真实成交', '真实到店', '真实价格接受度'],
    },
    {
      department: '售后部',
      stories: ['售后服务舆情问题Top', '质量问题售后承接信号'],
      requiredData: ['服务类问题标签', '情绪标签', '证据标签', '车主/售后阶段标签'],
      deferred: ['服务网络差异', '重复进店', '解决速度'],
    },
    {
      department: '公关部',
      stories: ['舆情态势监控', '负面话题溯源', '关键KOL风险监控'],
      requiredData: ['情绪标签', '问题标签', '内容发布时间', 'KOL风险值', '高互动内容'],
      deferred: ['谣言自动识别', '完整跨平台转发链路', 'KOL态度变化趋势'],
    },
  ];
}

export function getEventStrategySummary(eventType: string, modelName: string): string {
  const focus = getEventStoryFocus(eventType);
  if (focus.scenario === '营销事件') {
    return `${modelName} 当前应优先验证传播是否打到目标用户，并把有效内容、KOL/KOC和用户心智沉淀为下一次精准投放资产。`;
  }

  return `${modelName} 当前应优先核查问题证据强度、真实用户占比和扩散风险，再决定产品、售后或公关响应动作。`;
}
