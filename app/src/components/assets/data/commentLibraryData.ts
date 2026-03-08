export interface CommentLibraryItem {
  id: string;
  eventId: string;
  contentId: string;
  contentTitle: string;
  contentAuthor: string;
  contentAuthorType: 'KOL' | 'KOC' | '普通用户' | '媒体';
  fromKOLContent: boolean;
  text: string;
  platform: string;
  publishedAt: string;
  commentAuthorId: string;
  commentAuthorName: string;
  likeCount: number;
  interactionCount: number;
  replyLevel: number;
  sourceUrl: string;
  mindsetTag: string;
  stageTag: '准车主' | '试驾' | '车主' | '观望用户';
  propositionTag: string;
  issueTag: string;
  evidenceTag: string;
  sentimentTag: '积极' | '中性' | '负面' | '强负面';
  confidence: number;
  labelingReason: string;
  similarComments: string[];
}

export const commentLibraryData: CommentLibraryItem[] = [
  {
    id: 'CMT-9001',
    eventId: 'EVT-2026-001',
    contentId: 'CNT-1001',
    contentTitle: 'X7冬测续航实测：高速+低温工况是否达标',
    contentAuthor: '车研社',
    contentAuthorType: 'KOL',
    fromKOLContent: true,
    text: '我在哈尔滨开X7，零下20度通勤确实掉电快，但如果预热和路线规划做好，实际还能接受。',
    platform: 'B站',
    publishedAt: '2026-03-07 12:22',
    commentAuthorId: 'U-3011',
    commentAuthorName: '北方电车主',
    likeCount: 624,
    interactionCount: 739,
    replyLevel: 1,
    sourceUrl: 'https://example.com/comments/cmt-9001',
    mindsetTag: '理性对比',
    stageTag: '车主',
    propositionTag: '续航真实性',
    issueTag: '低温续航衰减',
    evidenceTag: '真实通勤案例',
    sentimentTag: '中性',
    confidence: 0.94,
    labelingReason: '含明确地域温度、使用场景和结论，信息完整度高。',
    similarComments: ['低温工况+路线规划', '通勤场景更接近真实用车'],
  },
  {
    id: 'CMT-9002',
    eventId: 'EVT-2026-001',
    contentId: 'CNT-1006',
    contentTitle: '直播切片：极寒环境补能效率实录',
    contentAuthor: '北方新能源观察',
    contentAuthorType: 'KOL',
    fromKOLContent: true,
    text: '排队40分钟才能充上，这种体验过年回家谁受得了？',
    platform: '微博',
    publishedAt: '2026-03-06 22:01',
    commentAuthorId: 'U-2008',
    commentAuthorName: '归乡候鸟',
    likeCount: 1093,
    interactionCount: 1315,
    replyLevel: 1,
    sourceUrl: 'https://example.com/comments/cmt-9002',
    mindsetTag: '效率焦虑',
    stageTag: '观望用户',
    propositionTag: '补能效率',
    issueTag: '排队时间过长',
    evidenceTag: '排队时长描述',
    sentimentTag: '强负面',
    confidence: 0.91,
    labelingReason: '强情绪+明确时间证据，观点指向明确。',
    similarComments: ['高峰期排队体验差', '节假日补能焦虑明显'],
  },
  {
    id: 'CMT-9003',
    eventId: 'EVT-2026-002',
    contentId: 'CNT-1003',
    contentTitle: 'S9首批提车作业：空间和智能座舱是亮点',
    contentAuthor: 'Alice驾趣',
    contentAuthorType: 'KOC',
    fromKOLContent: false,
    text: '今天试驾完感觉语音交互很顺，副驾连续下指令也不乱。',
    platform: '小红书',
    publishedAt: '2026-03-04 16:10',
    commentAuthorId: 'U-4412',
    commentAuthorName: '奶咖试驾',
    likeCount: 412,
    interactionCount: 498,
    replyLevel: 1,
    sourceUrl: 'https://example.com/comments/cmt-9003',
    mindsetTag: '尝鲜关注',
    stageTag: '试驾',
    propositionTag: '智能座舱体验',
    issueTag: '语音识别稳定性',
    evidenceTag: '试驾现场反馈',
    sentimentTag: '积极',
    confidence: 0.88,
    labelingReason: '描述具体体验动作与结果，可验证性较好。',
    similarComments: ['试驾环节语音表现好', '副驾指令识别稳定'],
  },
  {
    id: 'CMT-9004',
    eventId: 'EVT-2026-002',
    contentId: 'CNT-1004',
    contentTitle: '媒体横评：S9与同级竞品座舱体验对比',
    contentAuthor: 'AutoLab编辑部',
    contentAuthorType: '媒体',
    fromKOLContent: true,
    text: '看完横评，感觉S9车机确实快，但导航细节还得打磨。',
    platform: '懂车帝',
    publishedAt: '2026-03-03 11:02',
    commentAuthorId: 'U-7721',
    commentAuthorName: '参数与体感',
    likeCount: 368,
    interactionCount: 427,
    replyLevel: 1,
    sourceUrl: 'https://example.com/comments/cmt-9004',
    mindsetTag: '竞品对照',
    stageTag: '准车主',
    propositionTag: '智能座舱体验',
    issueTag: '导航细节优化',
    evidenceTag: '横评内容对照',
    sentimentTag: '中性',
    confidence: 0.86,
    labelingReason: '观点中性，存在明确对照对象和结论。',
    similarComments: ['车机快但地图策略一般', '导航细节是主要分歧点'],
  },
  {
    id: 'CMT-9005',
    eventId: 'EVT-2026-005',
    contentId: 'CNT-1005',
    contentTitle: '联名活动首周传播复盘：短视频平台声量最高',
    contentAuthor: '品牌观察局',
    contentAuthorType: '媒体',
    fromKOLContent: true,
    text: '这波联名确实让品牌年轻了，但担心热度过了就没后续。',
    platform: '抖音',
    publishedAt: '2026-03-08 09:20',
    commentAuthorId: 'U-5010',
    commentAuthorName: '品牌旁观者',
    likeCount: 742,
    interactionCount: 880,
    replyLevel: 1,
    sourceUrl: 'https://example.com/comments/cmt-9005',
    mindsetTag: '品牌认同',
    stageTag: '观望用户',
    propositionTag: '品牌年轻化',
    issueTag: '传播可持续性',
    evidenceTag: '活动周期观察',
    sentimentTag: '中性',
    confidence: 0.84,
    labelingReason: '观点含正反双向判断，语义清晰但证据较弱。',
    similarComments: ['联名短期有效', '后续持续内容是关键'],
  },
  {
    id: 'CMT-9006',
    eventId: 'EVT-2026-001',
    contentId: 'CNT-1002',
    contentTitle: '车主长帖：低温通勤一周真实电耗记录',
    contentAuthor: 'X7_沪A车主',
    contentAuthorType: '普通用户',
    fromKOLContent: false,
    text: '我觉得官方应该给冬季工况更透明的说明，不然大家预期都不一样。',
    platform: '汽车论坛',
    publishedAt: '2026-03-05 20:03',
    commentAuthorId: 'U-1192',
    commentAuthorName: '理性买车党',
    likeCount: 506,
    interactionCount: 642,
    replyLevel: 2,
    sourceUrl: 'https://example.com/comments/cmt-9006',
    mindsetTag: '焦虑观望',
    stageTag: '准车主',
    propositionTag: '续航真实性',
    issueTag: '信息透明度不足',
    evidenceTag: '官方口径对比',
    sentimentTag: '负面',
    confidence: 0.9,
    labelingReason: '问题定义明确，能直接映射业务沟通策略。',
    similarComments: ['官方口径与体验差异', '预期管理不足'],
  },
];

