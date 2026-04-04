import argparse
import logging
import sys

import algorithm


def run_categorize(args):
    algorithm.set_logging_level(getattr(logging, args.log_level))
    source = algorithm.read_excel(args.file)
    categorization = algorithm.init_categorization(source)

    if args.kanji:
        for char in args.kanji:
            row = algorithm.read_kanji_char(char, source)
            algorithm.categorize_kanji(row, categorization, source)
            print("-----------------")
    else:
        for i in range(len(source.df_kanji)):
            row = algorithm.read_kanji(source.df_kanji.loc[i])
            algorithm.categorize_kanji(row, categorization, source)
            print("-----------------")

    algorithm.categorize_queue(categorization)

    if args.subgroups:
        print("subgroup categorization")
        for key in dict(sorted(categorization.result.items())):
            print(key)
            res = {}
            for kanji in sorted(categorization.result[key], key=lambda x: x.ref, reverse=True):
                kanji_group = kanji.group if kanji.group != '' else "companion"
                if kanji_group in res:
                    res[kanji_group].append(kanji.char)
                else:
                    res[kanji_group] = [kanji.char]
            print(dict(sorted(res.items())))
    else:
        print("categorization")
        for key in categorization.result:
            print(key)
            for kanji in sorted(categorization.result[key], key=lambda x: x.ref, reverse=True):
                print(kanji.char, " (", kanji.ref, ")")


def run_lookup(args):
    algorithm.set_logging_level(logging.WARNING)
    source = algorithm.read_excel(args.file)

    for char in args.kanji:
        kanji = algorithm.read_kanji_char(char, source)
        print(f"Character:   {kanji.char}")
        print(f"Keyword:     {kanji.keyword}")
        print(f"On'yomi:     {'、'.join(kanji.on_reading)}")
        print(f"Kun'yomi:    {kanji.kun_reading}")
        print(f"Components:  {' '.join(filter(None, [kanji.component1, kanji.component2, kanji.component3, kanji.component4, kanji.component5]))}")
        print(f"SRL:         {kanji.srl}")
        print(f"Type:        {kanji.type}")
        print(f"Frequency:   {kanji.freq}")
        print(f"Group:       {kanji.group}")
        print("-----------------")


def main():
    parser = argparse.ArgumentParser(
        prog="kanji-mbo",
        description="Kanji categorization by meaning, reading, and component similarity"
    )
    parser.add_argument(
        "--file", "-f",
        default="../excel/1500 KANJI COMPONENTS - ver. 1.3.xlsx",
        help="path to the Excel data file"
    )
    parser.add_argument(
        "--log-level", "-l",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="logging level (default: INFO)"
    )

    subparsers = parser.add_subparsers(dest="command", help="available commands")

    # categorize command
    cat_parser = subparsers.add_parser("categorize", help="run full categorization pipeline")
    cat_parser.add_argument(
        "--kanji", "-k",
        nargs="+",
        help="specific kanji to categorize (default: all)"
    )
    cat_parser.add_argument(
        "--subgroups", "-s",
        action="store_true",
        help="show subgroup breakdown instead of flat list"
    )

    # lookup command
    lookup_parser = subparsers.add_parser("lookup", help="look up kanji data")
    lookup_parser.add_argument(
        "kanji",
        nargs="+",
        help="kanji characters to look up"
    )

    args = parser.parse_args()

    if args.command == "categorize":
        run_categorize(args)
    elif args.command == "lookup":
        run_lookup(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
