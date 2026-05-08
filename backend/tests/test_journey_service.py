import unittest

import pandas as pd

from backend.app.journey_service import _json_list, _row_to_matrix, _row_to_painpoint, _row_to_stage


class JourneyServiceTest(unittest.TestCase):
    def test_json_list_parses_only_real_json_arrays(self):
        self.assertEqual(_json_list('[{"label":"价格","value":2}]'), [{"label": "价格", "value": 2}])
        self.assertEqual(_json_list('{"label":"价格"}'), [])
        self.assertEqual(_json_list(""), [])

    def test_stage_mapping_keeps_lineage(self):
        item = _row_to_stage(
            pd.Series(
                {
                    "journey_stage": "报价/权益",
                    "touchpoint_cnt": 3,
                    "channel_cnt": 2,
                    "negative_ratio": 0.3333,
                    "intent_top_json": '[{"label":"询价","value":3}]',
                    "issue_top_json": '[{"label":"价格权益","value":3}]',
                    "channel_distribution_json": '[{"label":"dcc","value":2}]',
                    "representative_touchpoints_json": "[]",
                }
            )
        )

        self.assertEqual(item.stage, "报价/权益")
        self.assertEqual(item.touchpoint_count, 3)
        self.assertEqual(item.data_lineage.tables, ["ads_journey_stage_summary"])

    def test_matrix_mapping(self):
        item = _row_to_matrix(
            pd.Series(
                {
                    "source_channel": "dcc",
                    "journey_stage": "留资/外呼",
                    "touchpoint_cnt": 5,
                    "negative_ratio": 0.2,
                    "issue_top_json": "[]",
                    "intent_top_json": "[]",
                }
            )
        )

        self.assertEqual(item.source_channel, "dcc")
        self.assertEqual(item.journey_stage, "留资/外呼")

    def test_painpoint_mapping(self):
        item = _row_to_painpoint(
            pd.Series(
                {
                    "journey_stage": "报价/权益",
                    "issue_tag": "价格权益",
                    "touchpoint_cnt": 2,
                    "negative_ratio": 0.5,
                    "source_channels_json": '[{"label":"dcc","value":2}]',
                    "sample_texts_json": "[]",
                    "suggested_owner": "销售运营",
                    "suggested_action": "复盘报价话术",
                }
            )
        )

        self.assertEqual(item.suggested_owner, "销售运营")
        self.assertIn("报价", item.suggested_action)


if __name__ == "__main__":
    unittest.main()
