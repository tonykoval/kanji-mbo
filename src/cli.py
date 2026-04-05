import argparse
import csv
import io
import json
import logging
import sys
from collections import defaultdict
from dataclasses import asdict

import algorithm


def _kanji_to_dict(kanji):
    d = asdict(kanji)
    d["on_reading"] = kanji.on_reading_str
    d["components"] = kanji.components_str
    return d


def _format_categorize_json(categorization):
    output = {}
    for key in sorted(categorization.result):
        output[key] = [
            _kanji_to_dict(k)
            for k in sorted(categorization.result[key], key=lambda x: x.ref, reverse=True)
        ]
    return json.dumps(output, ensure_ascii=False, indent=2)


def _format_categorize_csv(categorization):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["group", "char", "ref", "keyword", "on_reading", "srl", "type", "freq"])
    for key in sorted(categorization.result):
        for k in sorted(categorization.result[key], key=lambda x: x.ref, reverse=True):
            writer.writerow([key, k.char, k.ref, k.keyword,
                             k.on_reading_str, k.srl, k.type, k.freq])
    return buf.getvalue()


def _format_lookup_json(kanji_list):
    return json.dumps([_kanji_to_dict(k) for k in kanji_list], ensure_ascii=False, indent=2)


def _format_lookup_csv(kanji_list):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["char", "keyword", "on_reading", "kun_reading", "components", "srl", "type", "freq", "group"])
    for k in kanji_list:
        writer.writerow([k.char, k.keyword, k.on_reading_str, k.kun_reading,
                         k.components_str, k.srl, k.type, k.freq, k.group])
    return buf.getvalue()


def run_categorize(args):
    algorithm.set_logging_level(getattr(logging, args.log_level))
    source = algorithm.read_excel(args.file)
    categorization = algorithm.init_categorization(source)

    if args.kanji:
        for char in args.kanji:
            kanji = algorithm.read_kanji_char(char, source)
            algorithm.categorize_kanji(kanji, categorization, source)
            print("-----------------")
    else:
        for kanji in algorithm.read_kanji_dataframe(source.df_kanji):
            algorithm.categorize_kanji(kanji, categorization, source)
            print("-----------------")

    algorithm.categorize_queue(categorization)

    fmt = getattr(args, "format", "text")
    if fmt == "json":
        print(_format_categorize_json(categorization))
    elif fmt == "csv":
        print(_format_categorize_csv(categorization), end="")
    elif args.subgroups:
        print("subgroup categorization")
        for key in sorted(categorization.result):
            print(key)
            res = defaultdict(list)
            for kanji in sorted(categorization.result[key], key=lambda x: x.ref, reverse=True):
                kanji_group = kanji.group if kanji.group != '' else "companion"
                res[kanji_group].append(kanji.char)
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

    kanji_list = [algorithm.read_kanji_char(char, source) for char in args.kanji]

    fmt = getattr(args, "format", "text")
    if fmt == "json":
        print(_format_lookup_json(kanji_list))
    elif fmt == "csv":
        print(_format_lookup_csv(kanji_list), end="")
    else:
        for kanji in kanji_list:
            print(f"Character:   {kanji.char}")
            print(f"Keyword:     {kanji.keyword}")
            print(f"On'yomi:     {kanji.on_reading_str}")
            print(f"Kun'yomi:    {kanji.kun_reading}")
            print(f"Components:  {kanji.components_str}")
            print(f"SRL:         {kanji.srl}")
            print(f"Type:        {kanji.type}")
            print(f"Frequency:   {kanji.freq}")
            print(f"Group:       {kanji.group}")
            print("-----------------")


def run_freq(args):
    from operator import attrgetter
    from disjoint_set import DisjointSet
    import freq_algorithm

    freq_algorithm.set_logging_level(getattr(logging, args.log_level))
    df = freq_algorithm.read_excel(args.file)
    list_kanji = freq_algorithm.read_kanji_dataframe(df)

    result = []
    for kanji in list_kanji:
        freq_algorithm.categorize_kanji(kanji, result, list_kanji)

    ds = DisjointSet()
    for k in result:
        ds.union(k.char, k.ref)

    # Collect ranked kanji from groups
    ranked = []
    for group in ds.itersets(with_canonical_elements=False):
        group_kanji = sorted(
            [k for k in list_kanji if k.char in group],
            key=attrgetter('freq')
        )
        ranked.extend(group_kanji)

    fmt = getattr(args, "format", "text")
    if fmt == "json":
        output = [{"rank": i + 1, "char": k.char, "keyword": k.keyword,
                    "onyomi": "\u3001".join(k.onyomi), "freq": k.freq, "ref": k.ref}
                   for i, k in enumerate(ranked)]
        print(json.dumps(output, ensure_ascii=False, indent=2))
    elif fmt == "csv":
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["rank", "char", "keyword", "onyomi", "freq", "ref"])
        for i, k in enumerate(ranked):
            writer.writerow([i + 1, k.char, k.keyword, "\u3001".join(k.onyomi), k.freq, k.ref])
        print(buf.getvalue(), end="")
    else:
        for i, k in enumerate(ranked):
            print(f"{i + 1}: {k.char}")


def run_anki(args):
    categorization, _ = algorithm.run_pipeline(args.file)

    from anki_export import export_categorization
    path = export_categorization(categorization, args.output, args.deck_name)
    total = sum(len(v) for v in categorization.result.values())
    print(f"Exported {total} kanji to {path}")


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
    parser.add_argument(
        "--format",
        choices=["text", "json", "csv"],
        default="text",
        help="output format (default: text)"
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

    # freq command (frequency-based grouping pipeline)
    freq_parser = subparsers.add_parser("freq", help="frequency-based kanji grouping")
    freq_parser.add_argument(
        "--file", "-f",
        default="../excel/1,200 KANJI.xlsx",
        dest="file",
        help="path to the frequency Excel data file"
    )

    # anki command (export to Anki deck)
    anki_parser = subparsers.add_parser("anki", help="export categorization to Anki .apkg deck")
    anki_parser.add_argument(
        "--output", "-o",
        default="kanji_mbo.apkg",
        help="output .apkg file path (default: kanji_mbo.apkg)"
    )
    anki_parser.add_argument(
        "--deck-name",
        default="Kanji MBO",
        help="Anki deck name (default: Kanji MBO)"
    )

    args = parser.parse_args()

    if args.command == "categorize":
        run_categorize(args)
    elif args.command == "lookup":
        run_lookup(args)
    elif args.command == "freq":
        run_freq(args)
    elif args.command == "anki":
        run_anki(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
