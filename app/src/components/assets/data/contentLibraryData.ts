export type AuthorType = 'KOL' | 'KOC' | '普通用户' | '媒体';
export type ContentType = '测评' | '对比' | '提车作业' | '资讯' | '讨论';
export type MediaForm = '图文' | '视频' | '直播切片' | '长文';

export interface ContentLibraryItem {
  id: string;
  eventId: string;
  eventName: string;
  title: string;
  summary: string;
  sourceUrl: string;
  platform: string;
  contentType: ContentType;
  mediaForm: MediaForm;
  authorId: string;
  authorName: string;
  authorType: AuthorType;
  isKOL: boolean;
  kolDomain?: string;
  fansCount?: number;
  publishedAt: string;
  likeCount: number;
  commentCount: number;
  shareCount: number;
  favoriteCount: number;
  engagementTotal: number;
  propositionTags: string[];
  issueTags: string[];
  evidenceTags: string[];
  contentTags: string[];
  tagConfidence: number;
  isHighConfidenceSample: boolean;
  mindsetDistribution: Array<{ label: string; value: number }>;
}

export const contentLibraryData: ContentLibraryItem[] = [
  {
    id: 'CNT-1001',
    eventId: 'EVT-2026-001',
    eventName: '智行SUV冬测续航争议',
    title: 'X7冬测续航实测：高速+低温工况是否达标',
    summary: '对比官方标称与真实高速工况，重点覆盖低温续航、电耗和补能效率。',
    sourceUrl: 'https://example.com/posts/cnt-1001',
    platform: 'B站',
    contentType: '测评',
    mediaForm: '视频',
    authorId: 'AUTH-301',
    authorName: '车研社',
    authorType: 'KOL',
    isKOL: true,
    kolDomain: '新能源测评',
    fansCount: 1260000,
    publishedAt: '2026-03-07 10:12',
    likeCount: 6120,
    commentCount: 1864,
    shareCount: 930,
    favoriteCount: 1210,
    engagementTotal: 10124,
    propositionTags: ['续航真实性', '低温电池表现'],
    issueTags: ['续航衰减'],
    evidenceTags: ['实测里程', '充电曲线'],
    contentTags: ['冬测', '高速工况'],
    tagConfidence: 0.93,
    isHighConfidenceSample: true,
    mindsetDistribution: [
      { label: '理性对比', value: 45 },
      { label: '担忧续航', value: 38 },
      { label: '品牌支持', value: 17 },
    ],
  },
  {
    id: 'CNT-1002',
    eventId: 'EVT-2026-001',
    eventName: '智行SUV冬测续航争议',
    title: '车主长帖：低温通勤一周真实电耗记录',
    summary: '普通车主记录一周通勤里程与电耗，并补充了家充与快充体验。',
    sourceUrl: 'https://example.com/posts/cnt-1002',
    platform: '汽车论坛',
    contentType: '讨论',
    mediaForm: '长文',
    authorId: 'AUTH-112',
    authorName: 'X7_沪A车主',
    authorType: '普通用户',
    isKOL: false,
    publishedAt: '2026-03-05 19:26',
    likeCount: 890,
    commentCount: 412,
    shareCount: 88,
    favoriteCount: 266,
    engagementTotal: 1656,
    propositionTags: ['使用场景差异'],
    issueTags: ['通勤续航焦虑'],
    evidenceTags: ['行驶日志'],
    contentTags: ['车主体验'],
    tagConfidence: 0.86,
    isHighConfidenceSample: true,
    mindsetDistribution: [
      { label: '实用主义', value: 52 },
      { label: '焦虑观望', value: 34 },
      { label: '品牌拥护', value: 14 },
    ],
  },
  {
    id: 'CNT-1003',
    eventId: 'EVT-2026-002',
    eventName: '新款S9上市口碑拉升',
    title: 'S9首批提车作业：空间和智能座舱是亮点',
    summary: '提车用户重点反馈车机流畅度、后排空间和交付体验。',
    sourceUrl: 'https://example.com/posts/cnt-1003',
    platform: '小红书',
    contentType: '提车作业',
    mediaForm: '图文',
    authorId: 'AUTH-223',
    authorName: 'Alice驾趣',
    authorType: 'KOC',
    isKOL: false,
    fansCount: 28000,
    publishedAt: '2026-03-04 14:33',
    likeCount: 3400,
    commentCount: 528,
    shareCount: 202,
    favoriteCount: 980,
    engagementTotal: 5110,
    propositionTags: ['空间表现', '座舱体验'],
    issueTags: ['交付周期咨询'],
    evidenceTags: ['提车照片'],
    contentTags: ['新车上市'],
    tagConfidence: 0.88,
    isHighConfidenceSample: true,
    mindsetDistribution: [
      { label: '尝鲜关注', value: 48 },
      { label: '价格敏感', value: 30 },
      { label: '配置导向', value: 22 },
    ],
  },
  {
    id: 'CNT-1004',
    eventId: 'EVT-2026-002',
    eventName: '新款S9上市口碑拉升',
    title: '媒体横评：S9与同级竞品座舱体验对比',
    summary: '从响应速度、导航能力和语音识别三个维度进行对比。',
    sourceUrl: 'https://example.com/posts/cnt-1004',
    platform: '懂车帝',
    contentType: '对比',
    mediaForm: '视频',
    authorId: 'AUTH-556',
    authorName: 'AutoLab编辑部',
    authorType: '媒体',
    isKOL: true,
    kolDomain: '汽车媒体',
    fansCount: 980000,
    publishedAt: '2026-03-03 09:40',
    likeCount: 2800,
    commentCount: 1360,
    shareCount: 420,
    favoriteCount: 630,
    engagementTotal: 5210,
    propositionTags: ['智能座舱体验'],
    issueTags: ['竞品差距'],
    evidenceTags: ['横评维度表'],
    contentTags: ['上市横评'],
    tagConfidence: 0.91,
    isHighConfidenceSample: true,
    mindsetDistribution: [
      { label: '竞品对照', value: 57 },
      { label: '品牌偏好', value: 26 },
      { label: '参数党', value: 17 },
    ],
  },
  {
    id: 'CNT-1005',
    eventId: 'EVT-2026-005',
    eventName: '春季品牌联名传播',
    title: '联名活动首周传播复盘：短视频平台声量最高',
    summary: '传播波峰集中在活动当天晚间，KOL二创内容贡献明显。',
    sourceUrl: 'https://example.com/posts/cnt-1005',
    platform: '抖音',
    contentType: '资讯',
    mediaForm: '视频',
    authorId: 'AUTH-445',
    authorName: '品牌观察局',
    authorType: '媒体',
    isKOL: true,
    kolDomain: '品牌营销',
    fansCount: 540000,
    publishedAt: '2026-03-08 08:05',
    likeCount: 4600,
    commentCount: 690,
    shareCount: 510,
    favoriteCount: 822,
    engagementTotal: 6622,
    propositionTags: ['品牌年轻化'],
    issueTags: ['话题可持续性'],
    evidenceTags: ['传播峰值曲线'],
    contentTags: ['联名活动'],
    tagConfidence: 0.84,
    isHighConfidenceSample: false,
    mindsetDistribution: [
      { label: '娱乐参与', value: 62 },
      { label: '品牌认同', value: 24 },
      { label: '路人围观', value: 14 },
    ],
  },
  {
    id: 'CNT-1006',
    eventId: 'EVT-2026-001',
    eventName: '智行SUV冬测续航争议',
    title: '直播切片：极寒环境补能效率实录',
    summary: '记录补能排队、充电桩功率波动与实际等待时长。',
    sourceUrl: 'https://example.com/posts/cnt-1006',
    platform: '微博',
    contentType: '测评',
    mediaForm: '直播切片',
    authorId: 'AUTH-880',
    authorName: '北方新能源观察',
    authorType: 'KOL',
    isKOL: true,
    kolDomain: '补能网络',
    fansCount: 350000,
    publishedAt: '2026-03-06 21:18',
    likeCount: 1820,
    commentCount: 970,
    shareCount: 215,
    favoriteCount: 411,
    engagementTotal: 3416,
    propositionTags: ['补能效率'],
    issueTags: ['排队时间'],
    evidenceTags: ['现场录像'],
    contentTags: ['极寒补能'],
    tagConfidence: 0.9,
    isHighConfidenceSample: true,
    mindsetDistribution: [
      { label: '效率焦虑', value: 49 },
      { label: '理性比较', value: 33 },
      { label: '情绪吐槽', value: 18 },
    ],
  },
];

export const platformOptions = ['全部平台', 'B站', '汽车论坛', '小红书', '懂车帝', '抖音', '微博'] as const;
export const contentTypeOptions = ['全部类型', '测评', '对比', '提车作业', '资讯', '讨论'] as const;
export const authorTypeOptions = ['全部作者', 'KOL', 'KOC', '普通用户', '媒体'] as const;
export const publishRangeOptions = ['全部时间', '近7天', '近30天', '近90天'] as const;
export const interactionRangeOptions = ['全部互动', '500+', '1,000+', '3,000+', '5,000+'] as const;
export const tagFilterOptions = ['全部标签', '命题', '问题', '证据'] as const;
export const confidenceOptions = ['全部样本', '高置信样本'] as const;
