from dataclasses import dataclass

import pandas
from typing import List


@dataclass
class Stem:
    group: str
    priority: int


@dataclass
class Kanji:
    ref: str
    char: str
    component1: str
    component2: str
    component3: str
    component4: str
    component5: str
    on_reading: List[str]
    kun_reading: str
    keyword: str
    srl: int
    type: str
    freq: int
    tags: List[str]


@dataclass
class Source:
    df_kanji: pandas.DataFrame
    df_keyword: pandas.DataFrame
    df_stem: pandas.DataFrame
    df_special: pandas.DataFrame


@dataclass
class Categorization:
    result: dict
    queue: dict


class Constants:
    other_grp = '77 other'
    special_grp = 'special'
    visual_grp = 'visual'
    mean = "MEAN"
    special = "SPECIAL"
    other = "OTHER"
    stem = "STEM"
    crown_tag = "CROWN_TAG"
    vr = "VR"
    form = "FORM"
    visual = "VISUAL"
    priority = "PRIORITY"


class ExcelColumn:
    kanji = "KANJI"
    key = "KEY"
    char = "CHAR"
    component1 = "COMPONENTS1"
    component2 = "COMPONENTS2"
    component3 = "COMPONENTS3"
    component4 = "COMPONENTS4"
    component5 = "COMPONENTS5"
    on_reading = "ON READING"
    kun_reading = "KUN READING"
    keyword = "KEYWORD"
    srl = "SRL"
    type = "TYPE"
    freq = "FREQ"
    tags = "TAGS"
    group = "GROUP"
    stem_kanji = "STEM KANJI"
    stem_component1 = "STEM 1"
    stem_component2 = "STEM 2"
    stem_component3 = "STEM 3"
    stem_component4 = "STEM 4"
    stem_component5 = "STEM 5"
    stem_component6 = "STEM 6"
    on_reading_delimiter = "、"
    list_columns = ["CHAR", "COMPONENTS1", "COMPONENTS2", "COMPONENTS3", "COMPONENTS4", "COMPONENTS5", "ON READING",
                     "KUN READING", "KEYWORD", "SRL", "TYPE", "FREQ", "TAGS", "GROUP"]
