import unittest

from backend.app.import_service import _prepare_rows
from backend.app.template_registry import get_template


class FakeDataFrame:
    def __init__(self, rows):
        self._rows = rows

    def to_dict(self, orient):
        if orient != "records":
            raise ValueError(f"unsupported orient: {orient}")
        return self._rows


class JourneyImportTest(unittest.TestCase):
    def test_journey_400_template_uses_minimum_required_fields(self):
        template = get_template("tpl-journey-400")

        self.assertIsNotNone(template)
        self.assertEqual(template["source_key"], "journey_400")
        self.assertEqual(template["target_table"], "dwd_customer_touchpoint")
        self.assertEqual(
            template["required_fields"],
            ["touchpoint_id", "touchpoint_time", "touchpoint_text"],
        )

    def test_journey_import_rows_keep_channel_level_identity(self):
        dataframe = FakeDataFrame(
            [
                {
                    "touchpoint_id": "tp-001",
                    "touchpoint_time": "2026-05-08 10:00:00",
                    "touchpoint_text": "用户咨询金融方案和优惠",
                    "user_display_name": "张先生",
                    "business_status": "报价",
                    "sentiment_tag": "中性",
                }
            ]
        )

        rows, rel_rows = _prepare_rows(dataframe, "journey_dcc")

        self.assertEqual(rel_rows, [])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["source_channel"], "dcc")
        self.assertEqual(rows[0]["source_system"], "dcc")
        self.assertEqual(rows[0]["source_record_id"], "tp-001")
        self.assertEqual(rows[0]["channel_user_key"], "张先生")
        self.assertEqual(rows[0]["touchpoint_text"], "用户咨询金融方案和优惠")
        self.assertEqual(rows[0]["business_status"], "报价")


if __name__ == "__main__":
    unittest.main()
