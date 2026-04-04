import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from model import Kanji, Source, Categorization, Constants, ExcelColumn, Stem


class TestKanji(unittest.TestCase):
    def _make_kanji(self, char="青", ref=None, srl=3, on_reading=None, keyword="blue",
                    type_val="MEAN", freq=1205, group="3a", component1="", component2="",
                    component3="", component4="", component5=""):
        return Kanji(
            ref=ref or char,
            char=char,
            component1=component1,
            component2=component2,
            component3=component3,
            component4=component4,
            component5=component5,
            on_reading=on_reading or ["セイ", "ショウ"],
            kun_reading="あお",
            keyword=keyword,
            srl=srl,
            type=type_val,
            freq=freq,
            tags=[],
            group=group,
        )

    def test_kanji_creation(self):
        k = self._make_kanji()
        self.assertEqual(k.char, "青")
        self.assertEqual(k.ref, "青")
        self.assertEqual(k.srl, 3)
        self.assertEqual(k.on_reading, ["セイ", "ショウ"])
        self.assertEqual(k.keyword, "blue")
        self.assertEqual(k.type, "MEAN")

    def test_kanji_ref_defaults_to_char(self):
        k = self._make_kanji(char="水")
        self.assertEqual(k.ref, "水")

    def test_kanji_ref_can_differ(self):
        k = self._make_kanji(char="清", ref="青")
        self.assertEqual(k.char, "清")
        self.assertEqual(k.ref, "青")

    def test_kanji_empty_on_reading(self):
        k = self._make_kanji(on_reading=[""])
        self.assertEqual(k.on_reading, [""])

    def test_kanji_tags_mutable(self):
        k = self._make_kanji()
        k.tags.append(Constants.crown_tag)
        self.assertIn(Constants.crown_tag, k.tags)

    def test_kanji_type_reassignment(self):
        k = self._make_kanji(type_val=Constants.mean)
        k.type = Constants.vr
        self.assertEqual(k.type, Constants.vr)


class TestStem(unittest.TestCase):
    def test_stem_creation(self):
        s = Stem(group="08 Wednesday", priority=3)
        self.assertEqual(s.group, "08 Wednesday")
        self.assertEqual(s.priority, 3)

    def test_stem_priority_comparison(self):
        s1 = Stem(group="a", priority=1)
        s2 = Stem(group="b", priority=3)
        self.assertGreater(s2.priority, s1.priority)


class TestCategorization(unittest.TestCase):
    def test_categorization_creation(self):
        c = Categorization(result={"01 numbers": []}, queue={})
        self.assertIn("01 numbers", c.result)
        self.assertEqual(len(c.queue), 0)

    def test_categorization_result_append(self):
        c = Categorization(result={"group": []}, queue={})
        k = Kanji(ref="百", char="百", component1="", component2="", component3="",
                  component4="", component5="", on_reading=["ヒャク"],
                  kun_reading="", keyword="hundred", srl=3, type="MEAN",
                  freq=100, tags=[], group="1a")
        c.result["group"].append(k)
        self.assertEqual(len(c.result["group"]), 1)
        self.assertEqual(c.result["group"][0].char, "百")

    def test_categorization_queue_setdefault(self):
        c = Categorization(result={}, queue={})
        c.queue.setdefault("青", []).append("清")
        c.queue.setdefault("青", []).append("晴")
        self.assertEqual(c.queue["青"], ["清", "晴"])


class TestConstants(unittest.TestCase):
    def test_group_constants(self):
        self.assertEqual(Constants.other_grp, "79 other")
        self.assertEqual(Constants.special_grp, "special")
        self.assertEqual(Constants.visual_grp, "visual")

    def test_type_constants(self):
        self.assertEqual(Constants.mean, "MEAN")
        self.assertEqual(Constants.special, "SPECIAL")
        self.assertEqual(Constants.other, "OTHER")
        self.assertEqual(Constants.stem, "STEM")
        self.assertEqual(Constants.vr, "VR")
        self.assertEqual(Constants.form, "FORM")
        self.assertEqual(Constants.visual, "VISUAL")
        self.assertEqual(Constants.priority, "PRIORITY")
        self.assertEqual(Constants.crown_tag, "CROWN_TAG")


class TestExcelColumn(unittest.TestCase):
    def test_column_names(self):
        self.assertEqual(ExcelColumn.char, "CHAR")
        self.assertEqual(ExcelColumn.component1, "COMPONENTS1")
        self.assertEqual(ExcelColumn.on_reading, "ON READING")
        self.assertEqual(ExcelColumn.srl, "SRL")

    def test_list_columns_length(self):
        self.assertEqual(len(ExcelColumn.list_columns), 14)

    def test_list_columns_contains_required(self):
        for col in ["CHAR", "COMPONENTS1", "COMPONENTS2", "ON READING", "KEYWORD", "SRL", "TYPE", "FREQ"]:
            self.assertIn(col, ExcelColumn.list_columns)

    def test_on_reading_delimiter(self):
        self.assertEqual(ExcelColumn.on_reading_delimiter, "、")


if __name__ == "__main__":
    unittest.main()
