import json
import unittest

import pandas as pd

from backend.app.tasks.customer_touchpoint_standardize import _build_public_touchpoints
from backend.app.tasks.journey_channel_matrix import _build_channel_matrix
from backend.app.tasks.journey_painpoint_summary import _build_painpoint_summary
from backend.app.tasks.journey_stage_summary import _build_stage_summary


class JourneyTaskTest(unittest.TestCase):
    def test_public_comments_standardize_to_touchpoints(self):
        comments = pd.DataFrame(
            [
                {
                    "comment_id": "cmt-1",
                    "platform": "小红书",
                    "content_id": "cnt-1",
                    "comment_author_id": "",
                    "comment_author_name": "用户A",
                    "comment_text": "这个车优惠多少",
                    "published_at": "2026-05-08 10:00:00",
                    "opinion_tag": "价格权益",
                    "intention_tag": "询价",
                    "sentiment_tag": "中性",
                    "mindset_tag": "经济实用",
                    "stage_tag": "",
                    "event_id": "evt-1",
                    "brand_name": "示例品牌",
                    "model_name": "示例车型",
                }
            ]
        )

        result = _build_public_touchpoints(comments)

        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["source_channel"], "public_social")
        self.assertEqual(result.iloc[0]["journey_stage"], "报价/权益")
        self.assertEqual(result.iloc[0]["issue_tag"], "价格权益")

    def test_stage_summary_counts_real_touchpoints(self):
        touchpoints = pd.DataFrame(
            [
                _touchpoint("tp-1", "public_social", "报价/权益", "价格权益", "负向"),
                _touchpoint("tp-2", "dcc", "报价/权益", "价格权益", "中性"),
            ]
        )

        result = _build_stage_summary(touchpoints)

        self.assertEqual(len(result), 1)
        row = result.iloc[0]
        self.assertEqual(row["touchpoint_cnt"], 2)
        self.assertEqual(row["channel_cnt"], 2)
        self.assertEqual(row["negative_ratio"], 0.5)
        self.assertEqual(json.loads(row["issue_top_json"])[0]["label"], "价格权益")

    def test_channel_matrix_groups_by_channel_and_stage(self):
        touchpoints = pd.DataFrame(
            [
                _touchpoint("tp-1", "public_social", "曝光认知", "外观", "中性"),
                _touchpoint("tp-2", "dcc", "留资/外呼", "跟进", "负向"),
            ]
        )

        result = _build_channel_matrix(touchpoints)

        self.assertEqual(len(result), 2)
        self.assertEqual(set(result["source_channel"]), {"public_social", "dcc"})

    def test_painpoint_summary_adds_owner_action(self):
        touchpoints = pd.DataFrame(
            [_touchpoint("tp-1", "dcc", "报价/权益", "价格权益", "负向")]
        )

        result = _build_painpoint_summary(touchpoints)

        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["suggested_owner"], "销售运营")
        self.assertIn("报价", result.iloc[0]["suggested_action"])


def _touchpoint(touchpoint_id, channel, stage, issue, sentiment):
    return {
        "touchpoint_id": touchpoint_id,
        "source_channel": channel,
        "source_system": channel,
        "source_record_id": touchpoint_id,
        "channel_user_key": "用户",
        "user_display_name": "用户",
        "touchpoint_text": "样本文本",
        "touchpoint_time": "2026-05-08 10:00:00",
        "brand_name": "示例品牌",
        "model_name": "示例车型",
        "city_name": None,
        "store_id": None,
        "store_name": None,
        "event_id": None,
        "content_id": None,
        "journey_stage": stage,
        "stage_confidence": 0.8,
        "stage_reason": "测试",
        "intent_tag": "询问",
        "issue_tag": issue,
        "sentiment_tag": sentiment,
        "mindset_tag": "",
        "business_status": "",
        "rating_score": None,
    }


if __name__ == "__main__":
    unittest.main()
