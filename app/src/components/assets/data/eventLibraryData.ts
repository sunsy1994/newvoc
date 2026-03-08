export type EventStatus = '进行中' | '已结束' | '归档';
export type EventRiskLevel = '高' | '中' | '低';

export interface EventLibraryItem {
  id: string;
  name: string;
  description: string;
  type: '新品上市' | '质量争议' | '服务体验' | '品牌传播' | '竞品对比';
  brand: string;
  model: string;
  keywords: string[];
  startDate: string;
  endDate: string;
  status: EventStatus;
  platforms: string[];
  contentCount: number;
  commentCount: number;
  authorCount: number;
  kolCount: number;
  heat: number;
  growth: number;
  riskLevel: EventRiskLevel;
  updatedAt: string;
  topics: string[];
}

export const eventLibraryData: EventLibraryItem[] = [
  {
    id: 'EVT-2026-001',
    name: '智行SUV冬测续航争议',
    description: '围绕冬测续航衰减与补能效率的集中讨论，争议持续上升。',
    type: '质量争议',
    brand: '极驰汽车',
    model: 'X7',
    keywords: ['冬测', '续航', '电耗', '补能'],
    startDate: '2026-01-06',
    endDate: '2026-03-20',
    status: '进行中',
    platforms: ['抖音', '微博', '汽车论坛', '小红书'],
    contentCount: 1246,
    commentCount: 23890,
    authorCount: 496,
    kolCount: 63,
    heat: 91,
    growth: 22.4,
    riskLevel: '高',
    updatedAt: '2026-03-08',
    topics: ['续航真实性', '低温电池表现', '官方解释可信度'],
  },
  {
    id: 'EVT-2026-002',
    name: '新款S9上市口碑拉升',
    description: '新车上市后一周口碑集中扩散，智能座舱和空间体验评价较高。',
    type: '新品上市',
    brand: '极驰汽车',
    model: 'S9',
    keywords: ['上市', '试驾', '智能座舱'],
    startDate: '2026-02-18',
    endDate: '2026-04-10',
    status: '进行中',
    platforms: ['懂车帝', '小红书', 'B站', '微博'],
    contentCount: 980,
    commentCount: 14567,
    authorCount: 382,
    kolCount: 47,
    heat: 82,
    growth: 18.9,
    riskLevel: '中',
    updatedAt: '2026-03-07',
    topics: ['智能座舱体验', '空间表现', '价格竞争力'],
  },
  {
    id: 'EVT-2026-003',
    name: '售后预约排队投诉',
    description: '集中在一线城市门店，涉及工单等待时间与配件到货慢。',
    type: '服务体验',
    brand: '极驰汽车',
    model: '全系',
    keywords: ['售后', '预约', '配件'],
    startDate: '2025-12-20',
    endDate: '2026-02-22',
    status: '已结束',
    platforms: ['微博', '汽车之家', '车主群'],
    contentCount: 446,
    commentCount: 6890,
    authorCount: 205,
    kolCount: 12,
    heat: 64,
    growth: -8.2,
    riskLevel: '中',
    updatedAt: '2026-02-22',
    topics: ['预约等待', '配件周期', '服务标准一致性'],
  },
  {
    id: 'EVT-2025-117',
    name: '竞品A7辅助驾驶对比讨论',
    description: '用户对比关注点集中在城市NOA稳定性与接管次数。',
    type: '竞品对比',
    brand: '极驰汽车',
    model: 'X7',
    keywords: ['NOA', '接管', '竞品对比'],
    startDate: '2025-11-08',
    endDate: '2026-01-31',
    status: '归档',
    platforms: ['B站', '懂车帝', '微博'],
    contentCount: 735,
    commentCount: 10342,
    authorCount: 318,
    kolCount: 36,
    heat: 58,
    growth: -12.6,
    riskLevel: '低',
    updatedAt: '2026-01-31',
    topics: ['城市NOA稳定性', '硬件冗余', '用户体感差异'],
  },
  {
    id: 'EVT-2026-004',
    name: '春节返乡补能网络体验',
    description: '跨省补能路线拥堵与排队体验成为春节期间高频议题。',
    type: '服务体验',
    brand: '极驰汽车',
    model: '全系',
    keywords: ['补能', '高速', '春节返乡'],
    startDate: '2026-01-22',
    endDate: '2026-02-15',
    status: '已结束',
    platforms: ['抖音', '微博', '车主APP'],
    contentCount: 563,
    commentCount: 12009,
    authorCount: 248,
    kolCount: 28,
    heat: 72,
    growth: -5.7,
    riskLevel: '中',
    updatedAt: '2026-02-16',
    topics: ['排队体验', '补能覆盖', '高速服务区体验'],
  },
  {
    id: 'EVT-2026-005',
    name: '春季品牌联名传播',
    description: '跨界联名活动带来品牌声量提升，情感正向反馈明显。',
    type: '品牌传播',
    brand: '极驰汽车',
    model: '全系',
    keywords: ['联名', '品牌活动', '传播'],
    startDate: '2026-03-01',
    endDate: '2026-04-01',
    status: '进行中',
    platforms: ['微博', '小红书', '抖音', '微信公众号'],
    contentCount: 322,
    commentCount: 4056,
    authorCount: 171,
    kolCount: 19,
    heat: 69,
    growth: 26.1,
    riskLevel: '低',
    updatedAt: '2026-03-08',
    topics: ['联名话题记忆点', '品牌年轻化', '内容二次传播'],
  },
];

export const eventTypeOptions = ['全部', '新品上市', '质量争议', '服务体验', '品牌传播', '竞品对比'] as const;
export const statusOptions = ['全部', '进行中', '已结束', '归档'] as const;
export const timeRangeOptions = ['全部时间', '近7天', '近30天', '近90天'] as const;
