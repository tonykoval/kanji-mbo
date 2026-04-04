import sys
import os
import unittest

import pandas

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from model import Kanji, Source, Categorization, Constants, ExcelColumn, Stem
import algorithm


def make_kanji(char, ref=None, srl=3, on_reading=None, keyword="", type_val="MEAN",
               freq=500, group="", component1="", component2="", component3="",
               component4="", component5=""):
    return Kanji(
        ref=ref or char,
        char=char,
        component1=component1,
        component2=component2,
        component3=component3,
        component4=component4,
        component5=component5,
        on_reading=on_reading or [""],
        kun_reading="",
        keyword=keyword,
        srl=srl,
        type=type_val,
        freq=freq,
        tags=[],
        group=group,
    )


def make_source(kanji_rows, keyword_rows=None, stem_rows=None, special_rows=None):
    df_kanji = pandas.DataFrame(kanji_rows, columns=ExcelColumn.list_columns)
    df_kanji.fillna('', inplace=True)

    keyword_cols = [ExcelColumn.keyword, ExcelColumn.group]
    df_keyword = pandas.DataFrame(keyword_rows or [], columns=keyword_cols)

    stem_cols = [ExcelColumn.stem_kanji, ExcelColumn.stem_component1,
                 ExcelColumn.stem_component2, ExcelColumn.stem_component3,
                 ExcelColumn.stem_component4, ExcelColumn.stem_component5,
                 ExcelColumn.stem_component6, ExcelColumn.group]
    df_stem = pandas.DataFrame(stem_rows or [], columns=stem_cols)
    df_stem.fillna('', inplace=True)

    special_cols = [ExcelColumn.kanji, ExcelColumn.key]
    df_special = pandas.DataFrame(special_rows or [], columns=special_cols)
    df_special.fillna('', inplace=True)

    return Source(df_kanji, df_keyword, df_stem, df_special)


def make_kanji_row(char, comp1="", comp2="", comp3="", comp4="", comp5="",
                   on_reading="", kun_reading="", keyword="", srl=3,
                   type_val="MEAN", freq=500, tags="", group=""):
    return [char, comp1, comp2, comp3, comp4, comp5,
            on_reading, kun_reading, keyword, srl, type_val, freq, tags, group]


class TestIsEmptyString(unittest.TestCase):
    def test_non_empty_returns_value(self):
        self.assertEqual(algorithm.is_empty_string("hello"), "hello")

    def test_empty_returns_none(self):
        self.assertIsNone(algorithm.is_empty_string(""))

    def test_kanji_returns_value(self):
        self.assertEqual(algorithm.is_empty_string("青"), "青")


class TestAddToQueue(unittest.TestCase):
    def test_adds_to_new_key(self):
        cat = Categorization(result={}, queue={})
        k = make_kanji("清")
        algorithm.add_to_queue(k, "青", cat)
        self.assertIn("青", cat.queue)
        self.assertEqual(len(cat.queue["青"]), 1)
        self.assertEqual(cat.queue["青"][0].char, "清")
        self.assertEqual(k.ref, "青")

    def test_appends_to_existing_key(self):
        cat = Categorization(result={}, queue={"青": [make_kanji("晴")]})
        k = make_kanji("清")
        algorithm.add_to_queue(k, "青", cat)
        self.assertEqual(len(cat.queue["青"]), 2)

    def test_sets_ref_on_kanji(self):
        cat = Categorization(result={}, queue={})
        k = make_kanji("請", ref="請")
        algorithm.add_to_queue(k, "青", cat)
        self.assertEqual(k.ref, "青")


class TestFindKeyword(unittest.TestCase):
    def test_found(self):
        source = make_source(
            kanji_rows=[make_kanji_row("百", keyword="hundred")],
            keyword_rows=[["hundred", "01 numbers"]],
        )
        k = make_kanji("百", keyword="hundred")
        self.assertEqual(algorithm.find_keyword(k, source), "01 numbers")

    def test_not_found(self):
        source = make_source(
            kanji_rows=[make_kanji_row("麻")],
            keyword_rows=[["hundred", "01 numbers"]],
        )
        k = make_kanji("麻", keyword="hemp")
        self.assertIsNone(algorithm.find_keyword(k, source))


class TestFindStem(unittest.TestCase):
    def test_found(self):
        source = make_source(
            kanji_rows=[make_kanji_row("水")],
            stem_rows=[["水", "", "", "", "", "", "", "08 Wednesday"]],
        )
        k = make_kanji("水")
        self.assertEqual(algorithm.find_stem(k, source), "08 Wednesday")

    def test_not_found(self):
        source = make_source(
            kanji_rows=[make_kanji_row("清")],
            stem_rows=[["水", "", "", "", "", "", "", "08 Wednesday"]],
        )
        k = make_kanji("清")
        self.assertIsNone(algorithm.find_stem(k, source))


