import logging
from typing import Optional, List, Callable, TypeVar

import pandas

T = TypeVar('T')

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)-4s %(message)s', datefmt='%m/%d %H:%M:%S')


def set_logging_level(state):
    logger.setLevel(state)


def is_empty_string(value: str) -> Optional[str]:
    if value != "":
        return value
    else:
        return None


def read_kanji_dataframe(dataframe: pandas.DataFrame, read_fn: Callable) -> list:
    return [read_fn(dataframe.iloc[i]) for i in range(len(dataframe.index))]


def find_kanji_on_reading(vr_cluster_kanji: List[T], kanji: T,
                          get_readings: Callable[[T], List[str]]) -> List[T]:
    kanji_readings = get_readings(kanji)
    res = []
    for vr_kanji in vr_cluster_kanji:
        vr_readings = get_readings(vr_kanji)
        if any(r in vr_readings for r in kanji_readings) and vr_readings != ['']:
            res.append(vr_kanji)
    return res


def find_cluster_1_2_3_components(component: str, kanji_char: str,
                                  df: pandas.DataFrame,
                                  col_char: str, col_comp1: str,
                                  col_comp2: str, col_comp3: str) -> pandas.DataFrame:
    return df[
        ((df[col_comp1] == component) |
         (df[col_comp2] == component) |
         (df[col_comp3] == component))
        & (df[col_char] != kanji_char)
    ]
