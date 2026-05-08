// 图表数据类型定义
export interface TrendData {
  date: string;
  value: number;
}

export interface ChannelData {
  channel: string;
  value: number;
}

export interface SentimentData {
  label: string;
  value: number;
  percentage: number;
  color: string;
}

export interface TableData {
  name: string;
  value: number | string;
  change?: number;
}

export interface PieData {
  name: string;
  value: number;
  color: string;
}

export interface RadarData {
  category: string;
  value: number;
}

// 部门图表配置
export interface DepartmentCharts {
  department: string;
  title: string;
  cards: ChartCard[];
}

export interface ChartCard {
  id: string;
  title: string;
  type: 'trend' | 'bar' | 'sentiment' | 'table' | 'pie' | 'radar';
  size?: 'full' | 'half';
  data: any;
  subtitle?: string;
}

// 市场部图表数据
const marketTrendData: TrendData[] = [
  { date: '1月1日', value: 12500 },
  { date: '1月4日', value: 15200 },
  { date: '1月7日', value: 18200 },
  { date: '1月10日', value: 16800 },
  { date: '1月13日', value: 22100 },
  { date: '1月16日', value: 19800 },
  { date: '1月19日', value: 25600 },
];

const marketChannelData: ChannelData[] = [
  { channel: '抖音', value: 24600 },
  { channel: '微博', value: 18500 },
  { channel: '汽车之家', value: 15200 },
  { channel: '小红书', value: 12800 },
  { channel: 'B站', value: 9800 },
];

const marketSentimentData: SentimentData[] = [
  { label: '正面评价', value: 28560, percentage: 68, color: 'bg-blue-500' },
  { label: '中性评价', value: 9850, percentage: 23, color: 'bg-gray-400' },
  { label: '负面评价', value: 3680, percentage: 9, color: 'bg-indigo-600' },
];

const marketKOLData: TableData[] = [
  { name: 'XX车评', value: '正面', change: 76 },
  { name: 'XX测评', value: '正面', change: 68 },
  { name: 'XX说车', value: '中性', change: 45 },
  { name: 'XX汽车', value: '负面', change: -12 },
  { name: 'XX评测', value: '正面', change: 82 },
];

// 产品部图表数据
const productTrendData: TrendData[] = [
  { date: '1月1日', value: 68 },
  { date: '1月4日', value: 72 },
  { date: '1月7日', value: 65 },
  { date: '1月10日', value: 78 },
  { date: '1月13日', value: 82 },
  { date: '1月16日', value: 75 },
  { date: '1月19日', value: 85 },
];

const productFeatureData: ChannelData[] = [
  { channel: '智能座舱', value: 52 },
  { channel: '外观设计', value: 48 },
  { channel: '驾驶体验', value: 35 },
  { channel: '内饰质感', value: 28 },
  { channel: '座椅舒适', value: 18 },
];

const productQualityData: TableData[] = [
  { name: '车机卡顿', value: 32, change: 0 },
  { name: '风噪问题', value: 28, change: 0 },
  { name: '续航达成', value: 18, change: 0 },
  { name: '异响', value: 22, change: 0 },
  { name: '黑屏重启', value: 15, change: 0 },
];

const productConfigData: ChannelData[] = [
  { channel: '大轮毂', value: 42 },
  { channel: '高阶智驾', value: 35 },
  { channel: '真皮座椅', value: 28 },
  { channel: 'HUD抬显', value: 22 },
  { channel: '音响系统', value: 18 },
];

// 销售部图表数据
const salesTrendData: TrendData[] = [
  { date: '1月1日', value: 38 },
  { date: '1月4日', value: 42 },
  { date: '1月7日', value: 35 },
  { date: '1月10日', value: 45 },
  { date: '1月13日', value: 48 },
  { date: '1月16日', value: 40 },
  { date: '1月19日', value: 52 },
];

