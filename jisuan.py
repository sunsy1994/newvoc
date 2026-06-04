import json
from collections import defaultdict
from typing import Dict, Any


def get_emotion_weight(emotion_level: str) -> float:
    """
    情绪权重：
    只做小幅加权，避免强情绪评论过度影响画像。
    """
    mapping = {
        "高": 1.10,
        "中": 1.05,
        "低": 1.00,
        "无法判断": 1.00
    }
    return mapping.get(emotion_level, 1.00)


def get_frequency_boost(support_count: int) -> float:
    """
    频次加成：
    同一标签被多条评论支持，说明该画像特征更稳定。
    """
    if support_count <= 1:
        return 1.00
    return 1 + min((support_count - 1) * 0.08, 0.24)


def get_sample_penalty(support_count: int) -> float:
    """
    样本量惩罚：
    防止单条评论直接把某个标签打成高分。
    """
    if support_count <= 1:
        return 0.78
    elif support_count == 2:
        return 0.92
    else:
        return 1.00


def get_feature_level(score: float) -> str:
    """
    标签强度等级。
    """
    if score >= 80:
        return "强特征"
    elif score >= 60:
        return "明显特征"
    elif score >= 40:
        return "弱信号"
    else:
        return "不明显"


def get_confidence_level(score: float, support_count: int) -> str:
    """
    置信等级：
    分数代表强度，support_count 代表稳定性。
    """
    if score >= 80 and support_count >= 3:
        return "高置信"
    elif score >= 70 and support_count >= 2:
        return "中高置信"
    elif score >= 60:
        return "中置信"
    elif score >= 40:
        return "低置信"
    else:
        return "不输出"


def calculate_user_profile(user_id: str, llm_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    输入：
        user_id: 用户 ID
        llm_result: LLM 输出的证据抽取 JSON

    输出：
        用户画像计算结果 profile_result
    """

    comments = llm_result.get("comment_evidence_results", [])
    label_bucket = defaultdict(list)

    # Step 1：按标签聚合证据
    for comment in comments:
        if not comment.get("is_valid", False):
            continue

        comment_id = comment.get("comment_id", "")
        comment_text = comment.get("comment_text", "")
        comment_quality_score = float(comment.get("comment_quality_score", 0))

        emotion = comment.get("emotion", {})
        emotion_level = emotion.get("emotion_level", "低")
        emotion_weight = get_emotion_weight(emotion_level)

        for evidence in comment.get("evidence_list", []):
            dimension = evidence.get("dimension", "")
            label = evidence.get("label", "")
            evidence_score = float(evidence.get("evidence_score", 0))

            if not dimension or not label:
                continue

            # 低于 0.5 的证据不参与画像计算
            if evidence_score < 0.5:
                continue

            key = (dimension, label)

            label_bucket[key].append({
                "comment_id": comment_id,
                "comment_text": comment_text,
                "comment_quality_score": comment_quality_score,
                "emotion_level": emotion_level,
                "emotion_weight": emotion_weight,
                "evidence_score": evidence_score,
                "evidence_text": evidence.get("evidence_text", ""),
                "reason": evidence.get("reason", "")
            })

    # Step 2：逐标签计算分数
    label_scores = []

    for (dimension, label), records in label_bucket.items():
        support_count = len(records)

        weighted_sum = 0.0
        weight_sum = 0.0

        for r in records:
            weight = r["comment_quality_score"] * r["emotion_weight"]
            weighted_sum += r["evidence_score"] * weight
            weight_sum += weight

        base_score = weighted_sum / weight_sum if weight_sum else 0.0
        frequency_boost = get_frequency_boost(support_count)
        sample_penalty = get_sample_penalty(support_count)

        final_score = base_score * frequency_boost * sample_penalty * 100
        final_score = min(final_score, 100)
        final_score = round(final_score, 1)

        label_scores.append({
            "dimension": dimension,
            "label": label,
            "final_score": final_score,
            "feature_level": get_feature_level(final_score),
            "confidence_level": get_confidence_level(final_score, support_count),
            "support_count": support_count,

            "calculation": {
                "base_score": round(base_score, 3),
                "frequency_boost": round(frequency_boost, 3),
                "sample_penalty": round(sample_penalty, 3),
                "formula": "FinalScore = BaseScore × FrequencyBoost × SamplePenalty × 100"
            },

            "evidence_examples": [
                {
                    "comment_id": r["comment_id"],
                    "evidence_text": r["evidence_text"],
                    "comment_text": r["comment_text"]
                }
                for r in records[:3]
            ],

            "evidence_details": [
                {
                    "comment_id": r["comment_id"],
                    "comment_text": r["comment_text"],
                    "evidence_text": r["evidence_text"],
                    "evidence_score": r["evidence_score"],
                    "comment_quality_score": r["comment_quality_score"],
                    "emotion_level": r["emotion_level"],
                    "emotion_weight": r["emotion_weight"],
                    "reason": r["reason"]
                }
                for r in records
            ]
        })

    # Step 3：排序
    label_scores.sort(key=lambda x: x["final_score"], reverse=True)

    # Step 4：取最高分标签作为主标签
    main_label_info = label_scores[0] if label_scores else None

    profile_result = {
        "user_id": user_id,
        "total_comments": llm_result.get("total_comments", 0),
        "valid_comments": llm_result.get("valid_comments", 0),

        "main_label": main_label_info["label"] if main_label_info else None,
        "main_dimension": main_label_info["dimension"] if main_label_info else None,
        "main_score": main_label_info["final_score"] if main_label_info else None,

        "label_scores": label_scores
    }

    return profile_result