JOURNEY_STAGES = [
    "曝光认知",
    "兴趣咨询",
    "对比评估",
    "留资/外呼",
    "试驾/到店",
    "报价/权益",
    "下订/战败",
    "交付/售后",
    "复购/推荐",
]

NEGATIVE_SENTIMENTS = {"负向", "强负面", "负面", "消极"}

BUSINESS_STATUS_STAGE = {
    "留资": "留资/外呼",
    "线索": "留资/外呼",
    "外呼": "留资/外呼",
    "邀约": "留资/外呼",
    "到店": "试驾/到店",
    "试驾": "试驾/到店",
    "报价": "报价/权益",
    "金融": "报价/权益",
    "权益": "报价/权益",
    "下订": "下订/战败",
    "订车": "下订/战败",
    "战败": "下订/战败",
    "成交": "下订/战败",
    "交付": "交付/售后",
    "售后": "交付/售后",
    "保养": "交付/售后",
    "维修": "交付/售后",
    "复购": "复购/推荐",
    "推荐": "复购/推荐",
    "转介绍": "复购/推荐",
}

TEXT_STAGE_KEYWORDS = [
    ("报价/权益", ["价格", "优惠", "权益", "金融", "贷款", "置换", "补贴", "保险"]),
    ("试驾/到店", ["到店", "门店", "试驾", "销售", "接待", "展厅"]),
    ("留资/外呼", ["留资", "电话", "外呼", "邀约", "预约", "回电"]),
    ("下订/战败", ["下订", "订车", "锁单", "退订", "战败", "不买"]),
    ("交付/售后", ["交付", "提车", "维修", "保养", "售后", "故障"]),
    ("复购/推荐", ["推荐", "复购", "转介绍", "朋友也买"]),
    ("对比评估", ["对比", "竞品", "配置", "续航", "空间", "油耗", "智驾"]),
    ("兴趣咨询", ["咨询", "了解", "怎么样", "能买吗", "想买"]),
]

CHANNEL_DEFAULT_STAGE = {
    "400": "兴趣咨询",
    "wecom": "兴趣咨询",
    "dcc": "留资/外呼",
    "dianping": "试驾/到店",
    "public_social": "曝光认知",
}


def _contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def infer_journey_stage(
    *,
    source_channel: str,
    text: str | None,
    business_status: str | None,
    rating_score: float | None,
) -> dict:
    status_text = (business_status or "").strip()
    for keyword, stage in BUSINESS_STATUS_STAGE.items():
        if keyword in status_text:
            return {
                "stage": stage,
                "confidence": 0.9,
                "reason": f"业务状态命中：{keyword}。",
            }

    text_value = (text or "").strip()
    for stage, keywords in TEXT_STAGE_KEYWORDS:
        if _contains_any(text_value, keywords):
            return {
                "stage": stage,
                "confidence": 0.7,
                "reason": f"文本关键词命中：{stage}。",
            }

    channel = (source_channel or "").strip().lower()
    fallback = CHANNEL_DEFAULT_STAGE.get(channel, "兴趣咨询")
    confidence = 0.6 if channel == "dianping" and rating_score is not None else 0.3
    return {
        "stage": fallback,
        "confidence": confidence,
        "reason": f"渠道默认阶段：{source_channel}。",
    }


def suggest_owner_and_action(
    *,
    journey_stage: str,
    issue_tag: str | None,
    sentiment_tag: str | None,
) -> dict:
    issue = issue_tag or ""
    sentiment = sentiment_tag or ""

    if journey_stage == "报价/权益" and ("价格" in issue or "权益" in issue):
        return {
            "owner": "销售运营",
            "action": "复盘报价话术、金融方案和权益解释，优先补充用户最常质疑的价格证据。",
        }

    if journey_stage == "试驾/到店":
        return {
            "owner": "门店运营",
            "action": "检查到店接待、试驾预约和门店体验反馈，沉淀高频问题处理口径。",
        }

    if journey_stage == "交付/售后":
        return {
            "owner": "服务运营",
            "action": "定位交付和售后负反馈样本，拆分服务流程、等待时间和维修质量问题。",
        }

    if "负" in sentiment:
        return {
            "owner": "客户运营",
            "action": "优先查看负向触点证据，判断是否需要补充解释、回访或跨部门处理。",
        }

    return {
        "owner": "客户运营",
        "action": "持续观察该阶段高频意图和问题，保留原文证据用于后续策略复盘。",
    }
