export type AuthorType = 'KOL' | 'KOC' | '普通用户' | '媒体';
export type ContentType = '测评' | '对比' | '提车作业' | '资讯' | '讨论';
export type MediaForm = '图文' | '视频' | '直播切片' | '长文';
export type ContentValueLevel = '高' | '中' | '低';
export type ContentValueFlag = '高互动' | '高证据' | '高争议' | '高意向' | '核心内容';
export type CommentStage = '车主' | '试驾' | '准车主' | '围观';
export type CommentAttitude = '认可' | '质疑' | '中立';

export interface ContentDistributionItem {
  label: string;
  value: number;
}

export interface ContentCommentProfile {
  highConfidenceRate: number;
  ownerRate: number;
  testDriveRate: number;
  prospectRate: number;
  doubtRate: number;
  approvalRate: number;
  positiveRate: number;
  negativeRate: number;
  stageTop: CommentStage;
  attitudeTop: CommentAttitude;
  mindsetDistribution: ContentDistributionItem[];
  emotionDistribution: ContentDistributionItem[];
  attitudeDistribution: ContentDistributionItem[];
  stageDistribution: ContentDistributionItem[];
}

export interface RelatedContentLink {
  id: string;
  title: string;
  reason: string;
}

export interface ContentRepresentativeComment {
  label: string;
  text: string;
}

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
  riskTags: string[];
  tagConfidence: number;
  isHighConfidenceSample: boolean;
  contentRole: string;
  valueLevel: ContentValueLevel;
  valueFlags: ContentValueFlag[];
  valueSummary: string;
  valueReasons: string[];
  riskSummary: string;
  isCoreContent: boolean;
  commentProfile: ContentCommentProfile;
  representativeComments: ContentRepresentativeComment[];
  relatedContents: RelatedContentLink[];
}

