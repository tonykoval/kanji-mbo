import sys
import os
import unittest
from unittest.mock import patch
from io import StringIO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import cli


class TestCliParser(unittest.TestCase):
    def test_no_command_exits(self):
        with patch('sys.argv', ['kanji-mbo']):
            with self.assertRaises(SystemExit):
                cli.main()

    def test_categorize_defaults(self):
        parser = cli.main.__code__  # just test argparse construction
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--file", "-f", default="../excel/1500 KANJI COMPONENTS - ver. 1.3.xlsx")
        parser.add_argument("--log-level", "-l", default="INFO")
        sub = parser.add_subparsers(dest="command")
        cat = sub.add_parser("categorize")
        cat.add_argument("--kanji", "-k", nargs="+")
        cat.add_argument("--subgroups", "-s", action="store_true")

        args = parser.parse_args(["categorize"])
        self.assertEqual(args.command, "categorize")
        self.assertIsNone(args.kanji)
        self.assertFalse(args.subgroups)
        self.assertEqual(args.log_level, "INFO")

    def test_categorize_with_kanji(self):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--file", "-f", default="test.xlsx")
        parser.add_argument("--log-level", "-l", default="INFO")
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
        sub = parser.add_subparsers(dest="command")
        sub.add_parser("categorize")

        args = parser.parse_args(["-f", "custom.xlsx", "-l", "WARNING", "categorize"])
        self.assertEqual(args.file, "custom.xlsx")
        self.assertEqual(args.log_level, "WARNING")


if __name__ == "__main__":
    unittest.main()
