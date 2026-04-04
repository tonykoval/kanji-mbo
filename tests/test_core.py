import sys
import os
import unittest
from dataclasses import dataclass
from typing import List

import pandas

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core import (
    is_empty_string,
    read_kanji_dataframe,
    find_kanji_on_reading,
    find_cluster_1_2_3_components,
)


@dataclass
class FakeKanji:
    char: str
    readings: List[str]


class TestIsEmptyString(unittest.TestCase):
    def test_non_empty(self):
        self.assertEqual(is_empty_string("hello"), "hello")

    def test_empty(self):
        self.assertIsNone(is_empty_string(""))

    def test_kanji(self):
        self.assertEqual(is_empty_string("青"), "青")


class TestReadKanjiDataframe(unittest.TestCase):
    def test_reads_all_rows(self):
        df = pandas.DataFrame({"col": ["a", "b", "c"]})
        result = read_kanji_dataframe(df, lambda row: row["col"])
        self.assertEqual(result, ["a", "b", "c"])

    def test_empty(self):
        df = pandas.DataFrame({"col": []})
        result = read_kanji_dataframe(df, lambda row: row["col"])
        self.assertEqual(result, [])


class TestFindKanjiOnReading(unittest.TestCase):
    def _get_readings(self, k):
        return k.readings

    def test_matching(self):
        target = FakeKanji("青", ["セイ", "ショウ"])
        cluster = [
            FakeKanji("清", ["セイ"]),
            FakeKanji("赤", ["セキ"]),
            FakeKanji("晴", ["セイ"]),
        ]
        result = find_kanji_on_reading(cluster, target, self._get_readings)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].char, "清")
        self.assertEqual(result[1].char, "晴")

    def test_no_match(self):
        target = FakeKanji("青", ["セイ"])
        cluster = [FakeKanji("赤", ["セキ"])]
        result = find_kanji_on_reading(cluster, target, self._get_readings)
        self.assertEqual(result, [])

    def test_empty_readings_excluded(self):
        target = FakeKanji("青", ["セイ"])
        cluster = [FakeKanji("某", [""])]
        result = find_kanji_on_reading(cluster, target, self._get_readings)
        self.assertEqual(result, [])

    def test_multiple_shared_readings(self):
        target = FakeKanji("生", ["セイ", "ショウ"])
        cluster = [FakeKanji("性", ["セイ", "ショウ"])]
        result = find_kanji_on_reading(cluster, target, self._get_readings)
        self.assertEqual(len(result), 1)


class TestFindCluster123Components(unittest.TestCase):
    def _make_df(self, rows):
        return pandas.DataFrame(rows, columns=["CHAR", "C1", "C2", "C3"])

    def test_finds_matching(self):
        df = self._make_df([
            ["青", "月", "", ""],
            ["清", "氵", "青", ""],
            ["晴", "日", "青", ""],
            ["赤", "", "", ""],
        ])
        result = find_cluster_1_2_3_components("青", "青", df, "CHAR", "C1", "C2", "C3")
        self.assertEqual(len(result), 2)
        chars = result["CHAR"].tolist()
        self.assertIn("清", chars)
        self.assertIn("晴", chars)

    def test_excludes_self(self):
        df = self._make_df([["青", "青", "", ""]])
        result = find_cluster_1_2_3_components("青", "青", df, "CHAR", "C1", "C2", "C3")
        self.assertEqual(len(result), 0)

    def test_matches_in_comp3(self):
        df = self._make_df([["漢", "", "", "青"]])
        result = find_cluster_1_2_3_components("青", "青", df, "CHAR", "C1", "C2", "C3")
        self.assertEqual(len(result), 1)

    def test_empty_dataframe(self):
        df = self._make_df([])
        result = find_cluster_1_2_3_components("青", "青", df, "CHAR", "C1", "C2", "C3")
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()
