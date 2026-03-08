export interface KOLItem {
  id: string;
  nickname: string;
  avatar: string;
  platform: string;
  fans: number;
  domain: '汽车' | '科技' | '生活' | '综合';
  authorType: 'KOL' | 'KOC' | '媒体';
  eventId: string;
  eventPosts: number;
  totalEngagement: number;
  totalComments: number;
  avgEngagement: number;
  highConfidenceRatio: number;
  effectiveEngagementRate: number;
  riskScore: number;
  roleTags: string[];
  mindsetTop3: string[];
  stageTop3: string[];
  intentionTop3: string[];
  summary: string;
  representativeComments: Array<{
    type: '高点赞' | '高置信' | '高意向' | '高争议' | '强证据';
    text: string;
  }>;
}

export const kolLibraryData: KOLItem[] = [
  {
    id: 'KOL-001',
    nickname: '车研社',
    avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=80&h=80&fit=crop&crop=face',
    platform: 'B站',
    fans: 1260000,
    domain: '汽车',
    authorType: 'KOL',
    eventId: 'EVT-2026-001',
    eventPosts: 5,
    totalEngagement: 28600,
    totalComments: 4120,
    avgEngagement: 5720,
    highConfidenceRatio: 0.46,
    effectiveEngagementRate: 0.39,
    riskScore: 0.28,
    roleTags: ['测评型', '解释型', '高证据型'],
    mindsetTop3: ['理性对比', '技术偏好', '价值平衡'],
    stageTop3: ['准车主', '试驾', '车主'],
    intentionTop3: ['对比', '试驾', '购买'],
    summary: '该KOL在本事件中以测评和证据型内容为主，对准车主与试驾群体的有效触达明显。',
    representativeComments: [
      { type: '高点赞', text: '这组实测数据很有参考价值，比只看参数靠谱。' },
      { type: '高置信', text: '我同路线通勤，实测结果和你视频接近。' },
      { type: '强证据', text: '低温电耗和充电曲线截图都贴出来了，可信。' },
    ],
  },
  {
    id: 'KOL-002',
    nickname: '北方新能源观察',
    avatar: 'https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=80&h=80&fit=crop&crop=face',
    platform: '微博',
    fans: 350000,
    domain: '科技',
    authorType: 'KOL',
    eventId: 'EVT-2026-001',
    eventPosts: 7,
    totalEngagement: 19420,
    totalComments: 3610,
    avgEngagement: 2774,
    highConfidenceRatio: 0.33,
    effectiveEngagementRate: 0.31,
    riskScore: 0.52,
    roleTags: ['争议型', '证据型'],
    mindsetTop3: ['效率焦虑', '焦虑观望', '理性对比'],
    stageTop3: ['观望用户', '准车主', '车主'],
    intentionTop3: ['了解', '对比', '放弃'],
    summary: '聚集了大量补能焦虑人群，互动高但争议度也高，适合证据补充型合作。',
    representativeComments: [
      { type: '高争议', text: '排队时间这个问题如果不改善，谁还敢长途。' },
      { type: '高点赞', text: '现场实录很直观，至少不是空口下结论。' },
      { type: '高意向', text: '如果后续补能优化我愿意再试驾一次。' },
    ],
  },
  {
    id: 'KOL-003',
    nickname: 'AutoLab编辑部',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=80&h=80&fit=crop&crop=face',
    platform: '懂车帝',
    fans: 980000,
    domain: '汽车',
    authorType: '媒体',
    eventId: 'EVT-2026-002',
    eventPosts: 4,
    totalEngagement: 16890,
    totalComments: 2890,
    avgEngagement: 4222,
    highConfidenceRatio: 0.41,
    effectiveEngagementRate: 0.36,
    riskScore: 0.22,
    roleTags: ['解释型', '测评型'],
    mindsetTop3: ['竞品对照', '技术偏好', '价值平衡'],
    stageTop3: ['准车主', '试驾', '观望用户'],
    intentionTop3: ['对比', '试驾', '购买'],
    summary: '对比型内容结构清晰，准车主人群转化线索较多，整体风险可控。',
    representativeComments: [
      { type: '高置信', text: '横评维度覆盖完整，确实能看出差异。' },
      { type: '高点赞', text: '最有用的是把语音和导航拆开测。' },
      { type: '强证据', text: '同路况多车对比，样本可信度高。' },
    ],
  },
  {
    id: 'KOL-004',
    nickname: '品牌观察局',
    avatar: 'https://images.unsplash.com/photo-1546961329-78bef0414d7c?w=80&h=80&fit=crop&crop=face',
    platform: '抖音',
    fans: 540000,
    domain: '综合',
    authorType: '媒体',
    eventId: 'EVT-2026-005',
    eventPosts: 6,
    totalEngagement: 22010,
    totalComments: 2450,
    avgEngagement: 3668,
    highConfidenceRatio: 0.27,
    effectiveEngagementRate: 0.29,
    riskScore: 0.35,
    roleTags: ['种草型', '高意向触发型'],
    mindsetTop3: ['品牌认同', '娱乐参与', '路人围观'],
    stageTop3: ['观望用户', '准车主', '试驾'],
    intentionTop3: ['了解', '对比', '试驾'],
    summary: '适合做品牌心智放大节点，兴趣触发强，但高置信证据表达偏弱。',
    representativeComments: [
      { type: '高意向', text: '联名之后对这品牌印象好很多，准备去店里看看。' },
      { type: '高点赞', text: '这波内容调性年轻化做得不错。' },
      { type: '高争议', text: '热闹归热闹，和产品实力关系不大吧。' },
    ],
  },
];

export const domainOptions = ['全部领域', '汽车', '科技', '生活', '综合'] as const;
export const authorTypeOptions = ['全部类型', 'KOL', 'KOC', '媒体'] as const;
export const platformOptions = ['全部平台', 'B站', '微博', '懂车帝', '抖音', '小红书'] as const;
export const fansRangeOptions = ['全部粉丝', '10万+', '30万+', '50万+', '100万+'] as const;
export const sortOptions = [
  { label: '总互动量', value: 'totalEngagement' },
  { label: '评论总量', value: 'totalComments' },
  { label: '有效互动率', value: 'effectiveEngagementRate' },
  { label: '高置信评论占比', value: 'highConfidenceRatio' },
  { label: '风险值', value: 'riskScore' },
  { label: '发文数', value: 'eventPosts' },
  { label: '粉丝量', value: 'fans' },
] as const;
