import sys
import os
from dataclasses import replace
from typing import List

import pandas

# Allow importing from parent src/ directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from model import Source, Kanji, ExcelColumn
from core import (
    is_empty_string, set_logging_level,
    read_kanji_dataframe as _read_kanji_dataframe,
    find_kanji_on_reading as _find_kanji_on_reading,
    find_cluster_1_2_3_components as _find_cluster_1_2_3_components,
)
from core import logger


def read_kanji(row: pandas.DataFrame) -> Kanji:
    return Kanji(
        char=row[ExcelColumn.kanji],
        ref=row[ExcelColumn.kanji],
        component1=row[ExcelColumn.component1],
        component2=row[ExcelColumn.component2],
        component3=row[ExcelColumn.component3],
        onyomi=row[ExcelColumn.onyomi].split(ExcelColumn.onyomi_delimiter),
        kunyomi=row[ExcelColumn.kunyomi],
        keyword=row[ExcelColumn.keyword],
        freq=int(row[ExcelColumn.freq])
    )


def read_kanji_dataframe(dataframe: pandas.DataFrame) -> List[Kanji]:
    return _read_kanji_dataframe(dataframe, read_kanji)


def read_kanji_char(kanji: str, source: Source) -> Kanji:
    row = source.df_kanji[source.df_kanji[ExcelColumn.kanji] == kanji].iloc[0]
    return read_kanji(row)


def read_excel(filename: str) -> pandas.DataFrame:
    df_kanji = pandas.read_excel(filename, sheet_name="MAIN")
    df_kanji.columns = ExcelColumn.list_columns
    df_kanji.fillna('', inplace=True)

    return df_kanji


def find_cluster_1_2_3_components(component: str, kanji: Kanji, source: Source) -> pandas.DataFrame:
    return _find_cluster_1_2_3_components(
        component, kanji.char, source.df_kanji,
        ExcelColumn.kanji, ExcelColumn.component1,
        ExcelColumn.component2, ExcelColumn.component3
    )


def find_min_freq_kanji(dataframe: pandas.DataFrame, source: Source):
    return read_kanji_char(dataframe[dataframe[ExcelColumn.freq] == dataframe[ExcelColumn.freq].min()].iloc[0], source)


def find_max_srl_kanji(vr_cluster: List[Kanji]) -> Kanji:
    max_srl = -1
    res_kanji = None

    for kanji in vr_cluster:
        if kanji.srl > max_srl:
            max_srl = kanji.srl
            res_kanji = kanji

    return res_kanji


def find_kanji_on_reading(vr_cluster_kanji: List[Kanji], kanji: Kanji) -> List[Kanji]:
    return _find_kanji_on_reading(vr_cluster_kanji, kanji, lambda k: k.onyomi)


def categorize_kanji(kanji: Kanji, result: List[Kanji], list_kanji: List[Kanji]):
    components = []
    for k in list_kanji:
        # todo fix != 0
        if (kanji.component2 == k.component2 and kanji.component2 != '') or \
                (kanji.char == k.component2 and kanji.char != '') or \
                (kanji.component2 == k.char and kanji.component2 != ''):
            components.append(k)

    components_str = ', '.join(c.char for c in components)

    print("-------------------------------------------")
    print(f"categorize: {kanji.char}")
    print(f"components count: {len(components)}")
    print(f"components: {components_str}")
    if len(components) == 0:
        print(f"RESULT: {kanji.char}")
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

        onyomi_str = ' | '.join(f"{o.char}, {o.freq}" for o in new_onyomi_list)

        print(f"onyomi filter count: {len(new_onyomi_list)}")
        print(f"onyomi filter: {onyomi_str}")
        if len(new_onyomi_list) != 0:
            new_kanji = replace(kanji, ref=min(new_onyomi_list, key=lambda o: o.freq).char)
            print(f"RESULT: {new_kanji.char}")
            result.append(new_kanji)
        else:
            print(f"RESULT: {kanji.char}")
            result.append(kanji)