class TestFindSpecial(unittest.TestCase):
    def test_found(self):
        source = make_source(
            kanji_rows=[make_kanji_row("麻")],
            special_rows=[["麻", "摩"]],
        )
        k = make_kanji("麻")
        self.assertEqual(algorithm.find_special(k, source), Constants.special_grp)

    def test_not_found(self):
        source = make_source(
            kanji_rows=[make_kanji_row("百")],
            special_rows=[["麻", "摩"]],
        )
        k = make_kanji("百")
        self.assertIsNone(algorithm.find_special(k, source))


class TestReadKanji(unittest.TestCase):
    def test_read_kanji_from_row(self):
        row = pandas.Series({
            ExcelColumn.char: "青",
            ExcelColumn.component1: "月",
            ExcelColumn.component2: "",
            ExcelColumn.component3: "",
            ExcelColumn.component4: "",
            ExcelColumn.component5: "",
            ExcelColumn.on_reading: "セイ、ショウ",
            ExcelColumn.kun_reading: "あお",
            ExcelColumn.keyword: "blue",
            ExcelColumn.srl: 3,
            ExcelColumn.type: "MEAN",
            ExcelColumn.freq: 1205,
            ExcelColumn.tags: "",
            ExcelColumn.group: "3a",
        })
        k = algorithm.read_kanji(row)
        self.assertEqual(k.char, "青")
        self.assertEqual(k.ref, "青")
        self.assertEqual(k.component1, "月")
        self.assertEqual(k.on_reading, ["セイ", "ショウ"])
        self.assertEqual(k.srl, 3)
        self.assertEqual(k.freq, 1205)

    def test_read_kanji_single_on_reading(self):
        row = pandas.Series({
            ExcelColumn.char: "百",
            ExcelColumn.component1: "",
            ExcelColumn.component2: "",
            ExcelColumn.component3: "",
            ExcelColumn.component4: "",
            ExcelColumn.component5: "",
            ExcelColumn.on_reading: "ヒャク",
            ExcelColumn.kun_reading: "",
            ExcelColumn.keyword: "hundred",
            ExcelColumn.srl: 3,
            ExcelColumn.type: "MEAN",
            ExcelColumn.freq: 100,
            ExcelColumn.tags: "",
            ExcelColumn.group: "1a",
        })
        k = algorithm.read_kanji(row)
        self.assertEqual(k.on_reading, ["ヒャク"])


class TestReadKanjiChar(unittest.TestCase):
    def test_lookup_by_char(self):
        source = make_source(
            kanji_rows=[
                make_kanji_row("百", on_reading="ヒャク", keyword="hundred", srl=3, freq=100, group="1a"),
                make_kanji_row("青", comp1="月", on_reading="セイ、ショウ", keyword="blue", srl=3, freq=1205, group="3a"),
            ],
        )
        k = algorithm.read_kanji_char("青", source)
        self.assertEqual(k.char, "青")
        self.assertEqual(k.keyword, "blue")

    def test_lookup_nonexistent_raises(self):
        source = make_source(kanji_rows=[make_kanji_row("百")])
        with self.assertRaises(IndexError):
            algorithm.read_kanji_char("龍", source)


class TestReadKanjiDataframe(unittest.TestCase):
    def test_reads_all_rows(self):
        source = make_source(
            kanji_rows=[
                make_kanji_row("百", on_reading="ヒャク"),
                make_kanji_row("青", on_reading="セイ"),
                make_kanji_row("赤", on_reading="セキ"),
            ],
        )
        result = algorithm.read_kanji_dataframe(source.df_kanji)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].char, "百")
        self.assertEqual(result[2].char, "赤")

    def test_empty_dataframe(self):
        source = make_source(kanji_rows=[])
        result = algorithm.read_kanji_dataframe(source.df_kanji)
        self.assertEqual(result, [])


class TestFindKanjiOnReading(unittest.TestCase):
    def test_matching_on_reading(self):
        target = make_kanji("青", on_reading=["セイ", "ショウ"])
        cluster = [
            make_kanji("清", on_reading=["セイ"]),
            make_kanji("赤", on_reading=["セキ"]),
            make_kanji("晴", on_reading=["セイ"]),
        ]
        result = algorithm.find_kanji_on_reading(cluster, target)
        self.assertEqual(len(result), 2)
        chars = [k.char for k in result]
        self.assertIn("清", chars)
        self.assertIn("晴", chars)

    def test_no_match(self):
        target = make_kanji("青", on_reading=["セイ"])
        cluster = [make_kanji("赤", on_reading=["セキ"])]
        result = algorithm.find_kanji_on_reading(cluster, target)
        self.assertEqual(result, [])

    def test_empty_on_reading_excluded(self):
        target = make_kanji("青", on_reading=["セイ"])
        cluster = [make_kanji("某", on_reading=[""])]
        result = algorithm.find_kanji_on_reading(cluster, target)
        self.assertEqual(result, [])


