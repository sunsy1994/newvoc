import html
import json
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd


ECHARTS_ASSET_PATH = Path(__file__).with_name('assets') / 'echarts.min.js'


@lru_cache(maxsize=1)
def _echarts_source():
    return ECHARTS_ASSET_PATH.read_text(encoding='utf-8')


STYLE_PRESETS = {
    'ft': {
        'style_name': 'Financial Times',
        'page_bg': '#FFF1E5',
        'body_bg': '#FFF1E5',
        'text': '#33302E',
        'muted': '#6B6B6B',
        'brand': '#0F5499',
        'assist': '#996600',
        'positive': '#09823A',
        'danger': '#CC0000',
        'border': '#E0D3C3',
        'table_header': '#FFF7F0',
        'table_even': '#FFFCF8',
        'panel_bg': '#FFFFFF',
        'insight_bg': '#FFFFFF',
        'cover_bg': '#F6EBDD',
        'metric_bg': '#FFF7F0',
        'grid': '#F5EDE3',
        'font_body': "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        'font_heading': "Georgia, 'Times New Roman', serif",
    },
    'mckinsey': {
        'style_name': 'McKinsey Consulting',
        'page_bg': '#FFFFFF',
        'body_bg': '#FFFFFF',
        'text': '#1A1A2E',
        'muted': '#666680',
        'brand': '#003366',
        'assist': '#4472C4',
        'positive': '#70AD47',
        'danger': '#ED7D31',
        'border': '#D6D6D6',
        'table_header': '#F7F8FA',
        'table_even': '#FBFCFE',
        'panel_bg': '#FFFFFF',
        'insight_bg': '#F4F6F9',
        'cover_bg': '#EEF2F7',
        'metric_bg': '#F4F6F9',
        'grid': '#E7EBF0',
        'font_body': "'Helvetica Neue', Arial, sans-serif",
        'font_heading': "'Helvetica Neue', Arial, sans-serif",
    },
}


def apply_aliases(df, alias_map):
    rename_dict = {}
    for target, aliases in alias_map.items():
        if target in df.columns:
            continue
        for alias in aliases:
            if alias in df.columns:
                rename_dict[alias] = target
                break
    if rename_dict:
        df = df.rename(columns=rename_dict)
    return df


def parse_metric(value):
    if pd.isna(value):
        return 0
    text = str(value).strip()
    if not text:
        return 0
    match = re.search(r'\d+(?:\.\d+)?', text.replace(',', ''))
    if not match:
        return 0
    number = float(match.group())
    return int(number) if number.is_integer() else number


def format_int(value):
    return f'{int(value):,}'