const salesBarrierData: PieData[] = [
  { name: '等真实口碑', value: 42, color: '#3b82f6' },
  { name: '等降价促销', value: 28, color: '#4f46e5' },
  { name: '配置纠结', value: 18, color: '#1d4ed8' },
  { name: '其他', value: 12, color: '#64748b' },
];

const salesServiceData: RadarData[] = [
  { category: '专业度', value: 85 },
  { category: '响应速度', value: 72 },
  { category: '价格透明', value: 68 },
  { category: '不逼单', value: 90 },
  { category: '试驾便利', value: 78 },
];

const salesCompetitorData: TableData[] = [
  { name: '本品牌', value: '认可高', change: 22 },
  { name: '竞品A', value: '价格低', change: -15 },
  { name: '竞品B', value: '配置高', change: -8 },
  { name: '竞品C', value: '服务好', change: -5 },
];

// 售后部图表数据
const serviceTrendData: TrendData[] = [
  { date: '1月1日', value: 76 },
  { date: '1月4日', value: 78 },
  { date: '1月7日', value: 72 },
  { date: '1月10日', value: 80 },
  { date: '1月13日', value: 82 },
  { date: '1月16日', value: 75 },
  { date: '1月19日', value: 85 },
];

const serviceIssueData: ChannelData[] = [
  { channel: '车机卡顿', value: 48 },
  { channel: '异响问题', value: 22 },
  { channel: '续航不满', value: 18 },
  { channel: '充电问题', value: 15 },
  { channel: '其他', value: 12 },
];

const serviceStoreData: ChannelData[] = [
  { channel: '等待时间', value: 42 },
  { channel: '备件周期', value: 26 },
  { channel: '服务态度', value: 18 },
  { channel: '费用透明', value: 15 },
  { channel: '重复进店', value: 12 },
];

const serviceResponseData: TrendData[] = [
  { date: '1月1日', value: 45 },
  { date: '1月4日', value: 38 },
  { date: '1月7日', value: 52 },
  { date: '1月10日', value: 35 },
  { date: '1月13日', value: 42 },
  { date: '1月16日', value: 48 },
  { date: '1月19日', value: 30 },
];

// 公关部图表数据
const prTrendData: TrendData[] = [
  { date: '1月1日', value: 8.2 },
  { date: '1月4日', value: 7.8 },
  { date: '1月7日', value: 9.1 },
  { date: '1月10日', value: 8.5 },
  { date: '1月13日', value: 7.5 },
  { date: '1月16日', value: 8.8 },
  { date: '1月19日', value: 8.0 },
];

const prNegativeData: PieData[] = [
  { name: '价格争议', value: 45, color: '#1d4ed8' },
  { name: '质量问题', value: 28, color: '#4f46e5' },
  { name: '服务投诉', value: 15, color: '#3b82f6' },
  { name: '其他', value: 12, color: '#64748b' },
];

const prKOLData: PieData[] = [
  { name: '正面KOL', value: 12, color: '#2563eb' },
  { name: '中立KOL', value: 8, color: '#a5b4fc' },
  { name: '开始质疑', value: 3, color: '#4f46e5' },
];

const prSpreadData: TableData[] = [
  { name: '专业论坛', value: '起源', change: 100 },
  { name: '微博', value: '扩散', change: 65 },
  { name: '抖音', value: '爆发', change: 85 },
  { name: '小红书', value: '传播', change: 45 },
];

