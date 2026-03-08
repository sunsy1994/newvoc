export interface AuthorContentItem {
  title: string;
  publishedAt: string;
  contentType: '提车' | '试驾' | '对比' | '测评' | '体验' | '投诉';
  engagement: number;
  comments: number;
  propositionTag: string;
  issueTag: string;
}

export interface AuthorLibraryItem {
  id: string;
  eventId: string;
  nickname: string;
  platform: string;
  authorType: '普通用户' | 'KOC' | '车主' | '试驾' | '媒体' | '品牌';
  isKOL: boolean;
  stageTag: '车主' | '试驾' | '准车主' | '未知';
  stageConfidence: number;
  stageReason: string;
  posts: number;
  totalEngagement: number;
  commentTriggerCount: number;
  topContentTypes: string[];
  propositionTop: string[];
  issueTop: string[];
  evidenceStrength: number;
  evidenceType: '亲历' | '试驾' | '截图' | '视频' | '转述';
  reproducible: boolean;
  controversyScore: number;
  highValue: boolean;
  highControversy: boolean;
  highConfidence: boolean;
  roleTags: string[];
  aiSummary: string;
  contentTimeline: AuthorContentItem[];
  representativeContents: string[];
  representativeComments: string[];
}

export const authorLibraryData: AuthorLibraryItem[] = [
  {
    id: 'AUTH-112',
    eventId: 'EVT-2026-001',
    nickname: 'X7_沪A车主',
    platform: '汽车论坛',
    authorType: '车主',
    isKOL: false,
    stageTag: '车主',
    stageConfidence: 0.93,
    stageReason: '命中“提车”“上牌”“通勤里程”等关键词，且持续输出真实使用细节。',
    posts: 6,
    totalEngagement: 4680,
    commentTriggerCount: 1286,
    topContentTypes: ['提车', '体验'],
    propositionTop: ['续航真实性', '补能效率', '车机体验'],
    issueTop: ['低温续航衰减', '信息透明度不足'],
    evidenceStrength: 88,
    evidenceType: '亲历',
    reproducible: true,
    controversyScore: 31,
    highValue: true,
    highControversy: false,
    highConfidence: true,
    roleTags: ['高证据作者', '真实车主样本'],
    aiSummary: '该作者以真实通勤体验为主，具备高置信车主特征，证据价值高且争议可控。',
    contentTimeline: [
      { title: '一周低温通勤电耗记录', publishedAt: '2026-03-02 08:14', contentType: '体验', engagement: 1210, comments: 366, propositionTag: '续航真实性', issueTag: '低温续航衰减' },
      { title: '提车后300公里补能体验', publishedAt: '2026-03-04 21:40', contentType: '提车', engagement: 1390, comments: 402, propositionTag: '补能效率', issueTag: '排队时间' },
    ],
    representativeContents: ['一周低温通勤电耗记录', '提车后300公里补能体验'],
    representativeComments: ['这种细节最有参考意义', '真实车主反馈比参数更重要'],
  },
  {
    id: 'AUTH-301',
    eventId: 'EVT-2026-001',
    nickname: '车研社',
    platform: 'B站',
    authorType: '媒体',
    isKOL: true,
    stageTag: '试驾',
    stageConfidence: 0.84,
    stageReason: '内容以试驾与横评为主，命中“试驾路线”“对比测试”等规则。',
    posts: 5,
    totalEngagement: 28600,
    commentTriggerCount: 4120,
    topContentTypes: ['测评', '对比'],
    propositionTop: ['续航真实性', '智能座舱体验'],
    issueTop: ['续航衰减', '导航细节优化'],
    evidenceStrength: 81,
    evidenceType: '视频',
    reproducible: true,
    controversyScore: 47,
    highValue: true,
    highControversy: true,
    highConfidence: true,
    roleTags: ['高互动作者', '高证据作者', '高争议作者'],
    aiSummary: '该作者传播效率高，能激发大量互动，但部分对比表达容易放大争议。',
    contentTimeline: [
      { title: 'X7冬测续航实测', publishedAt: '2026-03-07 10:12', contentType: '测评', engagement: 10124, comments: 1864, propositionTag: '续航真实性', issueTag: '低温续航衰减' },
      { title: '同级补能效率横评', publishedAt: '2026-03-06 19:05', contentType: '对比', engagement: 8230, comments: 1198, propositionTag: '补能效率', issueTag: '排队时间' },
    ],
    representativeContents: ['X7冬测续航实测', '同级补能效率横评'],
    representativeComments: ['证据很硬但语气有点激进', '有数据支持，结论可信'],
  },
  {
    id: 'AUTH-223',
    eventId: 'EVT-2026-002',
    nickname: 'Alice驾趣',
    platform: '小红书',
    authorType: 'KOC',
    isKOL: false,
    stageTag: '试驾',
    stageConfidence: 0.79,
    stageReason: '多次命中“试驾体验”“门店试驾反馈”，但缺少持续使用证据。',
    posts: 4,
    totalEngagement: 7340,
    commentTriggerCount: 1230,
    topContentTypes: ['试驾', '体验'],
    propositionTop: ['智能座舱体验', '空间表现'],
    issueTop: ['交付周期咨询'],
    evidenceStrength: 69,
    evidenceType: '视频',
    reproducible: false,
    controversyScore: 22,
    highValue: true,
    highControversy: false,
    highConfidence: false,
    roleTags: ['潜在KOC', '试驾体验样本'],
    aiSummary: '该作者对试驾阶段用户吸引力较强，内容互动稳定，适合作为轻量种草节点。',
    contentTimeline: [
      { title: 'S9门店试驾第一感受', publishedAt: '2026-03-04 14:33', contentType: '试驾', engagement: 5110, comments: 528, propositionTag: '智能座舱体验', issueTag: '语音稳定性' },
      { title: '后排空间实测记录', publishedAt: '2026-03-05 16:22', contentType: '体验', engagement: 2230, comments: 312, propositionTag: '空间表现', issueTag: '座椅舒适性' },
    ],
    representativeContents: ['S9门店试驾第一感受'],
    representativeComments: ['看完更想去试驾了', '信息真实但还想看长期体验'],
  },
  {
    id: 'AUTH-445',
    eventId: 'EVT-2026-005',
    nickname: '品牌观察局',
    platform: '抖音',
    authorType: '媒体',
    isKOL: true,
    stageTag: '未知',
    stageConfidence: 0.52,
    stageReason: '以传播复盘为主，阶段特征弱，更多是观察视角。',
    posts: 6,
    totalEngagement: 22010,
    commentTriggerCount: 2450,
    topContentTypes: ['体验', '对比'],
    propositionTop: ['品牌年轻化', '传播节奏'],
    issueTop: ['传播可持续性'],
    evidenceStrength: 55,
    evidenceType: '转述',
    reproducible: false,
    controversyScore: 42,
    highValue: false,
    highControversy: true,
    highConfidence: false,
    roleTags: ['高互动作者', '高争议作者'],
    aiSummary: '该作者擅长制造讨论热度，但证据链偏弱，建议作为传播观察样本而非证据样本。',
    contentTimeline: [
      { title: '联名传播复盘', publishedAt: '2026-03-08 08:05', contentType: '体验', engagement: 6622, comments: 690, propositionTag: '品牌年轻化', issueTag: '传播可持续性' },
      { title: '活动话题二创对比', publishedAt: '2026-03-08 20:12', contentType: '对比', engagement: 5290, comments: 512, propositionTag: '传播节奏', issueTag: '热度衰减' },
    ],
    representativeContents: ['联名传播复盘'],
    representativeComments: ['热度很高但转化不明确', '观点有趣但证据偏少'],
  },
];

export const platformOptions = ['全部平台', '汽车论坛', 'B站', '小红书', '抖音', '微博', '懂车帝'] as const;
export const authorTypeOptions = ['全部作者类型', '普通用户', 'KOC', '车主', '试驾', '媒体', '品牌'] as const;
export const stageOptions = ['全部阶段', '车主', '试驾', '准车主', '未知'] as const;
export const timeRangeOptions = ['全部时间', '近24h', '近7天', '近30天', '事件全周期'] as const;
export const contentTypeOptions = ['全部内容类型', '提车', '试驾', '对比', '测评', '体验', '投诉'] as const;
export const sentimentOptions = ['全部情绪', '积极', '中性', '负面', '强负面'] as const;
export const sortOptions = [
  { label: '发文数', value: 'posts' },
  { label: '总互动量', value: 'totalEngagement' },
  { label: '评论触发量', value: 'commentTriggerCount' },
  { label: '证据强度', value: 'evidenceStrength' },
  { label: '争议值', value: 'controversyScore' },
  { label: '阶段置信度', value: 'stageConfidence' },
] as const;
