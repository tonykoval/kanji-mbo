import sys
import os
import importlib
import unittest

import pandas

# Save original module state so we can restore after importing freq versions
_saved_model = sys.modules.pop('model', None)
_saved_algorithm = sys.modules.pop('algorithm', None)

freq_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'freq')
sys.path.insert(0, freq_path)

import model as freq_model
import algorithm as freq_algorithm

# Stash freq modules under unique keys and restore originals
sys.modules['freq_model'] = freq_model
sys.modules['freq_algorithm'] = freq_algorithm
del sys.modules['model']
del sys.modules['algorithm']
sys.path.remove(freq_path)

if _saved_model is not None:
    sys.modules['model'] = _saved_model
if _saved_algorithm is not None:
    sys.modules['algorithm'] = _saved_algorithm

Kanji = freq_model.Kanji
ExcelColumn = freq_model.ExcelColumn
algorithm = freq_algorithm


def make_kanji(char, ref=None, comp1="", comp2="", comp3="",
               onyomi=None, kunyomi="", keyword="", freq=500):
    return Kanji(
        ref=ref or char,
        char=char,
        component1=comp1,
        component2=comp2,
        component3=comp3,
        onyomi=onyomi or [""],
        kunyomi=kunyomi,
        keyword=keyword,
        freq=freq,
    )


def make_dataframe(rows):
    df = pandas.DataFrame(rows, columns=ExcelColumn.list_columns)
    df.fillna('', inplace=True)
    return df


def make_row(char, comp1="", comp2="", comp3="", onyomi="", kunyomi="", keyword="", freq=500):
    return [char, comp1, comp2, comp3, onyomi, kunyomi, keyword, freq]


class TestIsEmptyString(unittest.TestCase):
    def test_non_empty(self):
        self.assertEqual(algorithm.is_empty_string("test"), "test")

    def test_empty(self):
        self.assertIsNone(algorithm.is_empty_string(""))


class TestReadKanji(unittest.TestCase):
    def test_read_basic(self):
        df = make_dataframe([make_row("時", comp1="日", comp2="寺", onyomi="ジ", freq=26)])
        k = algorithm.read_kanji(df.iloc[0])
        self.assertEqual(k.char, "時")
        self.assertEqual(k.ref, "時")
        self.assertEqual(k.component1, "日")
        self.assertEqual(k.component2, "寺")
        self.assertEqual(k.onyomi, ["ジ"])
        self.assertEqual(k.freq, 26)

    def test_read_multiple_onyomi(self):
        df = make_dataframe([make_row("生", onyomi="セイ、ショウ")])
        k = algorithm.read_kanji(df.iloc[0])
        self.assertEqual(k.onyomi, ["セイ", "ショウ"])


class TestReadKanjiDataframe(unittest.TestCase):
    def test_reads_all(self):
        df = make_dataframe([
            make_row("人", onyomi="ジン"),
            make_row("日", onyomi="ニチ"),
            make_row("大", onyomi="ダイ"),
        ])
        result = algorithm.read_kanji_dataframe(df)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].char, "人")
        self.assertEqual(result[2].char, "大")

    def test_empty(self):
        df = make_dataframe([])
        result = algorithm.read_kanji_dataframe(df)
        self.assertEqual(result, [])


class TestFindKanjiOnReading(unittest.TestCase):
    def test_matching(self):
        target = make_kanji("中", onyomi=["チュウ"])
        cluster = [
            make_kanji("仲", onyomi=["チュウ"]),
            make_kanji("忠", onyomi=["チュウ"]),
            make_kanji("虫", onyomi=["チュウ"]),
            make_kanji("赤", onyomi=["セキ"]),
        ]
        result = algorithm.find_kanji_on_reading(cluster, target)
        self.assertEqual(len(result), 3)

    def test_no_match(self):
        target = make_kanji("中", onyomi=["チュウ"])
        cluster = [make_kanji("赤", onyomi=["セキ"])]
        result = algorithm.find_kanji_on_reading(cluster, target)
        self.assertEqual(result, [])

    def test_empty_onyomi_excluded(self):
        target = make_kanji("中", onyomi=["チュウ"])
        cluster = [make_kanji("某", onyomi=[""])]
        result = algorithm.find_kanji_on_reading(cluster, target)
        self.assertEqual(result, [])


class TestCategorizeKanji(unittest.TestCase):
    def test_no_components_self_reference(self):
        k = make_kanji("人", onyomi=["ジン"], freq=1)
        list_kanji = [k]
        result = []
        algorithm.categorize_kanji(k, result, list_kanji)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].char, "人")
        self.assertEqual(result[0].ref, "人")

    def test_with_onyomi_match_sets_ref_to_lowest_freq(self):
        k_time = make_kanji("時", comp2="寺", onyomi=["ジ"], freq=26)
        k_hold = make_kanji("持", comp2="寺", onyomi=["ジ"], freq=142)
        k_temple = make_kanji("寺", comp2="寺", onyomi=["ジ"], freq=650)
        list_kanji = [k_time, k_hold, k_temple]
        result = []
        algorithm.categorize_kanji(k_time, result, list_kanji)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].ref, "時")

    def test_no_onyomi_match_self_reference(self):
        k = make_kanji("出", comp2="山", onyomi=["シュツ"], freq=5)
        k2 = make_kanji("山", comp2="山", onyomi=["サン"], freq=400)
        list_kanji = [k, k2]
        result = []
        algorithm.categorize_kanji(k, result, list_kanji)
        self.assertEqual(result[0].ref, "出")

    def test_empty_components_no_match(self):
        k = make_kanji("一", onyomi=["イチ"], freq=3)
        list_kanji = [k]
        result = []
        algorithm.categorize_kanji(k, result, list_kanji)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].ref, "一")


class TestFindCluster123Components(unittest.TestCase):
    def _make_source(self, rows):
        df = make_dataframe(rows)
        return type('Source', (), {'df_kanji': df})()

    def test_finds_by_component(self):
        source = self._make_source([
            make_row("青", comp1="月"),
            make_row("清", comp1="氵", comp2="青"),
            make_row("晴", comp1="日", comp2="青"),
        ])
        k = make_kanji("青")
        result = algorithm.find_cluster_1_2_3_components("青", k, source)
        self.assertEqual(len(result), 2)

    def test_excludes_self(self):
        source = self._make_source([
            make_row("青", comp1="青"),
        ])
        k = make_kanji("青")
        result = algorithm.find_cluster_1_2_3_components("青", k, source)
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()
