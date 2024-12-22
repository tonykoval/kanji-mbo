from dataclasses import dataclass

import pandas
from typing import List


@dataclass
class Kanji:
    ref: str
    char: str
    component1: str
    component2: str
    component3: str
    onyomi: List[str]
    kunyomi: str
    keyword: str
    freq: int


@dataclass
class Source:
    df_kanji: pandas.DataFrame


class ExcelColumn:
    kanji = "Kanji"
    component1 = "Comp1"
    component2 = "Comp2"
    component3 = "Comp3"
    onyomi = "Onyomi"
    kunyomi = "Kunyomi"
    keyword = "Keyword"
    freq = "Freq"
    onyomi_delimiter = "、"
    list_columns = ["Kanji", "Comp1", "Comp2", "Comp3", "Onyomi", "Kunyomi", "Keyword", "Freq"]