// 导出所有部门图表数据
export const departmentChartsData: DepartmentCharts[] = [
  {
    department: 'market',
    title: '市场部数据',
    cards: [
      {
        id: 'market-trend',
        title: '声量趋势',
        type: 'trend',
        size: 'half',
        data: marketTrendData,
        subtitle: '近7天声量变化趋势'
      },
      {
        id: 'market-channel',
        title: '渠道声量分布',
        type: 'bar',
        size: 'half',
        data: marketChannelData,
        subtitle: '各渠道声量统计'
      },
      {
        id: 'market-sentiment',
        title: '情感分析',
        type: 'sentiment',
        size: 'half',
        data: marketSentimentData,
        subtitle: '用户情感倾向分布'
      },
      {
        id: 'market-kol',
        title: 'KOL效果对比',
        type: 'table',
        size: 'half',
        data: marketKOLData,
        subtitle: '主要KOL影响力评估'
      },
    ]
  },
  {
    department: 'product',
    title: '产品部数据',
    cards: [
      {
        id: 'product-trend',
        title: '产品口碑趋势',
        type: 'trend',
        size: 'half',
        data: productTrendData,
        subtitle: '正负反馈占比变化'
      },
      {
        id: 'product-feature',
        title: '功能评价分布',
        type: 'bar',
        size: 'half',
        data: productFeatureData,
        subtitle: '各功能用户评价占比'
      },
      {
        id: 'product-quality',
        title: '质量问题统计',
        type: 'table',
        size: 'half',
        data: productQualityData,
        subtitle: '高频问题反馈统计'
      },
      {
        id: 'product-config',
        title: '配置选择热度',
        type: 'bar',
        size: 'half',
        data: productConfigData,
        subtitle: '用户配置选择偏好'
      },
    ]
  },
  {
    department: 'sales',
    title: '销售部数据',
    cards: [
      {
        id: 'sales-trend',
        title: '价格感知趋势',
        type: 'trend',
        size: 'half',
        data: salesTrendData,
        subtitle: '价格相关表达占比变化'
      },
      {
        id: 'sales-barrier',
        title: '决策障碍分析',
        type: 'pie',
        size: 'half',
        data: salesBarrierData,
        subtitle: '用户不下单主要原因'
      },
      {
        id: 'sales-service',
        title: '销售服务评分',
        type: 'radar',
        size: 'half',
        data: salesServiceData,
        subtitle: '各维度服务评分'
      },
      {
        id: 'sales-competitor',
        title: '竞品对比',
        type: 'table',
        size: 'half',
        data: salesCompetitorData,
        subtitle: '与竞品用户认知对比'
      },
    ]
  },
  {
    department: 'service',
    title: '售后部数据',
    cards: [
      {
        id: 'service-trend',
        title: '服务满意度趋势',
        type: 'trend',
        size: 'half',
        data: serviceTrendData,
        subtitle: '近7天满意度变化'
      },
      {
        id: 'service-issue',
        title: '问题类型分布',
        type: 'bar',
        size: 'half',
        data: serviceIssueData,
        subtitle: '各类型问题数量'
      },
      {
        id: 'service-store',
        title: '服务场景问题分布',
        type: 'bar',
        size: 'half',
        data: serviceStoreData,
        subtitle: '售后服务相关问题数量'
      },
      {
        id: 'service-response',
        title: '服务负向趋势',
        type: 'trend',
        size: 'half',
        data: serviceResponseData,
        subtitle: '服务相关负向表达占比'
      },
    ]
  },
  {
    department: 'pr',
    title: '公关部数据',
    cards: [
      {
        id: 'pr-trend',
        title: '舆情态势趋势',
        type: 'trend',
        size: 'half',
        data: prTrendData,
        subtitle: '负面率变化趋势(%)'
      },
      {
        id: 'pr-negative',
        title: '负面话题占比',
        type: 'pie',
        size: 'half',
        data: prNegativeData,
        subtitle: '各负面话题分布'
      },
      {
        id: 'pr-kol',
        title: 'KOL立场分布',
        type: 'pie',
        size: 'half',
        data: prKOLData,
        subtitle: 'KOL态度统计'
      },
      {
        id: 'pr-spread',
        title: '传播路径分析',
        type: 'table',
        size: 'half',
        data: prSpreadData,
        subtitle: '话题传播路径追踪'
      },
    ]
  }
];