export const contentLibraryData: ContentLibraryItem[] = [
  {
    id: 'CNT-1001',
    eventId: 'EVT-2026-001',
    eventName: '智行SUV冬测续航争议',
    title: 'X7冬测续航实测：高速+低温工况是否达标',
    summary: '对比官方标称与真实高速工况，重点覆盖低温续航、电耗和补能效率，是本事件的证据型主内容。',
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
    issueTags: ['续航衰减', '官方标称偏差'],
    evidenceTags: ['实测里程', '充电曲线'],
    contentTags: ['冬测', '高速工况'],
    riskTags: ['参数争议扩散'],
    tagConfidence: 0.93,
    isHighConfidenceSample: true,
    contentRole: '测评型',
    valueLevel: '高',
    valueFlags: ['高互动', '高证据', '高争议', '核心内容'],
    valueSummary: '用完整实测链路建立争议证据，既拉高互动，也成为后续评论判断的中心样本。',
    valueReasons: ['包含高速与低温双场景数据', '评论区出现大量车主现身补充', '被多平台二次引用'],
    riskSummary: '若官方未及时回应，容易被解读为“官方续航不可信”的锚点内容。',
    isCoreContent: true,
    commentProfile: {
      highConfidenceRate: 72,
      ownerRate: 34,
      testDriveRate: 18,
      prospectRate: 27,
      doubtRate: 49,
      approvalRate: 31,
      positiveRate: 22,
      negativeRate: 46,
      stageTop: '车主',
      attitudeTop: '质疑',
      mindsetDistribution: [
        { label: '理性对比', value: 45 },
        { label: '担忧续航', value: 38 },
        { label: '品牌支持', value: 17 },
      ],
      emotionDistribution: [
        { label: '负向', value: 46 },
        { label: '中性', value: 32 },
        { label: '正向', value: 22 },
      ],
      attitudeDistribution: [
        { label: '质疑', value: 49 },
        { label: '认可', value: 31 },
        { label: '中立', value: 20 },
      ],
      stageDistribution: [
        { label: '车主', value: 34 },
        { label: '准车主', value: 27 },
        { label: '试驾', value: 18 },
        { label: '围观', value: 21 },
      ],
    },
    representativeComments: [
      { label: '高点赞评论', text: '如果是日常通勤还好，但高速+低温只剩这个续航，官方口径确实需要重讲。' },
      { label: '高置信评论', text: '我是北方车主，零下十度开暖风差不多就是这个掉电水平，数据基本对得上。' },
      { label: '强情绪评论', text: '买之前看标称，买之后看现实，用户最怕的就是这个落差。' },
    ],
    relatedContents: [
      { id: 'CNT-1006', title: '直播切片：极寒环境补能效率实录', reason: '同命题内容，补充补能维度证据' },
      { id: 'CNT-1002', title: '车主长帖：低温通勤一周真实电耗记录', reason: '同事件车主视角，对测评结论做真实使用补充' },
    ],
  },
  {
    id: 'CNT-1002',
    eventId: 'EVT-2026-001',
    eventName: '智行SUV冬测续航争议',
    title: '车主长帖：低温通勤一周真实电耗记录',
    summary: '普通车主记录一周通勤里程与电耗，并补充家充与快充体验，是事件里最典型的真实使用样本。',
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
    evidenceTags: ['行驶日志', '家充记录'],
    contentTags: ['车主体验', '通勤'],
    riskTags: ['个案被放大'],
    tagConfidence: 0.86,
    isHighConfidenceSample: true,
    contentRole: '体验型',
    valueLevel: '高',
    valueFlags: ['高证据', '高意向'],
    valueSummary: '虽然互动量不高，但车主链路完整，能回答“真实场景到底怎么样”这个关键问题。',
    valueReasons: ['真实车主连续一周记录', '评论中出现大量准车主追问', '与KOL测评形成互证'],
    riskSummary: '若缺少更多地域样本，容易被认为只是单一个案，外推风险较高。',
    isCoreContent: false,
    commentProfile: {
      highConfidenceRate: 81,
      ownerRate: 42,
      testDriveRate: 9,
      prospectRate: 31,
      doubtRate: 28,
      approvalRate: 44,
      positiveRate: 29,
      negativeRate: 33,
      stageTop: '车主',
      attitudeTop: '认可',
      mindsetDistribution: [
        { label: '实用主义', value: 52 },
        { label: '焦虑观望', value: 34 },
        { label: '品牌拥护', value: 14 },
      ],
      emotionDistribution: [
        { label: '中性', value: 38 },
        { label: '负向', value: 33 },
        { label: '正向', value: 29 },
      ],
      attitudeDistribution: [
        { label: '认可', value: 44 },
        { label: '质疑', value: 28 },
        { label: '中立', value: 28 },
      ],
      stageDistribution: [
        { label: '车主', value: 42 },
        { label: '准车主', value: 31 },
        { label: '围观', value: 18 },
        { label: '试驾', value: 9 },
      ],
    },
    representativeComments: [
      { label: '高点赞评论', text: '这种连续一周记录比一次性测评更有参考价值，至少知道日常能不能用。' },
      { label: '高置信评论', text: '我同城同车型，冬天上下班电耗差不多，堵车比高速更稳一点。' },
      { label: '高意向评论', text: '如果家里能装桩，这个续航我还能接受，主要看冬季高速返乡。' },
    ],
    relatedContents: [
      { id: 'CNT-1001', title: 'X7冬测续航实测：高速+低温工况是否达标', reason: '同争议主线，提供专业测评视角' },
      { id: 'CNT-1006', title: '直播切片：极寒环境补能效率实录', reason: '补足充电体验维度' },
    ],
  },
  {
    id: 'CNT-1003',
    eventId: 'EVT-2026-002',
    eventName: '新款S9上市口碑拉升',
    title: 'S9首批提车作业：空间和智能座舱是亮点',
    summary: '提车用户重点反馈车机流畅度、后排空间和交付体验，是上市期最有效的口碑拉升内容。',
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
    evidenceTags: ['提车照片', '车机实拍'],
    contentTags: ['新车上市', '提车日记'],
    riskTags: [],
    tagConfidence: 0.88,
    isHighConfidenceSample: true,
    contentRole: '提车型',
    valueLevel: '高',
    valueFlags: ['高互动', '高意向', '核心内容'],
    valueSummary: '评论区以准车主咨询和体验认可为主，是典型的成交前参考内容。',
    valueReasons: ['收藏率高，说明决策参考价值强', '提车视角降低营销感', '评论以配置和交付咨询为主'],
    riskSummary: '当前风险低，主要关注交付周期是否会从咨询点演化为负面议题。',
    isCoreContent: true,
    commentProfile: {
      highConfidenceRate: 68,
      ownerRate: 26,
      testDriveRate: 21,
      prospectRate: 37,
      doubtRate: 16,
      approvalRate: 58,
      positiveRate: 51,
      negativeRate: 12,
      stageTop: '准车主',
      attitudeTop: '认可',
      mindsetDistribution: [
        { label: '尝鲜关注', value: 48 },
        { label: '价格敏感', value: 30 },
        { label: '配置导向', value: 22 },
      ],
      emotionDistribution: [
        { label: '正向', value: 51 },
        { label: '中性', value: 37 },
        { label: '负向', value: 12 },
      ],
      attitudeDistribution: [
        { label: '认可', value: 58 },
        { label: '中立', value: 26 },
        { label: '质疑', value: 16 },
      ],
      stageDistribution: [
        { label: '准车主', value: 37 },
        { label: '车主', value: 26 },
        { label: '试驾', value: 21 },
        { label: '围观', value: 16 },
      ],
    },
    representativeComments: [
      { label: '高点赞评论', text: '后排空间和车机一起在线，家用车最怕偏科，S9这点挺稳。' },
      { label: '高意向评论', text: '准备本周末去试驾，主要想看看车机和座椅舒适度是不是和你说的一样。' },
      { label: '高置信评论', text: '我已经提车三天，车机流畅度和你拍出来差不多，导航语音反应很快。' },
    ],
    relatedContents: [
      { id: 'CNT-1004', title: '媒体横评：S9与同级竞品座舱体验对比', reason: '同命题内容，补充竞品比较视角' },
    ],
  },
  {
    id: 'CNT-1004',
    eventId: 'EVT-2026-002',
    eventName: '新款S9上市口碑拉升',
    title: '媒体横评：S9与同级竞品座舱体验对比',
    summary: '从响应速度、导航能力和语音识别三个维度横评同级车型，帮助用户建立差异认知。',
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
    issueTags: ['竞品差距', '语音识别准确率'],
    evidenceTags: ['横评维度表', '实测录屏'],
    contentTags: ['上市横评'],
    riskTags: ['竞品对标失焦'],
    tagConfidence: 0.91,
    isHighConfidenceSample: true,
    contentRole: '对比型',
    valueLevel: '中',
    valueFlags: ['高互动', '高证据'],
    valueSummary: '适合外部传播阶段拉升认知，但用户更关注结论是否和真实车主体验一致。',
    valueReasons: ['竞品比较框架清晰', '评论区会持续追加对标问题', '可作为销售话术辅助素材'],
    riskSummary: '若横评结论过于偏向单一维度，容易被评论区质疑“选择性比较”。',
    isCoreContent: false,
    commentProfile: {
      highConfidenceRate: 63,
      ownerRate: 18,
      testDriveRate: 24,
      prospectRate: 35,
      doubtRate: 24,
      approvalRate: 47,
      positiveRate: 43,
      negativeRate: 18,
      stageTop: '准车主',
      attitudeTop: '认可',
      mindsetDistribution: [
        { label: '竞品对照', value: 57 },
        { label: '品牌偏好', value: 26 },
        { label: '参数党', value: 17 },
      ],
      emotionDistribution: [
        { label: '正向', value: 43 },
        { label: '中性', value: 39 },
        { label: '负向', value: 18 },
      ],
      attitudeDistribution: [
        { label: '认可', value: 47 },
        { label: '中立', value: 29 },
        { label: '质疑', value: 24 },
      ],
      stageDistribution: [
        { label: '准车主', value: 35 },
        { label: '试驾', value: 24 },
        { label: '车主', value: 18 },
        { label: '围观', value: 23 },
      ],
    },
    representativeComments: [
      { label: '高点赞评论', text: '横评最有用的不是吹谁强，而是把每台车的短板讲清楚。' },
      { label: '高证据评论', text: '如果语音识别能把方言样本也加进去，横评结论会更完整。' },
      { label: '高意向评论', text: '我就是在 S9 和竞品之间摇摆，这种对比比单车测评更好用。' },
    ],
    relatedContents: [
      { id: 'CNT-1003', title: 'S9首批提车作业：空间和智能座舱是亮点', reason: '同车型车主体验，补充真实口碑' },
    ],
  },
  {
    id: 'CNT-1005',
    eventId: 'EVT-2026-005',
    eventName: '春季品牌联名传播',
    title: '联名活动首周传播复盘：短视频平台声量最高',
    summary: '传播波峰集中在活动当天晚间，KOL二创内容贡献明显，是品牌传播节奏复盘的主样本。',
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
    evidenceTags: ['传播峰值曲线', '平台拆解'],
    contentTags: ['联名活动', '传播复盘'],
    riskTags: ['话题衰减'],
    tagConfidence: 0.84,
    isHighConfidenceSample: false,
    contentRole: '观点型',
    valueLevel: '中',
    valueFlags: ['高互动'],
    valueSummary: '更偏传播复盘内容，适合品牌团队快速判断首周热度和二创放大效果。',
    valueReasons: ['平台峰值节奏清晰', '适合复盘投放与内容分发', '二创内容贡献被量化'],
    riskSummary: '需要警惕声量高但记忆点短的问题，后续内容接力不足会导致热度回落过快。',
    isCoreContent: false,
    commentProfile: {
      highConfidenceRate: 41,
      ownerRate: 6,
      testDriveRate: 4,
      prospectRate: 18,
      doubtRate: 12,
      approvalRate: 49,
      positiveRate: 54,
      negativeRate: 9,
      stageTop: '围观',
      attitudeTop: '认可',
      mindsetDistribution: [
        { label: '娱乐参与', value: 62 },
        { label: '品牌认同', value: 24 },
        { label: '路人围观', value: 14 },
      ],
      emotionDistribution: [
        { label: '正向', value: 54 },
        { label: '中性', value: 37 },
        { label: '负向', value: 9 },
      ],
      attitudeDistribution: [
        { label: '认可', value: 49 },
        { label: '中立', value: 39 },
        { label: '质疑', value: 12 },
      ],
      stageDistribution: [
        { label: '围观', value: 72 },
        { label: '准车主', value: 18 },
        { label: '车主', value: 6 },
        { label: '试驾', value: 4 },
      ],
    },
    representativeComments: [
      { label: '高点赞评论', text: '活动本身很会玩，但更重要的是联名后品牌到底被记住了什么。' },
      { label: '高传播评论', text: '二创素材包如果再开放一点，短视频扩散可能还能多跑两轮。' },
      { label: '中立评论', text: '声量不错，接下来就看能不能接到门店或试驾转化。' },
    ],
    relatedContents: [],
  },
  {
    id: 'CNT-1006',
    eventId: 'EVT-2026-001',
    eventName: '智行SUV冬测续航争议',
    title: '直播切片：极寒环境补能效率实录',
    summary: '记录补能排队、充电桩功率波动与实际等待时长，补足冬测争议中的补能体验证据。',
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
    issueTags: ['排队时间', '功率波动'],
    evidenceTags: ['现场录像', '等待时长'],
    contentTags: ['极寒补能', '直播切片'],
    riskTags: ['服务体验外溢'],
    tagConfidence: 0.9,
    isHighConfidenceSample: true,
    contentRole: '证据型',
    valueLevel: '高',
    valueFlags: ['高证据', '高争议'],
    valueSummary: '把抽象的“补能焦虑”具象成排队和功率波动，是争议升级的重要辅助内容。',
    valueReasons: ['视频证据直观', '评论区大量补充真实排队经历', '与冬测争议形成跨命题连接'],
    riskSummary: '容易把单点充电站问题外推为品牌级服务问题，需要结合区域覆盖解释。',
    isCoreContent: false,
    commentProfile: {
      highConfidenceRate: 69,
      ownerRate: 29,
      testDriveRate: 14,
      prospectRate: 24,
      doubtRate: 43,
      approvalRate: 26,
      positiveRate: 19,
      negativeRate: 48,
      stageTop: '车主',
      attitudeTop: '质疑',
      mindsetDistribution: [
        { label: '效率焦虑', value: 49 },
        { label: '理性比较', value: 33 },
        { label: '情绪吐槽', value: 18 },
      ],
      emotionDistribution: [
        { label: '负向', value: 48 },
        { label: '中性', value: 33 },
        { label: '正向', value: 19 },
      ],
      attitudeDistribution: [
        { label: '质疑', value: 43 },
        { label: '认可', value: 26 },
        { label: '中立', value: 31 },
      ],
      stageDistribution: [
        { label: '车主', value: 29 },
        { label: '准车主', value: 24 },
        { label: '围观', value: 33 },
        { label: '试驾', value: 14 },
      ],
    },
    representativeComments: [
      { label: '高点赞评论', text: '能不能充上比跑多远更致命，假期和冬天排队才是用户最直接的体验。' },
      { label: '高置信评论', text: '我在哈尔滨服务区也遇到过功率上不去的问题，等位时间比充电时间还长。' },
      { label: '强情绪评论', text: '买电车最怕补能像开盲盒，冬天更是加倍。' },
    ],
    relatedContents: [
      { id: 'CNT-1001', title: 'X7冬测续航实测：高速+低温工况是否达标', reason: '同事件核心内容，补能维度延展' },
      { id: 'CNT-1002', title: '车主长帖：低温通勤一周真实电耗记录', reason: '真实车主体验形成互证' },
    ],
  },
];

