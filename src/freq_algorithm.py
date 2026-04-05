"""Frequency-based kanji grouping pipeline.

Groups kanji by shared component2 and on'yomi, using frequency rank
instead of SRL for ordering. Simpler than the main categorization pipeline.
"""

from dataclasses import dataclass, replace
from typing import List

import pandas

from core import (
    is_empty_string, set_logging_level, logger,
    find_kanji_on_reading as _find_kanji_on_reading,
    find_cluster_1_2_3_components as _find_cluster_1_2_3_components,
)


# --- Model ---

@dataclass
class FreqKanji:
    ref: str
    char: str
    component1: str
    component2: str
    component3: str
    onyomi: List[str]
    kunyomi: str
    keyword: str
    freq: int

    @property
    def onyomi_str(self) -> str:
        return "\u3001".join(self.onyomi)


@dataclass
class FreqSource:
    df_kanji: pandas.DataFrame


class FreqExcelColumn:
    kanji = "Kanji"
    component1 = "Comp1"
    component2 = "Comp2"
    component3 = "Comp3"
    onyomi = "Onyomi"
    kunyomi = "Kunyomi"
    keyword = "Keyword"
    freq = "Freq"
    onyomi_delimiter = "\u3001"
    list_columns = ["Kanji", "Comp1", "Comp2", "Comp3", "Onyomi", "Kunyomi", "Keyword", "Freq"]


# --- Data loading ---

def read_kanji(row: pandas.Series) -> FreqKanji:
    return FreqKanji(
        char=row[FreqExcelColumn.kanji],
        ref=row[FreqExcelColumn.kanji],
        component1=row[FreqExcelColumn.component1],
        component2=row[FreqExcelColumn.component2],
        component3=row[FreqExcelColumn.component3],
        onyomi=row[FreqExcelColumn.onyomi].split(FreqExcelColumn.onyomi_delimiter),
        kunyomi=row[FreqExcelColumn.kunyomi],
        keyword=row[FreqExcelColumn.keyword],
        freq=int(row[FreqExcelColumn.freq]),
    )


def read_kanji_dataframe(dataframe: pandas.DataFrame) -> List[FreqKanji]:
    return [read_kanji(dataframe.iloc[i]) for i in range(len(dataframe.index))]


def read_kanji_char(kanji: str, source: FreqSource) -> FreqKanji:
    row = source.df_kanji[source.df_kanji[FreqExcelColumn.kanji] == kanji].iloc[0]
    return read_kanji(row)


def read_excel(filename: str) -> pandas.DataFrame:
    df_kanji = pandas.read_excel(filename, sheet_name="MAIN")
    df_kanji.columns = FreqExcelColumn.list_columns
    df_kanji.fillna('', inplace=True)
    return df_kanji


# --- Algorithm ---

def find_cluster_1_2_3_components(component: str, kanji: FreqKanji, source: FreqSource) -> pandas.DataFrame:
    return _find_cluster_1_2_3_components(
        component, kanji.char, source.df_kanji,
        FreqExcelColumn.kanji, FreqExcelColumn.component1,
        FreqExcelColumn.component2, FreqExcelColumn.component3
    )


def find_kanji_on_reading(vr_cluster_kanji: List[FreqKanji], kanji: FreqKanji) -> List[FreqKanji]:
    return _find_kanji_on_reading(vr_cluster_kanji, kanji, lambda k: k.onyomi)


def categorize_kanji(kanji: FreqKanji, result: List[FreqKanji], list_kanji: List[FreqKanji]):
    components = []
    for k in list_kanji:
        if (kanji.component2 == k.component2 and kanji.component2 != '') or \
                (kanji.char == k.component2 and kanji.char != '') or \
                (kanji.component2 == k.char and kanji.component2 != ''):
            components.append(k)

    components_str = ', '.join(c.char for c in components)

    logger.info(f"categorize: {kanji.char} | components: {len(components)} | {components_str}")

    if len(components) == 0:
        result.append(kanji)
    else:
        onyomi_list = []
        for k_onyomi in kanji.onyomi:
            for component in components:
                for c_onyomi in component.onyomi:
                    if k_onyomi == c_onyomi and k_onyomi != '':
                        onyomi_list.append(component)

        seen_onyomi = set()
        new_onyomi_list = []
        for obj in onyomi_list:
            if obj.char not in seen_onyomi:
                new_onyomi_list.append(obj)
                seen_onyomi.add(obj.char)

        if len(new_onyomi_list) != 0:
            new_kanji = replace(kanji, ref=min(new_onyomi_list, key=lambda o: o.freq).char)
            result.append(new_kanji)
        else:
            result.append(kanji)
