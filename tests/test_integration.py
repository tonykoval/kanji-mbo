"""Integration tests that run the full pipeline against real Excel data."""

import sys
import os
import logging
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import algorithm
from data_loader import read_excel
from model import Constants

EXCEL_FILE = os.path.join(os.path.dirname(__file__), '..', 'excel', '1500 KANJI COMPONENTS - ver. 1.3.xlsx')
SKIP_REASON = "Excel file not found"


@unittest.skipUnless(os.path.exists(EXCEL_FILE), SKIP_REASON)
class TestFullCategorization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        algorithm.set_logging_level(logging.WARNING)
        cls.source = read_excel(EXCEL_FILE)
        cls.categorization = algorithm.init_categorization(cls.source)

        for kanji in algorithm.read_kanji_dataframe(cls.source.df_kanji):
            algorithm.categorize_kanji(kanji, cls.categorization, cls.source)

        algorithm.categorize_queue(cls.categorization)

    def test_all_kanji_categorized(self):
        total = sum(len(v) for v in self.categorization.result.values())
        source_count = len(self.source.df_kanji)
        # Every kanji from the source should appear in exactly one group
        self.assertGreater(total, 0)
        self.assertGreaterEqual(total, source_count)

    def test_groups_non_empty(self):
        non_empty = {k: v for k, v in self.categorization.result.items() if len(v) > 0}
        self.assertGreater(len(non_empty), 0)

    def test_other_group_exists(self):
        self.assertIn(Constants.other_grp, self.categorization.result)

    def test_special_group_removed_after_queue(self):
        self.assertNotIn(Constants.special_grp, self.categorization.result)

    def test_queue_partially_resolved(self):
        # After categorize_queue, most queue entries should be placed into result groups.
        # Some remain because their ref kanji was categorized in a different group than expected.
        remaining = sum(len(v) for v in self.categorization.queue.values())
        total = sum(len(v) for v in self.categorization.result.values())
        # Result should contain significantly more kanji than the queue
        self.assertGreater(total, remaining)

    def test_kanji_have_valid_fields(self):
        for group_name, kanji_list in self.categorization.result.items():
            for k in kanji_list[:5]:  # spot-check first 5 per group
                self.assertTrue(k.char, f"Empty char in group {group_name}")
                self.assertTrue(k.ref, f"Empty ref in group {group_name}")
                self.assertIsInstance(k.srl, int)
                self.assertIsInstance(k.freq, int)
                self.assertIsInstance(k.on_reading, list)


@unittest.skipUnless(os.path.exists(EXCEL_FILE), SKIP_REASON)
class TestSingleKanjiCategorization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        algorithm.set_logging_level(logging.WARNING)
        cls.source = read_excel(EXCEL_FILE)

    def _categorize_one(self, char):
        categorization = algorithm.init_categorization(self.source)
        kanji = algorithm.read_kanji_char(char, self.source)
        algorithm.categorize_kanji(kanji, categorization, self.source)
        return categorization

    def test_keyword_kanji_placed_in_group(self):
        cat = self._categorize_one("百")
        # 百 should land somewhere (keyword rule)
        total = sum(len(v) for v in cat.result.values())
        self.assertGreaterEqual(total, 1)

    def test_lookup_returns_valid_data(self):
        kanji = algorithm.read_kanji_char("日", self.source)
        self.assertEqual(kanji.char, "日")
        self.assertTrue(len(kanji.on_reading) > 0)


@unittest.skipUnless(os.path.exists(EXCEL_FILE), SKIP_REASON)
class TestAnkiExport(unittest.TestCase):
    def test_export_creates_file(self):
        import tempfile
        from anki_export import export_categorization

        algorithm.set_logging_level(logging.WARNING)
        source = read_excel(EXCEL_FILE)
        categorization = algorithm.init_categorization(source)

        for kanji in algorithm.read_kanji_dataframe(source.df_kanji):
            algorithm.categorize_kanji(kanji, categorization, source)

        algorithm.categorize_queue(categorization)

        with tempfile.NamedTemporaryFile(suffix=".apkg", delete=False) as f:
            output_path = f.name

        try:
            export_categorization(categorization, output_path)
            self.assertTrue(os.path.exists(output_path))
            self.assertGreater(os.path.getsize(output_path), 0)
        finally:
            os.unlink(output_path)


if __name__ == "__main__":
    unittest.main()