export const platformOptions = ['全部平台', 'B站', '汽车论坛', '小红书', '懂车帝', '抖音', '微博'] as const;
export const contentTypeOptions = ['全部类型', '测评', '对比', '提车作业', '资讯', '讨论'] as const;
export const authorTypeOptions = ['全部作者', 'KOL', 'KOC', '普通用户', '媒体'] as const;
export const publishRangeOptions = ['全部时间', '近7天', '近30天', '近90天'] as const;
export const interactionRangeOptions = ['全部互动', '500+', '1,000+', '3,000+', '5,000+'] as const;
export const tagFilterOptions = ['全部标签', '命题', '问题', '证据', '风险'] as const;
export const confidenceOptions = ['全部样本', '高置信样本'] as const;
export const valueFilterOptions = ['全部价值', '高互动', '高证据', '高争议', '高意向', '核心内容'] as const;
export const commentFocusOptions = ['全部评论结构', '车主占比高', '试驾占比高', '质疑占比高', '认可占比高', '高置信占比高', '负向占比高'] as const;
export const contentSortOptions = [
  { value: 'engagement', label: '按综合互动量' },
  { value: 'comments', label: '按评论数' },
  { value: 'highConfidence', label: '按高置信评论占比' },
  { value: 'ownerRate', label: '按车主评论占比' },
  { value: 'doubtRate', label: '按质疑占比' },
  { value: 'positiveRate', label: '按正向占比' },
  { value: 'publishedAt', label: '按发布时间' },
  { value: 'valueLevel', label: '按价值等级' },
] as const;
