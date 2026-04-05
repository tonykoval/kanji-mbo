"""Data loading module — reads Excel files and converts rows to domain objects."""

from typing import List

import pandas

from model import Source, Kanji, ExcelColumn


def read_kanji(row: pandas.Series) -> Kanji:
    return Kanji(
        ref=row[ExcelColumn.char],
        char=row[ExcelColumn.char],
        component1=row[ExcelColumn.component1],
        component2=row[ExcelColumn.component2],
        component3=row[ExcelColumn.component3],
        component4=row[ExcelColumn.component4],
        component5=row[ExcelColumn.component5],
        on_reading=row[ExcelColumn.on_reading].split(ExcelColumn.on_reading_delimiter),
        kun_reading=row[ExcelColumn.kun_reading],
        keyword=row[ExcelColumn.keyword],
        srl=int(row[ExcelColumn.srl]),
        type=row[ExcelColumn.type],
        freq=int(row[ExcelColumn.freq]),
        tags=list(row[ExcelColumn.tags]),
        group=row[ExcelColumn.group],
    )


def read_kanji_dataframe(dataframe: pandas.DataFrame) -> List[Kanji]:
    return [read_kanji(dataframe.iloc[i]) for i in range(len(dataframe.index))]


def read_kanji_char(char: str, source: Source) -> Kanji:
    row = source.df_kanji[source.df_kanji[ExcelColumn.char] == char].iloc[0]
    return read_kanji(row)


def read_excel(filename: str) -> Source:
    df_kanji = pandas.read_excel(filename, sheet_name="MAIN")
    df_kanji.columns = ExcelColumn.list_columns
    df_kanji.fillna('', inplace=True)

    df_keyword = pandas.read_excel(filename, sheet_name="keyword.list")

    df_stem = pandas.read_excel(filename, sheet_name="stem.list")
    df_stem.fillna('', inplace=True)

    df_special = pandas.read_excel(filename, sheet_name="special.list")
    df_special.fillna('', inplace=True)

    return Source(df_kanji, df_keyword, df_stem, df_special)
