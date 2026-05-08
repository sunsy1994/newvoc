import unittest

from backend.app.journey_rules import infer_journey_stage, suggest_owner_and_action


class JourneyRulesTest(unittest.TestCase):
    def test_business_status_overrides_text(self):
        result = infer_journey_stage(
            source_channel="dcc",
            text="用户还想看看价格",
            business_status="到店",
            rating_score=None,
        )
        self.assertEqual(result["stage"], "试驾/到店")
        self.assertGreaterEqual(result["confidence"], 0.8)

    def test_price_text_maps_to_quote_stage(self):
        result = infer_journey_stage(
            source_channel="public_social",
            text="这车优惠多少，金融方案怎么算",
            business_status="",
            rating_score=None,
        )
        self.assertEqual(result["stage"], "报价/权益")

    def test_dianping_defaults_to_store_visit(self):
        result = infer_journey_stage(
            source_channel="dianping",
            text="整体体验不错，但是等待时间有点长",
            business_status="",
            rating_score=4,
        )
        self.assertEqual(result["stage"], "试驾/到店")
        self.assertIn("渠道默认", result["reason"])

    def test_sales_action_for_negative_price_issue(self):
        result = suggest_owner_and_action(
            journey_stage="报价/权益",
            issue_tag="价格权益",
            sentiment_tag="负向",
        )
        self.assertEqual(result["owner"], "销售运营")
        self.assertIn("报价", result["action"])


if __name__ == "__main__":
    unittest.main()