class TestFindMaxSrlKanji(unittest.TestCase):
    def test_single_kanji(self):
        kanji = [make_kanji("青", srl=3)]
        result = algorithm.find_max_srl_kanji(kanji)
        self.assertEqual(result.char, "青")

    def test_multiple_returns_highest(self):
        kanji = [
            make_kanji("清", srl=1),
            make_kanji("青", srl=5),
            make_kanji("晴", srl=3),
        ]
        result = algorithm.find_max_srl_kanji(kanji)
        self.assertEqual(result.char, "青")

    def test_equal_srl_returns_first_encountered(self):
        kanji = [
            make_kanji("清", srl=3),
            make_kanji("晴", srl=3),
        ]
        result = algorithm.find_max_srl_kanji(kanji)
        self.assertEqual(result.char, "清")


class TestFindMaxSrl(unittest.TestCase):
    def test_returns_row_with_max_srl(self):
        df = pandas.DataFrame([
            make_kanji_row("清", srl=1),
            make_kanji_row("青", srl=5),
            make_kanji_row("晴", srl=3),
        ], columns=ExcelColumn.list_columns)
        result = algorithm.find_max_srl(df)
        self.assertEqual(result[ExcelColumn.char], "青")


class TestFindStemVariations(unittest.TestCase):
    def test_found_in_stem_component1(self):
        source = make_source(
            kanji_rows=[],
            stem_rows=[["水", "氵", "氺", "", "", "", "", "08 Wednesday"]],
        )
        result = algorithm.find_stem_variations("氵", source, 3)
        self.assertIsNotNone(result)
        self.assertEqual(result.group, "08 Wednesday")
        self.assertEqual(result.priority, 3)

    def test_not_found(self):
        source = make_source(
            kanji_rows=[],
            stem_rows=[["水", "氵", "", "", "", "", "", "08 Wednesday"]],
        )
        result = algorithm.find_stem_variations("火", source, 2)
        self.assertIsNone(result)

    def test_empty_string_returns_none(self):
        source = make_source(kanji_rows=[], stem_rows=[])
        result = algorithm.find_stem_variations("", source, 1)
        self.assertIsNone(result)


class TestFindMaxStem(unittest.TestCase):
    def test_returns_highest_priority(self):
        stems = [
            Stem("a", 1),
            Stem("b", 3),
            Stem("c", 2),
        ]
        result = algorithm.find_max_stem(stems)
        self.assertEqual(result.group, "b")

    def test_with_nones(self):
        stems = [None, Stem("a", 2), None]
        result = algorithm.find_max_stem(stems)
        self.assertEqual(result.group, "a")

    def test_all_none(self):
        result = algorithm.find_max_stem([None, None, None])
        self.assertIsNone(result)


class TestFindCluster123Components(unittest.TestCase):
    def test_finds_matching_components(self):
        source = make_source(
            kanji_rows=[
                make_kanji_row("青", comp1="月"),
                make_kanji_row("清", comp1="氵", comp2="青"),
                make_kanji_row("晴", comp1="日", comp2="青"),
                make_kanji_row("赤"),
            ],
        )
        k = make_kanji("青")
        result = algorithm.find_cluster_1_2_3_components("青", k, source)
        self.assertEqual(len(result), 2)
        chars = result[ExcelColumn.char].tolist()
        self.assertIn("清", chars)
        self.assertIn("晴", chars)

    def test_excludes_self(self):
        source = make_source(
            kanji_rows=[
                make_kanji_row("青", comp1="青"),
                make_kanji_row("清", comp2="青"),
            ],
        )
        k = make_kanji("青")
        result = algorithm.find_cluster_1_2_3_components("青", k, source)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0][ExcelColumn.char], "清")


class TestAppendCategorization(unittest.TestCase):
    def test_append_not_first(self):
        cat = Categorization(result={"group": []}, queue={})
        k = make_kanji("百")
        algorithm.append_categorization("group", k, False, cat)
        self.assertEqual(len(cat.result["group"]), 1)
        self.assertEqual(cat.result["group"][0].char, "百")

    def test_append_first_inserts_at_start(self):
        existing = make_kanji("四")
        cat = Categorization(result={"group": [existing]}, queue={})
        k = make_kanji("百")
        algorithm.append_categorization("group", k, True, cat)
        self.assertEqual(cat.result["group"][0].char, "百")

    def test_flush_queue_on_append(self):
        queued = make_kanji("汁", ref="十")
        cat = Categorization(result={"group": []}, queue={"十": [queued]})
        k = make_kanji("十")
        algorithm.append_categorization("group", k, False, cat)
        self.assertEqual(len(cat.result["group"]), 2)
        self.assertNotIn("十", cat.queue)