def safe_html(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ''
    return html.escape(str(value), quote=True)


def script_safe_json(value):
    return (
        json.dumps(value, ensure_ascii=False)
        .replace('&', '\\u0026')
        .replace('<', '\\u003c')
        .replace('>', '\\u003e')
        .replace('\u2028', '\\u2028')
        .replace('\u2029', '\\u2029')
    )


def strip_inline_markdown(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', str(text))
    return text.replace('`', '').strip()


def normalize_brand(value):
    text = str(value).strip() if not pd.isna(value) else ''
    return text or '未标注品牌'


def extract_tags(text):
    if pd.isna(text):
        return []
    return [tag.strip() for tag in str(text).split() if tag.strip().startswith('#')]


def extract_keywords(text):
    if pd.isna(text):
        return []
    raw = re.findall(r'[\u4e00-\u9fffA-Za-z0-9]{2,}', str(text))
    stopwords = {
        '上汽大众', '大众', '视频', '作品', '我们', '你们', '他们', '相关', '发布',
        '一个', '这次', '这个', '那个', '可以', '已经', '还是', '以及', '因为',
        '什么', '怎么', '进行', '品牌', '官方', '账号', '经销商', '内容', '本周',
    }
    return [word for word in raw if word not in stopwords]


TOPIC_RULES = [
    ('新车上市 / 预售', ['预售', '上市', '登场', '亮相', '新车', '首发', '发布会']),
    ('产品卖点传播', ['旗舰', '动力', '底气', '品质', '满级', '性能', '科技', '配置']),
    ('智驾 / 智能化', ['智驾', '辅助', '智能', '智舱', '泊车', '驾驶', '循迹', '窄道']),
    ('空间 / 家庭出行', ['大6座', '家庭', '空间', '出行', '舒适', '全家', '陪伴']),
    ('长测 / 试驾 / 远征', ['长测', '远征', '万里长歌', '试驾', '穿越', '雪山', '崇左']),
    ('品牌活动 / 发布会', ['发布会', '全新以赴', '焕新', '活动', '车展', '首钢园']),
    ('用户互动 / UGC 共创', ['春日明信片', '摄影师', '共创', '互动', '征集', '带我寻春天']),
    ('经销商促销 / 门店活动', ['到店', '试驾有礼', '优惠', '购车', '门店', '销售', '置换']),
    ('售后 / 服务 / 交付', ['售后', '服务', '交付', '保障', 'wecare']),
]

POSITIVE_WORDS = {'喜欢', '好看', '不错', '可以', '支持', '期待', '高级', '真香', '种草', '稳', '帅', '想买', '给力'}
NEGATIVE_WORDS = {'贵', '烦', '一般', '吐槽', '失望', '不好', '差', '问题', '拉胯', '不行', '劝退'}


def infer_brand_from_content(df, fallback='未标注品牌'):
    text_pool = []
    for col in ['品牌', '作者', '标题', '话题标签']:
        if col in df.columns:
            text_pool.extend(df[col].dropna().astype(str).tolist())
    merged = ' '.join(text_pool)
    for candidate in ['上汽大众', '一汽大众', '比亚迪', '特斯拉', '理想', '问界', '蔚来', '小鹏']:
        if candidate in merged:
            return candidate
    return fallback


def classify_topic(title, tags=''):
    text = f'{title or ""} {tags or ""}'
    for topic, keywords in TOPIC_RULES:
        if any(keyword in text for keyword in keywords):
            return topic
    return '其他 / 待补充'


METRIC_COLUMNS = ['互动点赞数', '评论数', '收藏数', '分享数']


def _recompute_total_engagement(df):
    for col in METRIC_COLUMNS:
        if col not in df.columns:
            df[col] = 0
        df[col] = df[col].map(parse_metric)
    df['总互动量'] = sum((df[col] for col in METRIC_COLUMNS), start=0)
    return df


def _rank_top_works(df):
    ranked = df.copy()
    if '发布时间_dt' not in ranked.columns:
        ranked['发布时间_dt'] = pd.to_datetime(ranked.get('发布时间'), errors='coerce')
    for col in ['作品ID', '标题', '作者']:
        if col not in ranked.columns:
            ranked[col] = ''
    return ranked.sort_values(
        ['品牌', '总互动量', '互动点赞数', '评论数', '发布时间_dt', '作品ID', '标题', '作者'],
        ascending=[True, False, False, False, False, True, True, True],
        na_position='last',
        kind='mergesort',
    )


def prepare_works_df(path, default_brand='未标注品牌'):
    df = pd.read_excel(path)
    df = apply_aliases(df, {
        '账号类型': ['作者类型'],
        '互动点赞数': ['点赞数'],
        '总互动量': ['互动量综合'],
        '封面图路径': ['封面图URL', '封面URL'],
        '作品ID': ['work_id', '作品id'],
    })
    df = _recompute_total_engagement(df)
    if '品牌' not in df.columns:
        df['品牌'] = infer_brand_from_content(df, fallback=default_brand)
    df['品牌'] = df['品牌'].map(normalize_brand)
    df['发布时间_dt'] = pd.to_datetime(df.get('发布时间'), errors='coerce')
    df['发布日'] = df['发布时间_dt'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else '未知日期')
    if '账号类型' not in df.columns:
        df['账号类型'] = ''
    if '是否官方号' not in df.columns:
        df['是否官方号'] = df['账号类型'].astype(str).apply(lambda x: '是' if '官方' in x else '否')
    df['主题分类'] = df.apply(lambda row: classify_topic(row.get('标题', ''), row.get('话题标签', '')), axis=1)
    return df


def prepare_top_hot_df(works_df, top_hot_path=None, top_n=3, default_brand='未标注品牌'):
    if top_hot_path and Path(top_hot_path).exists():
        top_df = pd.read_excel(top_hot_path)
        top_df = apply_aliases(top_df, {
            '账号类型': ['作者类型'],
            '互动点赞数': ['点赞数'],
            '总互动量': ['互动量综合'],
            '封面图路径': ['封面图片'],
            '作品ID': ['work_id', '作品id'],
        })
        top_df = _recompute_total_engagement(top_df)
        if '品牌' not in top_df.columns:
            top_df['品牌'] = infer_brand_from_content(top_df, fallback=default_brand)
        top_df['品牌'] = top_df['品牌'].map(normalize_brand)
        top_df['发布时间_dt'] = pd.to_datetime(top_df.get('发布时间'), errors='coerce')
        if '主题分类' not in top_df.columns:
            top_df['主题分类'] = top_df.apply(lambda row: classify_topic(row.get('标题', ''), row.get('话题标签', '')), axis=1)
        return _rank_top_works(top_df).reset_index(drop=True)

    fallback = _rank_top_works(works_df)
    return fallback.groupby('品牌', dropna=False, group_keys=False).head(top_n).reset_index(drop=True)


def prepare_comments_df(path=None, default_brand='未标注品牌'):
    if not path or not Path(path).exists():
        return pd.DataFrame(columns=['品牌', '标题', '评论', '昵称', '地址', '日期'])
    df = pd.read_excel(path)
    df = apply_aliases(df, {
        '评论': ['评论内容'],
        '昵称': ['评论用户', '用户名'],
    })
    if '品牌' not in df.columns:
        df['品牌'] = infer_brand_from_content(df, fallback=default_brand)
    df['品牌'] = df['品牌'].map(normalize_brand)
    return df


def summarize_hot_topics(brand_df, hotlist_df=None, top_n=6):
    tag_counter = Counter()
    keyword_counter = Counter()
    tag_interactions = Counter()

    for _, row in brand_df.iterrows():
        interaction = parse_metric(row.get('总互动量', 0))
        for tag in extract_tags(row.get('话题标签')):
            tag_counter[tag] += 1
            tag_interactions[tag] += interaction
        for word in extract_keywords(row.get('标题')):
            keyword_counter[word] += 1

    topics = []
    for tag, count in tag_counter.most_common(top_n):
        topics.append({
            'name': tag,
            'evidence': '原始标签',
            'works': count,
            'interactions': tag_interactions[tag],
            'topic_type': '高频出现' if count >= 3 else '低频出现',
        })

    if len(topics) < top_n:
        for word, count in keyword_counter.most_common(top_n * 2):
            if any(word in item['name'] for item in topics):
                continue
            topics.append({
                'name': word,
                'evidence': '标题关键词',
                'works': count,
                'interactions': 0,
                'topic_type': '低频出现',
            })
            if len(topics) >= top_n:
                break

    if hotlist_df is not None and not hotlist_df.empty:
        related_words = []
        for col in hotlist_df.columns:
            related_words.extend(hotlist_df[col].dropna().astype(str).tolist())
        for item in topics:
            if any(item['name'].replace('#', '') in word for word in related_words):
                item['topic_type'] = '热榜相关'

    return topics[:top_n]


def summarize_comments(comment_df):
    if comment_df.empty:
        return {
            'count': 0,
            'keywords': [],
            'samples': [],
        }

    keyword_counter = Counter()
    sentiment_counter = Counter()
    for text in comment_df['评论'].dropna().astype(str):
        lowered = text.lower()
        positive_hits = sum(word in lowered for word in POSITIVE_WORDS)
        negative_hits = sum(word in lowered for word in NEGATIVE_WORDS)
        if positive_hits > negative_hits:
            sentiment_counter['正向'] += 1
        elif negative_hits > positive_hits:
            sentiment_counter['负向'] += 1
        else:
            sentiment_counter['中性'] += 1
        for word in extract_keywords(text):
            keyword_counter[word] += 1

    sample_df = comment_df.copy()
    if '昵称' not in sample_df.columns:
        sample_df['昵称'] = '用户'
    if '评论' not in sample_df.columns:
        sample_df['评论'] = ''
    samples = sample_df[['昵称', '评论']].head(5).to_dict('records')
    return {
        'count': len(comment_df),
        'keywords': keyword_counter.most_common(8),
        'samples': samples,
        'sentiment': sentiment_counter,
    }


def format_sentiment_ratio(sentiment_counter):
    total = sum(sentiment_counter.values())
    if total == 0:
        return {'正向': 0, '中性': 0, '负向': 0}
    return {
        '正向': round(sentiment_counter.get('正向', 0) * 100 / total, 1),
        '中性': round(sentiment_counter.get('中性', 0) * 100 / total, 1),
        '负向': round(sentiment_counter.get('负向', 0) * 100 / total, 1),
    }


def summarize_topic_categories(brand_df):
    topic_df = (
        brand_df.groupby('主题分类', dropna=False)
        .agg(作品数=('标题', 'count'), 累计互动量=('总互动量', 'sum'))
        .reset_index()
        .sort_values(['作品数', '累计互动量'], ascending=[False, False])
    )
    return topic_df


def summarize_official_dealer_relation(brand_df, hotlist_df=None):
    if '是否官方号' not in brand_df.columns:
        return {
            'status': '信息不足',
            'official_topics': [],
            'dealer_topics': [],
            'overlap_topics': [],
            'message': '未识别到官方号字段，暂无法判断官方与经销商承接关系。',
        }

    official_df = brand_df[brand_df['是否官方号'].astype(str) == '是']
    dealer_df = brand_df[brand_df['是否官方号'].astype(str) != '是']
    official_topics = official_df['主题分类'].dropna().astype(str).tolist()
    dealer_topics = dealer_df['主题分类'].dropna().astype(str).tolist()
    overlap = [topic for topic in set(official_topics) if topic in set(dealer_topics)]

    hotlist_words = []
    if hotlist_df is not None and not hotlist_df.empty:
        for col in hotlist_df.columns:
            hotlist_words.extend(hotlist_df[col].dropna().astype(str).tolist())
    hotspot_match = any(topic.replace(' / ', '')[:4] in ''.join(hotlist_words) for topic in overlap)

    if overlap and hotspot_match:
        status = '强关联'
    elif overlap:
        status = '弱关联'
    else:
        status = '未见明显关联'

    if status == '强关联':
        message = '官方账号已经释放明确主题，经销商内容也在同步承接，且与热榜话题存在交集。'
    elif status == '弱关联':
        message = '官方与经销商在主题上已有重叠，但热榜承接还不算集中，更像局部跟进。'
    else:
        message = '当前经销商内容与官方传播主线重叠不多，更多在各自发挥。'

    return {
        'status': status,
        'official_topics': Counter(official_topics).most_common(3),
        'dealer_topics': Counter(dealer_topics).most_common(3),
        'overlap_topics': overlap[:5],
        'message': message,
    }


def build_official_dealer_sankey(brand_df):
    if '是否官方号' not in brand_df.columns:
        return {'nodes': [], 'links': [], 'highlight_topic': '', 'message': '缺少官方号字段，无法绘制桑基图。'}

    official_df = brand_df[brand_df['是否官方号'].astype(str) == '是'].copy()
    dealer_df = brand_df[brand_df['是否官方号'].astype(str) != '是'].copy()
    if official_df.empty or dealer_df.empty:
        return {'nodes': [], 'links': [], 'highlight_topic': '', 'message': '官方或经销商样本不足，暂无法形成承接流向。'}

    official_topics = Counter()
    official_topic_avg = {}
    topic_dealer_pairs = Counter()
    dealer_effect = {}

    brand_avg_interaction = dealer_df['总互动量'].mean() if not dealer_df.empty else 0

    for _, row in official_df.iterrows():
        topics = extract_tags(row.get('话题标签'))
        if not topics:
            topics = [row.get('主题分类', '其他 / 待补充')]
        interaction = parse_metric(row.get('总互动量', 0)) or 1
        for topic in topics:
            official_topics[topic] += interaction

    for topic in list(official_topics.keys()):
        official_topic_avg[topic] = official_df[
            official_df['话题标签'].astype(str).str.contains(re.escape(topic), na=False)
        ]['总互动量'].mean()
        if pd.isna(official_topic_avg[topic]):
            official_topic_avg[topic] = 0

    for _, row in dealer_df.iterrows():
        dealer = str(row.get('作者', '未知经销商')).strip() or '未知经销商'
        topics = extract_tags(row.get('话题标签'))
        if not topics:
            topics = [row.get('主题分类', '其他 / 待补充')]
        interaction = parse_metric(row.get('总互动量', 0)) or 1

        for topic in topics:
            if topic not in official_topics:
                continue
            topic_dealer_pairs[(topic, dealer)] += interaction
            if dealer not in dealer_effect:
                dealer_effect[dealer] = {'values': [], 'topics': set()}
            dealer_effect[dealer]['values'].append(interaction)
            dealer_effect[dealer]['topics'].add(topic)

    if not topic_dealer_pairs:
        return {'nodes': [], 'links': [], 'highlight_topic': '', 'message': '暂无明显的官方话题被经销商承接，无法形成有效流向。', 'dealer_summary': []}

    top_topics = [topic for topic, _ in official_topics.most_common(5)]
    filtered_pairs = {k: v for k, v in topic_dealer_pairs.items() if k[0] in top_topics}
    dealer_totals_for_chart = Counter()
    for (_, dealer), value in filtered_pairs.items():
        dealer_totals_for_chart[dealer] += value
    top_dealers_for_chart = {dealer for dealer, _ in dealer_totals_for_chart.most_common(8)}
    filtered_pairs = {
        pair: value
        for pair, value in filtered_pairs.items()
        if pair[1] in top_dealers_for_chart
    }

    nodes = []
    links = []
    topic_names = set()
    dealer_names = set()

    nodes.append({
        'name': '官方账号',
        'depth': 0,
        'itemStyle': {'color': '#0F5499'}
    })

    for topic in top_topics:
        if any(pair_topic == topic for pair_topic, _ in filtered_pairs.keys()):
            topic_names.add(topic)
            nodes.append({
                'name': topic,
                'depth': 1,
                'itemStyle': {'color': '#996600'}
            })

    dealer_summary = []
    effect_totals = Counter()
    for dealer, info in dealer_effect.items():
        avg_value = sum(info['values']) / len(info['values']) if info['values'] else 0
        if brand_avg_interaction <= 0:
            effect = '正常承接'
            color = '#8C7E72'
        elif avg_value >= brand_avg_interaction * 1.15:
            effect = '正向放大'
            color = '#09823A'
        elif avg_value <= brand_avg_interaction * 0.85:
            effect = '反向/低效'
            color = '#CC0000'
        else:
            effect = '正常承接'
            color = '#8C7E72'
        effect_totals[effect] += sum(info['values'])
        dealer_summary.append({
            'dealer': dealer,
            'effect': effect,
            'avg_interaction': round(avg_value, 1),
            'topic_count': len(info['topics']),
            'color': color,
            'total_interaction': round(sum(info['values']), 1),
        })

    dealer_color_map = {item['dealer']: item['color'] for item in dealer_summary}
    chart_dealers = sorted(top_dealers_for_chart, key=lambda name: dealer_totals_for_chart.get(name, 0), reverse=True)
    for dealer in chart_dealers:
        nodes.append({
            'name': dealer,
            'depth': 2,
            'itemStyle': {'color': dealer_color_map.get(dealer, '#8C7E72')}
        })

    for topic in top_topics:
        if topic not in topic_names:
            continue
        links.append({
            'source': '官方账号',
            'target': topic,
            'value': int(official_topics.get(topic, 0)),
        })

    for (topic, dealer), value in sorted(filtered_pairs.items(), key=lambda x: x[1], reverse=True):
        links.append({
            'source': topic,
            'target': dealer,
            'value': int(value),
        })

    highlight_topic = top_topics[0] if top_topics else ''
    strongest_dealer = max(dealer_summary, key=lambda x: x['avg_interaction']) if dealer_summary else None
    if highlight_topic and strongest_dealer:
        message = (
            f'本周官方最强发起话题是「{highlight_topic}」，经销商承接后，'
            f'「{strongest_dealer["dealer"]}」表现最强，归为「{strongest_dealer["effect"]}」。'
        )
    else:
        message = '当前已识别到官方发起与经销商承接链路，但尚不足以形成更明确的效果判断。'

    dealer_summary = sorted(dealer_summary, key=lambda x: x['avg_interaction'], reverse=True)
    return {
        'nodes': nodes,
        'links': links,
        'highlight_topic': highlight_topic,
        'message': message,
        'dealer_summary': dealer_summary[:5],
    }


def build_brand_insights(brand_df, top_df, topic_summary, video_insight=None):
    total_works = len(brand_df)
    total_interactions = int(brand_df['总互动量'].sum())
    avg_interactions = round(total_interactions / total_works, 1) if total_works else 0
    official_ratio = 0
    if '是否官方号' in brand_df.columns and total_works:
        official_ratio = round((brand_df['是否官方号'].astype(str) == '是').mean() * 100, 1)

    insights = [
        f'本周样本共覆盖 {total_works} 条作品，总互动量 {format_int(total_interactions)}，平均单条互动 {avg_interactions}。',
        f'官方账号内容占比约 {official_ratio}% ，可用于直接观察品牌官方传播动作。',
    ]
    if not top_df.empty:
        hottest = top_df.iloc[0]
        insights.append(
            f'本周最热作品来自「{hottest.get("作者", "未知账号")}」，总互动量 {format_int(hottest.get("总互动量", 0))}，发布时间为 {hottest.get("发布时间", "未知时间")}。'
        )
    if topic_summary:
        insights.append(
            f'当前最强势的话题集中在「{topic_summary[0]["name"]}」等方向，说明品牌正在强化相关传播主线。'
        )
    if video_insight:
        insights.append(
            f'已补充「{video_insight.get("source_name", "视频及评论总结.md")}」中的视频内容与评论摘要，用于补足原始作品表缺少的评论语义层信息。'
        )
    return insights


def extract_md_section(text, heading):
    pattern = rf'###\s+{re.escape(heading)}\s*\n(.*?)(?=\n###\s+|\n##\s+|\Z)'
    match = re.search(pattern, text, flags=re.S)
    return match.group(1).strip() if match else ''


def parse_video_insights(path=None):
    if not path:
        return None
    md_path = Path(path)
    if not md_path.exists():
        return None
    text = md_path.read_text(encoding='utf-8')

    def field(name):
        match = re.search(rf'-\s+\*\*{re.escape(name)}\*\*：(.+)', text)
        return match.group(1).strip() if match else ''

    sentiment = dict(re.findall(r'\*\*(正面|中性|负面)\*\*：([\d.]+%)', text))
    comments = []
    for line in text.splitlines():
        if not line.startswith('|') or set(line.strip()) <= {'|', '-', ' '}:
            continue
        parts = [part.strip() for part in line.strip('|').split('|')]
        if len(parts) >= 4 and parts[0] != '作者':
            comments.append({
                'author': parts[0],
                'comment': parts[1],
                'likes': parts[2],
                'feature': parts[3],
            })

    reply_match = re.search(r'####\s+三、作者.*?\n(.*?)(?=\n####\s+|\Z)', text, flags=re.S)
    reply_lines = []
    if reply_match:
        reply_lines = [
            strip_inline_markdown(re.sub(r'^\s*-\s*', '', line))
            for line in reply_match.group(1).splitlines()
            if line.strip().startswith('-')
        ]

    def bullet_lines(section):
        return [
            strip_inline_markdown(re.sub(r'^\s*-\s*', '', line))
            for line in section.splitlines()
            if line.strip().startswith('-')
        ]

    return {
        'source_name': md_path.name,
        'link': field('视频链接'),
        'title': field('标题'),
        'author': field('作者'),
        'publish_time': field('发布时间'),
        'intro': bullet_lines(extract_md_section(text, '视频介绍')),
        'key_points': bullet_lines(extract_md_section(text, '要点总结')),
        'sentiment': sentiment,
        'comments': comments,
        'reply_lines': reply_lines,
    }


def matches_video_insight(row, insight):
    if not insight:
        return False
    insight_link = str(insight.get('link') or '')
    row_link = str(row.get('视频链接', '') or '')
    if insight_link and (insight_link in row_link or row_link in insight_link):
        return True
    insight_title = str(insight.get('title') or '').strip('“”"')
    row_title = str(row.get('标题', '') or '').strip('“”"')
    return bool(insight_title and row_title and (insight_title[:24] in row_title or row_title[:24] in insight_title))


def render_video_insight_block(video_insight, mode='section'):
    if not video_insight:
        return ''
    title = safe_html(video_insight.get('title') or '未命名视频')
    link = safe_html(_http_url(video_insight.get('link')))
    author = safe_html(video_insight.get('author') or '未知作者')
    publish_time = safe_html(video_insight.get('publish_time') or '未知时间')
    source_name = safe_html(video_insight.get('source_name') or '视频及评论总结.md')
    sentiment = video_insight.get('sentiment') or {}
    intro_items = ''.join(f'<li>{safe_html(item)}</li>' for item in video_insight.get('intro', [])[:5])
    key_items = ''.join(f'<li>{safe_html(item)}</li>' for item in video_insight.get('key_points', [])[:5])
    comment_rows = ''.join(
        f"""
        <tr>
          <td>{safe_html(item.get('author'))}</td>
          <td>{safe_html(item.get('comment'))}</td>
          <td>{safe_html(item.get('likes'))}</td>
          <td>{safe_html(item.get('feature'))}</td>
        </tr>
        """
        for item in video_insight.get('comments', [])[:6]
    ) or '<tr><td colspan="4">暂无典型评论</td></tr>'
    reply_items = ''.join(f'<li>{safe_html(item)}</li>' for item in video_insight.get('reply_lines', [])[:5])
    href = f'<a href="{link}" target="_blank" rel="noreferrer">{link}</a>' if link else '未提供链接'
    sentiment_text = (
        f"正面 {safe_html(sentiment.get('正面', '未标注'))} / "
        f"中性 {safe_html(sentiment.get('中性', '未标注'))} / "
        f"负面 {safe_html(sentiment.get('负面', '未标注'))}"
    )
    compact_class = ' video-insight-compact' if mode == 'compact' else ''
    heading = '<h3>视频与评论洞察补充</h3>' if mode == 'compact' else '<h2>视频与评论洞察补充</h2>'
    return f"""
    <div class="video-insight{compact_class}">
      {heading}
      <p class="meta">来源：{source_name}。视频：{author} | {publish_time} | {href}</p>
      <h3>{title}</h3>
      <p><strong>评论情绪：</strong>{sentiment_text}</p>
      <div class="video-grid">
        <div>
          <h3>视频内容要点</h3>
          <ul>{intro_items or '<li>暂无视频介绍</li>'}</ul>
        </div>
        <div>
          <h3>时间线摘要</h3>
          <ul>{key_items or '<li>暂无时间线摘要</li>'}</ul>
        </div>
      </div>
      <table class="comment-table">
        <thead><tr><th>评论作者</th><th>评论内容</th><th>点赞</th><th>判断</th></tr></thead>
        <tbody>{comment_rows}</tbody>
      </table>
      <div class="reply-box">
        <strong>作者回复行为：</strong>
        <ul>{reply_items or '<li>暂无作者回复总结</li>'}</ul>
      </div>
    </div>
    """


def render_missing_video_insight_block():
    rows = ''.join(
        f'<dt>{label}</dt><dd>无</dd>'
        for label in ('视频介绍', '要点总结', '评论情绪', '评论关键词', '典型评论', '作者回复')
    )
    return f"""
    <div class="video-insight video-insight-compact">
      <h3>视频与评论洞察补充</h3>
      <dl class="insight-detail-list">{rows}</dl>
    </div>
    """


def build_html(
    brand: str,
    works_df: pd.DataFrame,
    top_df: pd.DataFrame,
    comments_df: pd.DataFrame,
    hot_topics: list[dict],
    output_name: str,
    *,
    style_key: str = 'mckinsey',
    video_insights: dict | None = None,
) -> str:
    brand_df = works_df
    style = STYLE_PRESETS.get(style_key, STYLE_PRESETS['mckinsey'])
    legacy_video_insight = (
        video_insights
        if video_insights and 'source_name' in video_insights
        else None
    )
    first_video_insight = legacy_video_insight or next(iter((video_insights or {}).values()), None)
    total_works = len(brand_df)
    total_interactions = int(brand_df['总互动量'].sum())
    avg_interactions = round(total_interactions / total_works, 1) if total_works else 0
    official_count = int((brand_df.get('是否官方号', '').astype(str) == '是').sum()) if '是否官方号' in brand_df.columns else 0

    author_summary = (
        brand_df.groupby('作者', dropna=False)
        .agg(作品数=('标题', 'count'), 总互动量=('总互动量', 'sum'))
        .reset_index()
        .sort_values(['总互动量', '作品数'], ascending=[False, False])
    )
    trend = (
        brand_df.groupby('发布日', dropna=False)
        .agg(作品数=('标题', 'count'), 总互动量=('总互动量', 'sum'))
        .reset_index()
        .sort_values('发布日')
    )
    insights = build_brand_insights(brand_df, top_df, hot_topics, video_insight=first_video_insight)
    topic_category_df = summarize_topic_categories(brand_df)
    sankey_data = build_official_dealer_sankey(brand_df)
    sankey_height = max(460, min(760, 120 + len(sankey_data.get('nodes', [])) * 34))

    topic_rows = ''.join(
        f"""
        <tr>
          <td>{idx + 1}</td>
          <td>{safe_html(item['name'])}</td>
          <td>{safe_html(item['evidence'])}</td>
          <td>{item['works']}</td>
          <td>{format_int(item['interactions'])}</td>
          <td>{safe_html(item['topic_type'])}</td>
        </tr>
        """
        for idx, item in enumerate(hot_topics)
    ) or '<tr><td colspan="6">暂无足够话题数据</td></tr>'

    category_rows = ''.join(
        f"""
        <tr>
          <td>{idx + 1}</td>
          <td>{safe_html(row['主题分类'])}</td>
          <td>{int(row['作品数'])}</td>
          <td>{format_int(row['累计互动量'])}</td>
        </tr>
        """
        for idx, (_, row) in enumerate(topic_category_df.iterrows())
    ) or '<tr><td colspan="4">暂无主题分类数据</td></tr>'

    comment_summary_by_url = {}
    comment_summary_by_title = {}
    if not comments_df.empty and 'URL' in comments_df.columns:
        for url, group in comments_df.groupby('URL', dropna=False):
            comment_summary_by_url[url] = summarize_comments(group)
    if not comments_df.empty and '标题' in comments_df.columns:
        for title, group in comments_df.groupby('标题', dropna=False):
            comment_summary_by_title[str(title)] = summarize_comments(group)

    top_cards = []
    video_insight_matched = False
    for _, row in top_df.head(3).iterrows():
        comment_summary = comment_summary_by_url.get(row.get('视频链接'), {'count': 0, 'keywords': [], 'samples': []})
        if comment_summary['count'] == 0 and '标题' in row.index and not comments_df.empty:
            comment_summary = comment_summary_by_title.get(str(row.get('标题', '')), {'count': 0, 'keywords': [], 'samples': []})
        keyword_text = '、'.join([word for word, _ in comment_summary['keywords'][:5]]) or '暂无评论关键词'
        sentiment_ratio = format_sentiment_ratio(comment_summary.get('sentiment', Counter()))
        comment_sample_html = ''.join(
            f'<li><strong>{safe_html(sample.get("昵称"))}</strong>：{safe_html(sample.get("评论"))}</li>'
            for sample in comment_summary['samples'][:3]
        ) or '<li>暂无评论样本</li>'
        cover_path = _image_source(row.get('封面图路径', ''))
        cover_html = f'<img class="cover" src="{safe_html(cover_path)}" alt="封面图" />' if cover_path and not pd.isna(cover_path) else '<div class="cover cover-empty">暂无封面图</div>'
        topic_evidence = ' '.join(extract_tags(row.get('话题标签'))) or '暂无原始话题'
        insight_html = render_missing_video_insight_block()
        work_id = str(row.get('作品ID', ''))
        row_video_insight = (
            (video_insights or {}).get(work_id)
            if not legacy_video_insight
            else legacy_video_insight
        )
        if row_video_insight and (
            not legacy_video_insight or matches_video_insight(row, row_video_insight)
        ):
            video_insight_matched = True
            insight_html = render_video_insight_block(row_video_insight, mode='compact')

        top_cards.append(f"""
        <article class="hot-card" data-work-id="{safe_html(work_id)}">
          <div class="cover-wrap">{cover_html}</div>
          <div class="hot-body">
            <div class="hot-meta">{safe_html(row.get('作者', '未知账号'))} | {safe_html(row.get('发布时间', '未知时间'))}</div>
            <h3>{safe_html(row.get('标题', '')).replace(chr(10), '<br>')}</h3>
            <div class="metric-strip">
              <span>赞 {format_int(row.get('互动点赞数', 0))}</span>
              <span>评 {format_int(row.get('评论数', 0))}</span>
              <span>藏 {format_int(row.get('收藏数', 0))}</span>
              <span>转 {format_int(row.get('分享数', 0))}</span>
              <span class="strong">总互动 {format_int(row.get('总互动量', 0))}</span>
            </div>
            <p><strong>原始话题：</strong>{safe_html(topic_evidence)}</p>
            <p><strong>主题分类：</strong>{safe_html(row.get('主题分类', '其他 / 待补充'))}</p>
            <p><strong>评论关键词：</strong>{safe_html(keyword_text)}</p>
            <p><strong>评论情绪：</strong>正向 {sentiment_ratio['正向']}% / 中性 {sentiment_ratio['中性']}% / 负向 {sentiment_ratio['负向']}%</p>
            <ul class="comment-list">{comment_sample_html}</ul>
            {insight_html}
          </div>
        </article>
        """)

    standalone_video_insight_html = ''
    if legacy_video_insight and not video_insight_matched:
        standalone_video_insight_html = f"""
        <section class="section">
          {render_video_insight_block(legacy_video_insight)}
        </section>
        """

    report_data = {
        'author_labels': author_summary['作者'].fillna('未知账号').tolist(),
        'author_values': author_summary['总互动量'].astype(int).tolist(),
        'trend_labels': trend['发布日'].tolist(),
        'trend_works': trend['作品数'].astype(int).tolist(),
        'trend_interactions': trend['总互动量'].astype(int).tolist(),
        'topic_labels': [item['name'] for item in hot_topics],
        'topic_values': [int(item['works']) for item in hot_topics],
        'category_labels': topic_category_df['主题分类'].tolist(),
        'category_values': topic_category_df['作品数'].astype(int).tolist(),
        'sankey_nodes': sankey_data['nodes'],
        'sankey_links': sankey_data['links'],
    }
    report_json = script_safe_json(report_data)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{safe_html(brand)} 周度VOC竞品报告</title>
  <script>{_echarts_source()}</script>
  <style>
    html {{ background: {style['page_bg']}; }}
    body {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 40px 48px;
      background: {style['body_bg']};
      color: {style['text']};
      font-family: {style['font_body']};
      line-height: 1.6;
    }}
    .top-line {{ height: 4px; background: {style['brand']}; margin-bottom: 20px; }}
    h1, h2, h3 {{ font-family: {style['font_heading']}; margin: 0; }}
    h1 {{ font-size: 40px; margin-bottom: 12px; }}
    h2 {{ font-size: 24px; margin-bottom: 14px; }}
    .meta {{ color: {style['muted']}; margin: 0 0 28px; }}
    .section {{ margin-top: 40px; }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 16px;
    }}
    .card, .panel, .hot-card {{
      background: {style['panel_bg']};
      border: 1px solid {style['border']};
    }}
    .card {{ padding: 20px; }}
    .card .label {{ color: {style['muted']}; font-size: 13px; }}
    .card .value {{ font-size: 34px; font-family: {style['font_heading']}; margin-top: 8px; }}
    .insight-list {{ display: grid; gap: 12px; }}
    .insight {{ background: {style['insight_bg']}; border-left: 4px solid {style['brand']}; border: 1px solid {style['border']}; padding: 16px 18px; }}
    .grid {{ display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 20px; }}
    .panel {{ padding: 20px; }}
    .chart {{ width: 100%; height: 320px; }}
    .hot-list {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }}
    .hot-card {{ overflow: hidden; display: flex; flex-direction: column; }}
    .cover-wrap {{ background: {style['cover_bg']}; aspect-ratio: 4 / 5; display: flex; align-items: center; justify-content: center; max-height: 240px; }}
    .cover {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
    .cover-empty {{ color: {style['muted']}; font-size: 14px; }}
    .hot-body {{ padding: 12px 12px 14px; }}
    .hot-meta {{ color: {style['muted']}; font-size: 12px; margin-bottom: 6px; }}
    .hot-body h3 {{ font-size: 16px; line-height: 1.4; margin-bottom: 8px; display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; }}
    .hot-body p {{ margin: 6px 0; font-size: 13px; }}
    .metric-strip {{ display: flex; flex-wrap: wrap; gap: 4px 6px; margin: 8px 0; }}
    .metric-strip span {{ background: {style['metric_bg']}; border: 1px solid {style['border']}; padding: 4px 8px; font-size: 12px; }}
    .metric-strip .strong {{ color: {style['brand']}; font-weight: 600; }}
    .comment-list {{ margin: 6px 0 0; padding-left: 16px; }}
    .video-insight {{ background: {style['panel_bg']}; border: 1px solid {style['border']}; padding: 20px; }}
    .video-insight-compact {{ margin-top: 14px; padding: 14px; background: {style['insight_bg']}; }}
    .video-insight h3 {{ font-size: 16px; margin: 8px 0; }}
    .video-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
    .video-insight ul {{ margin: 6px 0 12px; padding-left: 18px; }}
    .insight-detail-list {{ display: grid; grid-template-columns: 96px 1fr; margin: 8px 0 0; }}
    .insight-detail-list dt, .insight-detail-list dd {{ margin: 0; padding: 6px 8px; border-bottom: 1px solid {style['grid']}; }}
    .insight-detail-list dt {{ color: {style['muted']}; font-weight: 600; }}
    .reply-box {{ margin-top: 12px; padding: 12px; background: {style['metric_bg']}; border: 1px solid {style['border']}; }}
    .comment-table {{ margin-top: 10px; }}
    table {{ width: 100%; border-collapse: collapse; background: {style['panel_bg']}; border: 1px solid {style['border']}; }}
    th, td {{ padding: 12px 10px; border-bottom: 1px solid {style['grid']}; text-align: left; font-size: 14px; vertical-align: top; }}
    th {{ background: {style['table_header']}; }}
    tr:nth-child(even) td {{ background: {style['table_even']}; }}
    a {{ color: {style['brand']}; text-decoration: none; }}
    .footer {{ color: {style['muted']}; font-size: 12px; margin-top: 24px; }}
    @media (max-width: 960px) {{
      body {{ padding: 24px; }}
      .cards, .grid, .hot-list {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="top-line"></div>
  <h1>{safe_html(brand)} 周度VOC竞品报告</h1>
  <p class="meta">本次使用 {style['style_name']} 风格。报告默认按品牌分别生成。当前输入文件：{safe_html(output_name)}。</p>

  <section class="section" aria-label="报告概览">
    <div class="cards">
      <div class="card"><div class="label">本周新增作品</div><div class="value">{format_int(total_works)}</div></div>
      <div class="card"><div class="label">总互动量</div><div class="value">{format_int(total_interactions)}</div></div>
      <div class="card"><div class="label">平均单条互动</div><div class="value">{avg_interactions}</div></div>
      <div class="card"><div class="label">官方账号作品数</div><div class="value">{format_int(official_count)}</div></div>
    </div>
  </section>

  <section class="section">
    <h2>核心发现</h2>
    <div class="insight-list">
      {''.join(f'<div class="insight">{safe_html(text)}</div>' for text in insights)}
    </div>
  </section>

  <section class="section">
    <h2>Top3 热门作品</h2>
    <div class="hot-list">
      {''.join(top_cards) or '<div class="insight">暂无热门作品数据</div>'}
    </div>
  </section>

  {standalone_video_insight_html}

  <section class="section grid">
    <div class="panel">
      <h2>账号互动贡献</h2>
      <div id="authorChart" class="chart"></div>
    </div>
    <div class="panel">
      <h2>发布时间与互动走势</h2>
      <div id="trendChart" class="chart"></div>
    </div>
  </section>

  <section class="section grid">
    <div class="panel">
      <h2>上周该品牌相关热门话题</h2>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>话题</th>
            <th>证据</th>
            <th>作品数</th>
            <th>累计互动量</th>
            <th>判断口径</th>
          </tr>
        </thead>
        <tbody>{topic_rows}</tbody>
      </table>
    </div>
    <div class="panel">
      <h2>热门话题热度分布</h2>
      <div id="topicChart" class="chart"></div>
    </div>
  </section>

  <section class="section grid">
    <div class="panel">
      <h2>话题分类分布</h2>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>主题分类</th>
            <th>作品数</th>
            <th>累计互动量</th>
          </tr>
        </thead>
        <tbody>{category_rows}</tbody>
      </table>
    </div>
    <div class="panel">
      <h2>重点经销商承接效果</h2>
      <div class="insight-list">
        {''.join(
            f'<div class="insight"><strong>{safe_html(item["dealer"])}</strong>：{safe_html(item["effect"])}，平均互动 {item["avg_interaction"]}，承接主题数 {item["topic_count"]}</div>'
            for item in sankey_data.get('dealer_summary', [])
        ) or '<div class="insight">暂无足够的经销商承接样本</div>'}
      </div>
    </div>
  </section>

  <section class="section">
    <div class="panel">
      <h2>官方发起 → 经销商承接 桑基图</h2>
      <p class="meta">优先按原视频话题建立关系，突出本周官方重点发起与经销商承接流向。{safe_html(sankey_data['message'])}</p>
      <div id="sankeyChart" class="chart" style="height: {sankey_height}px;"></div>
    </div>
  </section>

  <div class="footer">注：评论分析基于每品牌 Top3 热门作品的评论数据；如评论或封面未提供，报告会保留结构并提示缺失。</div>

  <script>
    const reportData = {report_json};
    const colorMain = '{style['brand']}';
    const colorAssist = '{style['assist']}';
    const colorGreen = '{style['positive']}';
    const wrapLabel = (text, step = 8) => {{
      const raw = String(text || '');
      if (raw.length <= step) return raw;
      const parts = [];
      for (let i = 0; i < raw.length; i += step) {{
        parts.push(raw.slice(i, i + step));
      }}
      return parts.join('\\n');
    }};

    const authorChart = echarts.init(document.getElementById('authorChart'));
    authorChart.setOption({{
      animation: false,
      grid: {{ left: 60, right: 20, top: 20, bottom: 40 }},
      xAxis: {{ type: 'value', splitLine: {{ lineStyle: {{ color: '{style['grid']}', type: 'dashed' }} }} }},
      yAxis: {{ type: 'category', data: reportData.author_labels, axisTick: {{ show: false }} }},
      series: [{{ type: 'bar', data: reportData.author_values, itemStyle: {{ color: colorMain }} }}],
      tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }} }}
    }});

    const trendChart = echarts.init(document.getElementById('trendChart'));
    trendChart.setOption({{
      animation: false,
      tooltip: {{ trigger: 'axis' }},
      legend: {{ data: ['作品数', '总互动量'] }},
      grid: {{ left: 48, right: 28, top: 40, bottom: 60 }},
      xAxis: {{ type: 'category', data: reportData.trend_labels, axisLabel: {{ rotate: 35 }} }},
      yAxis: [
        {{ type: 'value', name: '作品数', splitLine: {{ lineStyle: {{ color: '{style['grid']}', type: 'dashed' }} }} }},
        {{ type: 'value', name: '总互动量' }}
      ],
      series: [
        {{ name: '作品数', type: 'bar', data: reportData.trend_works, itemStyle: {{ color: colorAssist }} }},
        {{ name: '总互动量', type: 'line', yAxisIndex: 1, data: reportData.trend_interactions, itemStyle: {{ color: colorGreen }}, lineStyle: {{ width: 2 }} }}
      ]
    }});

    const topicChart = echarts.init(document.getElementById('topicChart'));
    topicChart.setOption({{
      animation: false,
      tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }} }},
      grid: {{ left: 80, right: 20, top: 20, bottom: 30 }},
      xAxis: {{ type: 'value', splitLine: {{ lineStyle: {{ color: '{style['grid']}', type: 'dashed' }} }} }},
      yAxis: {{ type: 'category', data: reportData.topic_labels, axisLabel: {{ width: 150, overflow: 'truncate' }} }},
      series: [{{ type: 'bar', data: reportData.topic_values, itemStyle: {{ color: colorGreen }} }}]
    }});

    const sankeyChart = echarts.init(document.getElementById('sankeyChart'));
    sankeyChart.setOption({{
      animation: false,
      tooltip: {{
        trigger: 'item',
        triggerOn: 'mousemove'
      }},
      series: [{{
        type: 'sankey',
        layout: 'none',
        left: 24,
        right: 120,
        top: 36,
        bottom: 36,
        nodeWidth: 14,
        nodeGap: 28,
        draggable: false,
        emphasis: {{ focus: 'adjacency' }},
        nodeAlign: 'justify',
        lineStyle: {{
          color: 'source',
          curveness: 0.24,
          opacity: 0.28
        }},
        label: {{
          color: '{style['text']}',
          fontSize: 12,
          lineHeight: 16,
          width: 150,
          overflow: 'truncate',
          formatter: function(params) {{
            return params.name;
          }}
        }},
        data: reportData.sankey_nodes,
        links: reportData.sankey_links
      }}]
    }});

    window.addEventListener('resize', () => {{
      authorChart.resize();
      trendChart.resize();
      topicChart.resize();
      sankeyChart.resize();
    }});
  </script>
