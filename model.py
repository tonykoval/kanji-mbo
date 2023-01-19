from dataclasses import dataclass

import pandas


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