export const platformOptions = ['全部平台', 'B站', '微博', '小红书', '懂车帝', '抖音', '汽车论坛'] as const;
export const contentTypeSourceOptions = ['全部来源', 'KOL内容下', '普通用户内容下'] as const;
export const confidenceOptions = ['全部置信度', '高置信(>=0.9)'] as const;
export const publishRangeOptions = ['全部时间', '近7天', '近30天', '近90天'] as const;
export const interactionRangeOptions = ['全部互动', '300+', '500+', '800+', '1,000+'] as const;
export const mindsetOptions = ['全部心智', '理性对比', '效率焦虑', '尝鲜关注', '竞品对照', '品牌认同', '焦虑观望'] as const;
export const stageOptions = ['全部阶段', '准车主', '试驾', '车主', '观望用户'] as const;
export const propositionOptions = ['全部命题', '续航真实性', '补能效率', '智能座舱体验', '品牌年轻化'] as const;
export const issueOptions = ['全部问题', '低温续航衰减', '排队时间过长', '语音识别稳定性', '导航细节优化', '传播可持续性', '信息透明度不足'] as const;
export const evidenceOptions = ['全部证据', '真实通勤案例', '排队时长描述', '试驾现场反馈', '横评内容对照', '活动周期观察', '官方口径对比'] as const;
export const sentimentOptions = ['全部情绪', '积极', '中性', '负面', '强负面'] as const;