</body>
</html>"""


def _http_url(value: Any) -> str:
    url = str(value or '').strip()
    return url if re.match(r'^https?://', url, flags=re.IGNORECASE) else ''


def _image_source(value: Any) -> str:
    source = str(value or '').strip()
    if not source:
        return ''
    if re.match(r'^[A-Za-z]:[\\/]', source):
        return source
    if re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:', source) and not re.match(
        r'^https?://',
        source,
        flags=re.IGNORECASE,
    ):
        return ''
    return source


def _record_row(record: dict[str, Any], brand_name: str) -> dict[str, Any]:
    return {
        '作品ID': str(record.get('work_id') or ''),
        '标题': str(record.get('title') or ''),
        '作者': str(record.get('author_name') or ''),
        '品牌': brand_name,
        '账号类型': str(record.get('account_type') or ''),
        '是否官方号': '是' if record.get('is_official') else '否',
        '发布时间': str(record.get('published_at') or ''),
        '话题标签': str(record.get('topic_tags') or ''),
        '视频链接': _http_url(record.get('video_url')),
        '封面图路径': str(record.get('cover_path') or ''),
        '互动点赞数': parse_metric(record.get('interaction_like_cnt')),
        '评论数': parse_metric(record.get('comment_cnt')),
        '收藏数': parse_metric(record.get('favorite_cnt')),
        '分享数': parse_metric(record.get('share_cnt')),
    }


def _record_video_insight(record: dict[str, Any], markdown: str) -> dict[str, Any]:
    parsed_sections: dict[str, list[str]] = {
        '视频介绍': [],
        '要点总结': [],
        '评论情绪': [],
        '评论关键词': [],
        '典型评论': [],
        '作者回复': [],
    }
    current = '视频介绍'
    for line in str(markdown or '').splitlines():
        heading = re.match(r'^\s*#{1,6}\s*(.+?)\s*#*\s*$', line)
        if heading and heading.group(1) in parsed_sections:
            current = heading.group(1)
            continue
        if line.strip():
            parsed_sections[current].append(re.sub(r'^\s*-\s*', '', line).strip())
    sentiment_text = ' '.join(parsed_sections['评论情绪'])
    return {
        'source_name': '数据库作品洞察',
        'link': _http_url(record.get('video_url')),
        'title': str(record.get('title') or ''),
        'author': str(record.get('author_name') or ''),
        'publish_time': str(record.get('published_at') or ''),
        'intro': parsed_sections['视频介绍'],
        'key_points': parsed_sections['要点总结'],
        'sentiment': {
            '正面': sentiment_text or '未标注',
            '中性': '未标注',
            '负面': '未标注',
        },
        'comments': [
            {
                'author': '用户',
                'comment': item,
                'likes': '',
                'feature': '典型评论',
            }
            for item in parsed_sections['典型评论']
        ],
        'reply_lines': parsed_sections['作者回复'],
    }


def generate_html_from_records(
    records: list[dict],
    *,
    brand_name: str,
    output_name: str,
    video_insights_by_work_id: dict[str, str],
) -> str:
    works_df = pd.DataFrame(_record_row(record, brand_name) for record in records)
    if works_df.empty:
        works_df = pd.DataFrame(
            columns=[
                '作品ID', '标题', '作者', '品牌', '账号类型', '是否官方号',
                '发布时间', '话题标签', '视频链接', '封面图路径',
                '互动点赞数', '评论数', '收藏数', '分享数',
            ]
        )
    works_df = _recompute_total_engagement(works_df)
    works_df['发布时间_dt'] = pd.to_datetime(works_df['发布时间'], errors='coerce')
    works_df['发布日'] = works_df['发布时间_dt'].apply(
        lambda value: value.strftime('%Y-%m-%d') if pd.notna(value) else '未知日期'
    )
    works_df['主题分类'] = works_df.apply(
        lambda row: classify_topic(row.get('标题', ''), row.get('话题标签', '')),
        axis=1,
    )
    top_df = prepare_top_hot_df(works_df)
    record_by_id = {str(record.get('work_id') or ''): record for record in records}
    parsed_insights = {
        work_id: _record_video_insight(record_by_id.get(work_id, {}), markdown)
        for work_id, markdown in video_insights_by_work_id.items()
        if str(markdown or '').strip() and str(markdown or '').strip() != '无'
    }
    return build_html(
        brand_name,
        works_df,
        top_df,
        pd.DataFrame(),
        summarize_hot_topics(works_df),
        output_name,
        style_key='mckinsey',
        video_insights=parsed_insights,
    )