class TestCategorizeKanjiRule1(unittest.TestCase):
    def test_keyword_mean_assigns_to_group(self):
        source = make_source(
            kanji_rows=[make_kanji_row("百", on_reading="ヒャク", keyword="hundred", type_val="MEAN")],
            keyword_rows=[["hundred", "01 numbers"]],
        )
        cat = Categorization(result={"01 numbers": [], Constants.other_grp: []}, queue={})
        k = make_kanji("百", keyword="hundred", type_val=Constants.mean)
        algorithm.categorize_kanji(k, cat, source)
        self.assertEqual(len(cat.result["01 numbers"]), 1)
        self.assertEqual(cat.result["01 numbers"][0].char, "百")

    def test_keyword_other_assigns_to_other(self):
        source = make_source(
            kanji_rows=[make_kanji_row("某", keyword="certain", type_val="OTHER")],
            keyword_rows=[["certain", "21 talk"]],
        )
        cat = Categorization(result={"21 talk": [], Constants.other_grp: []}, queue={})
        k = make_kanji("某", keyword="certain", type_val=Constants.other)
        algorithm.categorize_kanji(k, cat, source)
        self.assertEqual(len(cat.result[Constants.other_grp]), 1)


class TestCategorizeKanjiRule2(unittest.TestCase):
    def test_stem_assigns_first_in_group(self):
        source = make_source(
            kanji_rows=[make_kanji_row("水", on_reading="スイ", type_val="STEM")],
            stem_rows=[["水", "", "", "", "", "", "", "08 Wednesday"]],
        )
        existing = make_kanji("海")
        cat = Categorization(result={"08 Wednesday": [existing]}, queue={})
        k = make_kanji("水", type_val=Constants.stem)
        algorithm.categorize_kanji(k, cat, source)
        self.assertEqual(cat.result["08 Wednesday"][0].char, "水")


class TestSeventhRule(unittest.TestCase):
    def test_assigns_to_other(self):
        cat = Categorization(result={Constants.other_grp: []}, queue={})
        k = make_kanji("某")
        algorithm.seventh_rule(k, cat)
        self.assertEqual(len(cat.result[Constants.other_grp]), 1)
        self.assertEqual(cat.result[Constants.other_grp][0].char, "某")


class TestCategorizeSrl(unittest.TestCase):
    def test_single_row_queues(self):
        source = make_source(kanji_rows=[make_kanji_row("青", srl=5)])
        cat = Categorization(result={}, queue={})
        df = source.df_kanji
        k = make_kanji("清", srl=1)
        algorithm.categorize_srl(df, k, cat, source, Constants.visual)
        self.assertEqual(k.type, Constants.visual)
        self.assertIn("青", cat.queue)

    def test_multiple_rows_uses_max_srl(self):
        source = make_source(
            kanji_rows=[
                make_kanji_row("晴", srl=2),
                make_kanji_row("青", srl=5),
            ],
        )
        cat = Categorization(result={}, queue={})
        k = make_kanji("清", srl=1)
        algorithm.categorize_srl(source.df_kanji, k, cat, source, Constants.visual)
        self.assertIn("青", cat.queue)


class TestInitCategorization(unittest.TestCase):
    def test_creates_groups_from_keyword_and_stem(self):
        source = make_source(
            kanji_rows=[make_kanji_row("百", on_reading="ヒャク")],
            keyword_rows=[["hundred", "01 numbers"], ["blue", "03 colors"]],
            stem_rows=[["水", "", "", "", "", "", "", "08 Wednesday"]],
        )
        cat = algorithm.init_categorization(source)
        self.assertIn("01 numbers", cat.result)
        self.assertIn("03 colors", cat.result)
        self.assertIn("08 Wednesday", cat.result)
        self.assertIn(Constants.other_grp, cat.result)
        self.assertIn(Constants.special_grp, cat.result)

    def test_creates_queue_from_special(self):
        source = make_source(
            kanji_rows=[make_kanji_row("麻", on_reading="マ")],
            special_rows=[["麻", "摩"]],
        )
        cat = algorithm.init_categorization(source)
        self.assertIn("摩", cat.queue)
        self.assertEqual(cat.queue["摩"][0].char, "麻")


if __name__ == "__main__":
    unittest.main()
