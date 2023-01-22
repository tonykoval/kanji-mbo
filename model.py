from dataclasses import dataclass

import pandas
from typing import List


@dataclass
class Kanji:
    char: str
    component1: str
    component2: str
    component3: str
    component4: str
    component5: str
    on_reading: str
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


@dataclass
class Categorization:
    result: dict
    queue: dict


class Constants:
    special_grp = '78 special'
    other_grp = '77 other'
    visual_grp = 'visual'

