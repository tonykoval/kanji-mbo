import sys
import os
import unittest
from unittest.mock import patch
from io import StringIO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import cli
from model import Kanji, Categorization, Constants


def _make_kanji(char, ref=None, keyword="", on_reading=None, kun_reading="",
                srl=3, type_val="MEAN", freq=500, group="",
                comp1="", comp2="", comp3="", comp4="", comp5=""):
    return Kanji(
        ref=ref or char, char=char,
        component1=comp1, component2=comp2, component3=comp3,
        component4=comp4, component5=comp5,
        on_reading=on_reading or [""], kun_reading=kun_reading,
        keyword=keyword, srl=srl, type=type_val, freq=freq,
        tags=[], group=group,
    )


class TestCliParser(unittest.TestCase):
    def test_no_command_exits(self):
        with patch('sys.argv', ['kanji-mbo']):
            with self.assertRaises(SystemExit):
                cli.main()

    def test_categorize_defaults(self):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--file", "-f", default="../excel/1500 KANJI COMPONENTS - ver. 1.3.xlsx")
        parser.add_argument("--log-level", "-l", default="INFO")
        parser.add_argument("--format", default="text")
        sub = parser.add_subparsers(dest="command")
        cat = sub.add_parser("categorize")
        cat.add_argument("--kanji", "-k", nargs="+")
        cat.add_argument("--subgroups", "-s", action="store_true")

        args = parser.parse_args(["categorize"])
        self.assertEqual(args.command, "categorize")
        self.assertIsNone(args.kanji)
        self.assertFalse(args.subgroups)
        self.assertEqual(args.log_level, "INFO")
        self.assertEqual(args.format, "text")

    def test_categorize_with_kanji(self):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--file", "-f", default="test.xlsx")
        parser.add_argument("--log-level", "-l", default="INFO")
        parser.add_argument("--format", default="text")
        sub = parser.add_subparsers(dest="command")
        cat = sub.add_parser("categorize")
        cat.add_argument("--kanji", "-k", nargs="+")
        cat.add_argument("--subgroups", "-s", action="store_true")

        args = parser.parse_args(["categorize", "-k", "青", "赤"])
        self.assertEqual(args.kanji, ["青", "赤"])

    def test_categorize_subgroups_flag(self):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--file", "-f", default="test.xlsx")
        parser.add_argument("--log-level", "-l", default="INFO")
        parser.add_argument("--format", default="text")
        sub = parser.add_subparsers(dest="command")
        cat = sub.add_parser("categorize")
        cat.add_argument("--kanji", "-k", nargs="+")
        cat.add_argument("--subgroups", "-s", action="store_true")

        args = parser.parse_args(["categorize", "--subgroups"])
        self.assertTrue(args.subgroups)

    def test_lookup_parses_kanji(self):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--file", "-f", default="test.xlsx")
        parser.add_argument("--log-level", "-l", default="INFO")
        parser.add_argument("--format", default="text")
        sub = parser.add_subparsers(dest="command")
        lookup = sub.add_parser("lookup")
        lookup.add_argument("kanji", nargs="+")

        args = parser.parse_args(["lookup", "青", "赤", "白"])
        self.assertEqual(args.command, "lookup")
        self.assertEqual(args.kanji, ["青", "赤", "白"])

    def test_custom_file_and_log_level(self):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--file", "-f", default="default.xlsx")
        parser.add_argument("--log-level", "-l", default="INFO")
        parser.add_argument("--format", default="text")
        sub = parser.add_subparsers(dest="command")
        sub.add_parser("categorize")

        args = parser.parse_args(["-f", "custom.xlsx", "-l", "WARNING", "categorize"])
        self.assertEqual(args.file, "custom.xlsx")
        self.assertEqual(args.log_level, "WARNING")

    def test_format_json_option(self):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--format", choices=["text", "json", "csv"], default="text")
        sub = parser.add_subparsers(dest="command")
        sub.add_parser("categorize")

        args = parser.parse_args(["--format", "json", "categorize"])
        self.assertEqual(args.format, "json")

    def test_format_csv_option(self):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--format", choices=["text", "json", "csv"], default="text")
        sub = parser.add_subparsers(dest="command")
        sub.add_parser("categorize")

        args = parser.parse_args(["--format", "csv", "categorize"])
        self.assertEqual(args.format, "csv")


class TestFormatFunctions(unittest.TestCase):
    def setUp(self):
        self.cat = Categorization()
        self.cat.result["group1"] = [
            _make_kanji("青", keyword="blue", on_reading=["セイ", "ショウ"], srl=3, freq=1205),
            _make_kanji("赤", keyword="red", on_reading=["セキ"], srl=2, freq=900),
        ]

    def test_format_categorize_json(self):
        import json
        output = cli._format_categorize_json(self.cat)
        data = json.loads(output)
        self.assertIn("group1", data)
        self.assertEqual(len(data["group1"]), 2)
        self.assertEqual(data["group1"][0]["char"], "青")  # sorted by ref desc

    def test_format_categorize_csv(self):
        output = cli._format_categorize_csv(self.cat)
        lines = output.strip().splitlines()
        self.assertEqual(lines[0].strip(), "group,char,ref,keyword,on_reading,srl,type,freq")
        self.assertEqual(len(lines), 3)  # header + 2 rows

    def test_format_lookup_json(self):
        import json
        kanji_list = self.cat.result["group1"]
        output = cli._format_lookup_json(kanji_list)
        data = json.loads(output)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["char"], "青")

    def test_format_lookup_csv(self):
        kanji_list = self.cat.result["group1"]
        output = cli._format_lookup_csv(kanji_list)
        lines = output.strip().splitlines()
        self.assertEqual(lines[0].strip(), "char,keyword,on_reading,kun_reading,components,srl,type,freq,group")
        self.assertEqual(len(lines), 3)

    def test_kanji_to_dict(self):
        k = _make_kanji("青", keyword="blue", on_reading=["セイ", "ショウ"],
                        comp1="月", comp2="土")
        d = cli._kanji_to_dict(k)
        self.assertEqual(d["char"], "青")
        self.assertEqual(d["on_reading"], "セイ、ショウ")
        self.assertEqual(d["components"], "月 土")


if __name__ == "__main__":
    unittest.main()
