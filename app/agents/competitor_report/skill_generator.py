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


def build_topic_account_network(brand_df):
    topic_interactions = Counter()
    topic_works = Counter()
    edge_interactions = Counter()
    edge_works = Counter()
    account_types = {}
    tagged_rows = []

    for _, row in brand_df.iterrows():
        topics = list(
            dict.fromkeys(
                tag.lstrip('#').strip()
                for tag in extract_tags(row.get('话题标签'))
                if tag.lstrip('#').strip()
            )
        )
        if not topics:
            continue
        account = str(row.get('作者', '未知账号')).strip() or '未知账号'
        interaction = parse_metric(row.get('总互动量', 0))
        account_type_text = str(row.get('账号类型', ''))
        is_official = str(row.get('是否官方号', '')).strip() == '是' or '官方' in account_type_text
        if is_official:
            account_type = 'official'
        elif '经销' in account_type_text or '门店' in account_type_text:
            account_type = 'dealer'
        else:
            account_type = 'other'
        account_types[account] = account_type
        tagged_rows.append((account, topics, interaction))
        for topic in topics:
            topic_interactions[topic] += interaction
            topic_works[topic] += 1
            edge_interactions[(topic, account)] += interaction
            edge_works[(topic, account)] += 1

    if not tagged_rows:
        return {
            'topics': [],
            'accounts': [],
            'links': [],
            'message': '当前时间范围暂无可构建的话题传播网络。',
        }

    top_topics = [
        topic
        for topic, _ in sorted(
            topic_interactions.items(),
            key=lambda item: (-item[1], -topic_works[item[0]], item[0]),
        )[:10]
    ]
    top_topic_set = set(top_topics)
    account_interactions = Counter()
    account_works = Counter()
    for account, topics, interaction in tagged_rows:
        if top_topic_set.intersection(topics):
            account_interactions[account] += interaction
            account_works[account] += 1

    top_accounts = [
        account
        for account, _ in sorted(
            account_interactions.items(),
            key=lambda item: (-item[1], -account_works[item[0]], item[0]),
        )
    ]
    topics = [
        {
            'name': topic,
            'interaction_count': int(topic_interactions[topic]),
            'work_count': int(topic_works[topic]),
        }
        for topic in top_topics
    ]
    accounts = [
        {
            'name': account,
            'account_type': account_types.get(account, 'other'),
            'interaction_count': int(account_interactions[account]),
            'work_count': int(account_works[account]),
        }
        for account in top_accounts
    ]
    links = [
        {
            'topic': topic,
            'account': account,
            'work_count': int(edge_works[(topic, account)]),
            'interaction_count': int(edge_interactions[(topic, account)]),
        }
        for topic in top_topics
        for account in top_accounts
        if edge_works[(topic, account)] > 0
    ]
    return {
        'topics': topics,
        'accounts': accounts,
        'links': links,
        'message': f'展示累计互动量最高的 {len(topics)} 个话题及其全部 {len(accounts)} 个传播账号。',
    }


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
        'dealer_summary': dealer_summary,
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
    topic_network = build_topic_account_network(brand_df)
    sankey_data = build_official_dealer_sankey(brand_df)
    sankey_height = max(460, min(680, 180 + len(sankey_data.get('nodes', [])) * 24))

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
        keyword_text = '、'.join([word for word, _ in comment_summary['keywords'][:5]]) or '无'
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
        insight_keywords = (row_video_insight or {}).get('keywords') or []
        if insight_keywords:
            keyword_text = '、'.join(str(item) for item in insight_keywords[:5])
        if row_video_insight and (
            not legacy_video_insight or matches_video_insight(row, row_video_insight)
        ):
            video_insight_matched = True
            insight_html = render_video_insight_block(row_video_insight, mode='compact')
        selection_reason = str(row.get('入选判断') or '').strip()
        selection_reason_html = (
            '<p class="selection-reason"><strong>入选判断：</strong>'
            f'{safe_html(selection_reason)}</p>'
            if selection_reason
            else ''
        )

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
            {selection_reason_html}
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

    dealer_summary = sankey_data.get('dealer_summary', [])
    strongest_dealer = max(dealer_summary, key=lambda item: item['total_interaction'], default=None)
    widest_dealer = max(dealer_summary, key=lambda item: (item['topic_count'], item['total_interaction']), default=None)
    inefficient_dealer = next((item for item in dealer_summary if item['effect'] == '反向/低效'), None)
    dealer_digest = [
        (
            '最强承接账号',
            f'{strongest_dealer["dealer"]}，累计互动 {format_int(strongest_dealer["total_interaction"])}'
            if strongest_dealer else '暂无足够样本',
        ),
        (
            '覆盖话题最多账号',
            f'{widest_dealer["dealer"]}，覆盖 {widest_dealer["topic_count"]} 个话题'
            if widest_dealer else '暂无足够样本',
        ),
        (
            '低效承接账号',
            f'{inefficient_dealer["dealer"]}，平均互动 {inefficient_dealer["avg_interaction"]}'
            if inefficient_dealer else '暂无明确低效样本',
        ),
    ]

    report_data = {
        'total_interactions': total_interactions,
        'author_labels': author_summary['作者'].fillna('未知账号').head(8).tolist(),
        'author_values': author_summary['总互动量'].astype(int).head(8).tolist(),
        'trend_labels': trend['发布日'].tolist(),
        'trend_works': trend['作品数'].astype(int).tolist(),
        'trend_interactions': trend['总互动量'].astype(int).tolist(),
        'topic_network': topic_network,
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
    .lieflat-chart {{ display: block; overflow: visible; }}
    .chart-kicker {{ color: {style['muted']}; font-size: 12px; margin: -8px 0 12px; }}
    .chart-source {{ color: {style['muted']}; font-size: 10px; letter-spacing: .12em; margin-top: 8px; }}
    .thread-status {{ min-height: 32px; display: flex; align-items: center; gap: 10px; color: {style['muted']}; font-size: 12px; border-top: 1px solid {style['grid']}; padding-top: 8px; }}
    .thread-status strong {{ color: {style['text']}; }}
    .thread-pin {{ color: {style['brand']}; font-size: 10px; font-weight: 700; letter-spacing: .08em; }}
    .thread-route {{ transition: opacity .18s ease, stroke-width .18s ease; }}
    .thread-route.hot {{ opacity: .92 !important; }}
    .lieflat-chart.focused .thread-route:not(.hot) {{ opacity: .05 !important; }}
    .thread-node {{ cursor: pointer; transition: opacity .18s ease; }}
    .lieflat-chart.focused .thread-node:not(.hot) {{ opacity: .24; }}
    .thread-hit {{ cursor: pointer; }}
    .topic-force-chart {{ height: 640px; cursor: grab; }}
    .topic-force-chart:active {{ cursor: grabbing; }}
    .dealer-digest {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin: 16px 0 20px; }}
    .dealer-digest-item {{ padding: 14px 16px; background: {style['insight_bg']}; border: 1px solid {style['border']}; }}
    .dealer-digest-label {{ color: {style['muted']}; font-size: 11px; letter-spacing: .08em; }}
    .dealer-digest-value {{ margin-top: 6px; color: {style['text']}; font-size: 14px; font-weight: 650; }}
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
    .selection-reason {{ margin-top: 12px !important; padding: 10px 12px; border-left: 3px solid {style['brand']}; background: {style['panel_bg']}; }}
    .selection-reason strong {{ color: {style['brand']}; }}
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
      .cards, .grid, .hot-list, .dealer-digest {{ grid-template-columns: 1fr; }}
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
      <p class="chart-kicker">相对贡献刻度用于快速比较账号强弱，行尾保留精确互动量。</p>
      <svg id="authorChart" class="chart lieflat-chart" viewBox="0 0 560 320" preserveAspectRatio="xMidYMid meet" aria-label="账号互动贡献 Tick Rows"></svg>
      <div class="chart-source">TICK ROWS · ACCOUNT CONTRIBUTION</div>
    </div>
    <div class="panel">
      <h2>发布时间与互动走势</h2>
      <div id="trendChart" class="chart"></div>
    </div>
  </section>

  <section class="section">
    <div class="panel">
      <h2>话题传播网络</h2>
      <p class="chart-kicker">展示互动量最高的 Top10 话题及全部传播账号；大球是话题，小球是账号，节点大小代表累计互动量，连线粗细代表作品数。</p>
      <div id="topicChart" class="topic-force-chart" aria-label="热门话题与传播账号 Force Graph"></div>
      <div class="chart-source">FORCE GRAPH · TOPIC ACCOUNT NETWORK</div>
    </div>
  </section>

  <section class="section">
    <div class="panel">
      <h2>官方发起 → 经销商承接 桑基图</h2>
      <p class="meta">每条线代表一条可追溯的承接关系；悬停聚焦单条或整束链路，点击可锁定。{safe_html(sankey_data['message'])}</p>
      <div class="dealer-digest">
        {''.join(
            f'<div class="dealer-digest-item"><div class="dealer-digest-label">{safe_html(label)}</div><div class="dealer-digest-value">{safe_html(value)}</div></div>'
            for label, value in dealer_digest
        )}
      </div>
      <svg id="sankeyChart" class="chart lieflat-chart" style="height: {sankey_height}px;" viewBox="0 0 1100 560" preserveAspectRatio="xMidYMid meet" aria-label="官方到经销商 Big Threads"></svg>
      <div id="threadStatus" class="thread-status"><span id="threadStatusText">悬停线条或节点查看传播链路</span><span id="threadStatusPin" class="thread-pin"></span></div>
      <div class="chart-source">BIG THREADS · OFFICIAL → TOPIC → DEALER</div>
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

    const svgNS = 'http://www.w3.org/2000/svg';
    const svgEl = (parent, tag, attrs = {{}}) => {{
      const node = document.createElementNS(svgNS, tag);
      Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value));
      parent.appendChild(node);
      return node;
    }};
    const svgText = (parent, attrs, value) => {{
      const node = svgEl(parent, 'text', attrs);
      node.textContent = value;
      return node;
    }};
    const stableNoise = (a, b) => Math.abs(((a * 73856093) ^ (b * 19349663)) % 1000) / 1000;
    const compactNumber = value => new Intl.NumberFormat('zh-CN', {{ notation: 'compact', maximumFractionDigits: 1 }}).format(value || 0);

    const renderAuthorTickRows = () => {{
      const svg = document.getElementById('authorChart');
      const rows = reportData.author_labels.map((label, index) => ({{
        label,
        value: Number(reportData.author_values[index] || 0)
      }}));
      if (!rows.length) {{
        svgText(svg, {{ x: 280, y: 155, fill: '{style['muted']}', 'text-anchor': 'middle', 'font-size': 14 }}, '暂无账号互动数据');
        return;
      }}
      const maxValue = Math.max(...rows.map(row => row.value), 1);
      const x0 = 176;
      const maxTicks = 28;
      const tickGap = 9.2;
      rows.forEach((row, index) => {{
        const y = 30 + index * 36;
        const tickCount = row.value > 0 ? Math.max(1, Math.round(row.value / maxValue * maxTicks)) : 0;
        svgText(svg, {{
          x: 164, y: y + 4, fill: '{style['muted']}', 'text-anchor': 'end',
          'font-size': 11, 'font-weight': 600
        }}, String(row.label).slice(0, 12));
        svgEl(svg, 'line', {{
          x1: x0, y1: y + 10, x2: x0 + maxTicks * tickGap, y2: y + 10,
          stroke: '{style['grid']}', 'stroke-width': .8
        }});
        for (let tick = 0; tick < tickCount; tick += 1) {{
          const x = x0 + tick * tickGap + tickGap / 2;
          const height = 10 + stableNoise(tick + 1, index + 2) * 8;
          svgEl(svg, 'line', {{
            x1: x, y1: y + 10, x2: x, y2: y + 10 - height,
            stroke: colorMain, 'stroke-width': 1.6,
            opacity: .58 + stableNoise(tick + 3, index + 5) * .42,
            'stroke-linecap': 'round'
          }});
          if (tick % 5 === 4) {{
            svgEl(svg, 'circle', {{ cx: x, cy: y + 14, r: 1.2, fill: colorAssist, opacity: .7 }});
          }}
        }}
        svgText(svg, {{
          x: x0 + maxTicks * tickGap + 16, y: y + 4, fill: '{style['text']}',
          'font-size': 12, 'font-weight': 700
        }}, compactNumber(row.value));
      }});
    }};
    renderAuthorTickRows();

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

    const renderTopicForceGraph = () => {{
      const chart = echarts.init(document.getElementById('topicChart'));
      const network = reportData.topic_network || {{ topics: [], accounts: [], links: [] }};
      if (!network.topics.length || !network.accounts.length) {{
        chart.setOption({{
          title: {{
            text: network.message || '当前时间范围暂无可构建的话题传播网络',
            left: 'center',
            top: 'middle',
            textStyle: {{ color: '{style['muted']}', fontSize: 14, fontWeight: 400 }}
          }}
        }});
        return chart;
      }}

      const maxTopicInteraction = Math.max(...network.topics.map(item => item.interaction_count), 1);
      const maxAccountInteraction = Math.max(...network.accounts.map(item => item.interaction_count), 1);
      const topicShare = value => value / maxTopicInteraction;
      const accountShare = value => value / maxAccountInteraction;
      const accountColors = {{
        official: colorMain,
        dealer: colorGreen,
        other: colorAssist
      }};
      const nodes = [
        ...network.topics.map(item => ({{
          id: `topic::${{item.name}}`,
          name: item.name,
          nodeType: '话题',
          interactionCount: item.interaction_count,
          workCount: item.work_count,
          symbolSize: 50 + Math.sqrt(topicShare(item.interaction_count)) * 38,
          itemStyle: {{ color: colorAssist, borderColor: '{style['body_bg']}', borderWidth: 4 }},
          label: {{ show: true, color: '{style['text']}', fontWeight: 700, fontSize: 11 }}
        }})),
        ...network.accounts.map(item => ({{
          id: `account::${{item.name}}`,
          name: item.name,
          nodeType: item.account_type === 'official' ? '官方账号' : item.account_type === 'dealer' ? '经销商账号' : '其他账号',
          interactionCount: item.interaction_count,
          workCount: item.work_count,
          symbolSize: 8 + Math.sqrt(accountShare(item.interaction_count)) * 24,
          itemStyle: {{ color: accountColors[item.account_type] || colorAssist }},
          label: {{ show: item.account_type === 'official', color: '{style['text']}', fontSize: 10 }}
        }}))
      ];
      const links = network.links.map(item => ({{
        source: `account::${{item.account}}`,
        target: `topic::${{item.topic}}`,
        workCount: item.work_count,
        interactionCount: item.interaction_count,
        lineStyle: {{
          width: .8 + Math.min(5, item.work_count * 1.2),
          color: '{style['grid']}',
          opacity: .48,
          curveness: .08
        }}
      }}));
      const option = {{
        animationDuration: 320,
        tooltip: {{
          renderMode: 'richText',
          backgroundColor: '{style['body_bg']}',
          borderColor: '{style['border']}',
          textStyle: {{ color: '{style['text']}', fontSize: 12 }},
          formatter: params => {{
            if (params.dataType === 'edge') {{
              return `${{params.data.workCount}} 条作品\\n累计互动 ${{compactNumber(params.data.interactionCount)}}`;
            }}
            const ratio = reportData.total_interactions > 0
              ? (params.data.interactionCount / reportData.total_interactions * 100).toFixed(1)
              : '0.0';
            return `${{params.data.nodeType}} · ${{params.name}}\\n${{params.data.workCount}} 条作品\\n累计互动 ${{compactNumber(params.data.interactionCount)}}\\n互动占比 ${{ratio}}%`;
          }}
        }},
        series: [{{
          type: 'graph',
          layout: 'force',
          roam: true,
          draggable: true,
          data: nodes,
          links,
          force: {{
            repulsion: [90, 260],
            edgeLength: [64, 150],
            gravity: .12,
            friction: .22,
            layoutAnimation: true
          }},
          emphasis: {{
            focus: 'adjacency',
            lineStyle: {{ opacity: .95, width: 2.4 }},
            label: {{ show: true, color: '{style['text']}', position: 'right' }}
          }},
          blur: {{
            itemStyle: {{ opacity: .12 }},
            lineStyle: {{ opacity: .04 }}
          }}
        }}]
      }};
      const replay = () => {{
        chart.clear();
        chart.setOption(option);
      }};
      replay();
      chart.getZr().on('click', event => {{ if (!event.target) replay(); }});
      return chart;
    }};
    const topicChart = renderTopicForceGraph();

    const renderBigThreads = () => {{
      const svg = document.getElementById('sankeyChart');
      const statusText = document.getElementById('threadStatusText');
      const statusPin = document.getElementById('threadStatusPin');
      const topicNames = reportData.sankey_nodes.filter(node => node.depth === 1).map(node => node.name);
      const dealerNames = reportData.sankey_nodes.filter(node => node.depth === 2).map(node => node.name);
      const routes = reportData.sankey_links
        .filter(link => topicNames.includes(link.source) && dealerNames.includes(link.target))
        .map(link => ({{ source: '官方账号', topic: link.source, dealer: link.target, value: Number(link.value || 0) }}));
      if (!routes.length) {{
        svgText(svg, {{ x: 550, y: 270, fill: '{style['muted']}', 'text-anchor': 'middle', 'font-size': 14 }}, '暂无可追溯的官方—话题—经销商承接链路');
        return;
      }}

      const xSource = 130;
      const xTopic = 520;
      const xDealer = 930;
      const sourceY = 280;
      const distribute = (index, total, top = 82, bottom = 492) => total <= 1 ? (top + bottom) / 2 : top + index * (bottom - top) / (total - 1);
      const topicY = new Map(topicNames.map((name, index) => [name, distribute(index, topicNames.length)]));
      const dealerY = new Map(dealerNames.map((name, index) => [name, distribute(index, dealerNames.length)]));
      const maxRoute = Math.max(...routes.map(route => route.value), 1);
      const pathFor = route => `M${{xSource + 8}} ${{sourceY}} C300 ${{sourceY}} 350 ${{topicY.get(route.topic)}} ${{xTopic}} ${{topicY.get(route.topic)}} C690 ${{topicY.get(route.topic)}} 735 ${{dealerY.get(route.dealer)}} ${{xDealer - 8}} ${{dealerY.get(route.dealer)}}`;

      [[xSource, '① 官方发起'], [xTopic, '② 话题主线'], [xDealer, '③ 经销商承接']].forEach(([x, label]) => {{
        svgText(svg, {{ x, y: 32, fill: '{style['muted']}', 'text-anchor': 'middle', 'font-size': 11, 'font-weight': 700, 'letter-spacing': '.12em' }}, label);
      }});

      const threadGroup = svgEl(svg, 'g');
      routes.forEach((route, index) => {{
        const d = pathFor(route);
        route.line = svgEl(threadGroup, 'path', {{
          d, fill: 'none', stroke: colorMain,
          'stroke-width': Math.max(1, route.value / maxRoute * 6),
          opacity: .12 + route.value / maxRoute * .24,
          'stroke-linecap': 'round', class: 'thread-route'
        }});
        route.hit = svgEl(threadGroup, 'path', {{
          d, fill: 'none', stroke: '#000', 'stroke-opacity': 0,
          'stroke-width': 12, class: 'thread-hit', 'data-route': index
        }});
      }});

      const nodes = [];
      const addNode = (x, y, label, kind, index, anchor, color) => {{
        const group = svgEl(svg, 'g', {{ class: 'thread-node', 'data-kind': kind, 'data-index': index }});
        svgEl(group, 'circle', {{ cx: x, cy: y, r: kind === 'source' ? 7 : 4, fill: color }});
        svgText(group, {{
          x: anchor === 'end' ? x - 14 : x + 14, y: y + 4,
          fill: '{style['text']}', 'text-anchor': anchor, 'font-size': 11, 'font-weight': 650
        }}, String(label).slice(0, 16));
        svgEl(group, 'rect', {{
          x: anchor === 'end' ? x - 130 : x - 8, y: y - 12,
          width: 138, height: 24, fill: '#000', 'fill-opacity': 0, class: 'thread-hit'
        }});
        nodes.push(group);
      }};
      addNode(xSource, sourceY, '官方账号', 'source', 0, 'end', colorMain);
      topicNames.forEach((name, index) => addNode(xTopic, topicY.get(name), name, 'topic', index, 'start', colorAssist));
      dealerNames.forEach((name, index) => addNode(xDealer, dealerY.get(name), name, 'dealer', index, 'start', colorGreen));

      let pinned = false;
      const clearFocus = () => {{
        svg.classList.remove('focused');
        routes.forEach(route => route.line.classList.remove('hot'));
        nodes.forEach(node => node.classList.remove('hot'));
        statusText.textContent = '悬停线条或节点查看传播链路';
        statusPin.textContent = '';
      }};
      const focusRoutes = (selected, label) => {{
        svg.classList.add('focused');
        routes.forEach(route => route.line.classList.toggle('hot', selected.includes(route)));
        nodes.forEach(node => {{
          const kind = node.dataset.kind;
          const index = Number(node.dataset.index);
          const name = kind === 'topic' ? topicNames[index] : kind === 'dealer' ? dealerNames[index] : '官方账号';
          node.classList.toggle('hot', selected.some(route => route.source === name || route.topic === name || route.dealer === name));
        }});
        statusText.textContent = label;
      }};
      const actionFor = target => {{
        const hit = target.closest?.('.thread-hit');
        if (!hit) return null;
        if (hit.dataset.route !== undefined) {{
          const route = routes[Number(hit.dataset.route)];
          return () => focusRoutes([route], `${{route.source}} → ${{route.topic}} → ${{route.dealer}} · ${{compactNumber(route.value)}} 次互动`);
        }}
        const node = hit.closest('.thread-node');
        if (!node) return null;
        const kind = node.dataset.kind;
        const index = Number(node.dataset.index);
        const name = kind === 'topic' ? topicNames[index] : kind === 'dealer' ? dealerNames[index] : '官方账号';
        const selected = routes.filter(route => route.source === name || route.topic === name || route.dealer === name);
        const total = selected.reduce((sum, route) => sum + route.value, 0);
        return () => focusRoutes(selected, `${{name}} · ${{selected.length}} 条链路 · ${{compactNumber(total)}} 次互动`);
      }};
      svg.addEventListener('mousemove', event => {{
        if (pinned) return;
        const action = actionFor(event.target);
        action ? action() : clearFocus();
      }});
      svg.addEventListener('mouseleave', () => {{ if (!pinned) clearFocus(); }});
      svg.addEventListener('click', event => {{
        const action = actionFor(event.target);
        if (action) {{
          pinned = true;
          action();
          statusPin.textContent = 'PINNED · 点击空白处释放';
        }} else {{
          pinned = false;
          clearFocus();
        }}
      }});
    }};
    renderBigThreads();

    window.addEventListener('resize', () => {{
      trendChart.resize();
      topicChart.resize();
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
        '入选判断': str(record.get('selection_reason') or ''),
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
        'keywords': parsed_sections['评论关键词'],
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
                '入选判断',
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
