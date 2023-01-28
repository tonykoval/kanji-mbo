from typing import Optional, List, Tuple

import pandas
import logging
from disjoint_set import DisjointSet

from model import Source, Categorization, Constants, Kanji, ExcelColumn, Stem

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)-4s %(message)s', datefmt='%m/%d %H:%M:%S')


def set_logging_level(state):
    logger.setLevel(state)


def read_kanji(row: pandas.DataFrame) -> Kanji:
    return Kanji(
        char=row[ExcelColumn.char],
        component1=row[ExcelColumn.component1],
        component2=row[ExcelColumn.component2],
        component3=row[ExcelColumn.component3],
        component4=row[ExcelColumn.component4],
        component5=row[ExcelColumn.component5],
        on_reading=row[ExcelColumn.on_reading],
        kun_reading=row[ExcelColumn.kun_reading],
        keyword=row[ExcelColumn.keyword],
        srl=int(row[ExcelColumn.srl]),
        type=row[ExcelColumn.type],
        freq=int(row[ExcelColumn.freq]),
        tags=list(row[ExcelColumn.tags])
    )


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
    return Source(df_kanji, df_keyword, df_stem)


def init_categorization(source: Source) -> Categorization:
    categorization = {}

    for grp in source.df_keyword[ExcelColumn.group].unique():
        categorization[grp] = []

    for grp in source.df_stem[ExcelColumn.group].unique():
        categorization[grp] = []

    categorization[Constants.other_grp] = []
    categorization[Constants.special_grp] = []
    categorization[Constants.visual_grp] = []

    queue = {}
    return Categorization(categorization, queue)


def find_keyword(kanji: Kanji, source: Source) -> Optional[str]:
    group = source.df_keyword[source.df_keyword[ExcelColumn.keyword] == kanji.keyword][ExcelColumn.group]
    if group.empty:
        return None
    else:
        return group.iloc[0]


def find_stem(kanji: Kanji, source: Source) -> Optional[str]:
    group = source.df_stem[source.df_stem[ExcelColumn.stem_kanji] == kanji.char][ExcelColumn.group]
    if group.empty:
        return None
    else:
        return group.iloc[0]


def append_categorization(category: str, kanji: Kanji, is_first: bool, categorization: Categorization):
    if is_first:
        if kanji.char in categorization.queue.keys():
            for ch in categorization.queue[kanji.char]:
                categorization.result[category].insert(0, ch)
            categorization.result[category].insert(0, kanji)
            del categorization.queue[kanji.char]
        else:
            categorization.result[category].insert(0, kanji)
    else:
        if kanji.char in categorization.queue.keys():
            categorization.result[category].append(kanji)
            for ch in categorization.queue[kanji.char]:
                categorization.result[category].append(ch)
            del categorization.queue[kanji.char]
        else:
            categorization.result[category].append(kanji)


def is_empty_string(value: str) -> Optional[str]:
    if value != "":
        return value
    else:
        return None


def find_cluster_1_2_3_components(component: str, kanji: Kanji, source: Source) -> pandas.DataFrame:
    return source.df_kanji[
        ((source.df_kanji[ExcelColumn.component1] == component) |
         (source.df_kanji[ExcelColumn.component2] == component) |
         (source.df_kanji[ExcelColumn.component3] == component)
         )
        & (source.df_kanji[ExcelColumn.char] != kanji.char)
    ]


def find_max_srv(dataframe: pandas.DataFrame):
    return dataframe[dataframe[ExcelColumn.srl] == dataframe[ExcelColumn.srl].max()].iloc[0]


def find_onyomi(kanji: Kanji, vr_cluster: pandas.DataFrame, categorization: Categorization,
                source: Source):
    vr_crowns = kanji.on_reading.split(ExcelColumn.on_reading_delimiter)
    onyomi = vr_cluster[vr_cluster[ExcelColumn.on_reading].isin(vr_crowns)]
    if onyomi.empty:
        fifth_rule(kanji, categorization, source)
    else:
        if len(onyomi.index) > 1:
            logger.info("kanji > 1")
            max_srl_kanji = find_max_srv(onyomi)
            logger.info("max srl kanji: {}".format(max_srl_kanji[ExcelColumn.char]))
            kanji.type = Constants.vr
            if max_srl_kanji[ExcelColumn.char] in categorization.queue.keys():
                categorization.queue[max_srl_kanji[ExcelColumn.char]].append(kanji)
            else:
                categorization.queue[max_srl_kanji[ExcelColumn.char]] = []
                categorization.queue[max_srl_kanji[ExcelColumn.char]].append(kanji)
        else:
            logger.info("kanji = 1")
            kanji.type = Constants.vr
            max_srl_kanji = onyomi.iloc[0]
            if max_srl_kanji[ExcelColumn.char] in categorization.queue.keys():
                categorization.queue[max_srl_kanji[ExcelColumn.char]].append(kanji)
            else:
                categorization.queue[max_srl_kanji[ExcelColumn.char]] = []
                categorization.queue[max_srl_kanji[ExcelColumn.char]].append(kanji)


def seventh_rule(kanji: Kanji, categorization: Categorization):
    logger.info("7. rule")
    append_categorization(Constants.other_grp, kanji, False, categorization)


def categorize_srl(dataframe: pandas.DataFrame, kanji: Kanji, categorization: Categorization, source: Source, type: str):
    if len(dataframe.index) > 1:
        max_srl_kanji = find_max_srv(dataframe)
        kanji.type = type

        if max_srl_kanji[ExcelColumn.char] in categorization.queue.keys():
            categorization.queue[max_srl_kanji[ExcelColumn.char]].append(kanji)
        else:
            categorization.queue[max_srl_kanji[ExcelColumn.char]] = []
            categorization.queue[max_srl_kanji[ExcelColumn.char]].append(kanji)
    else:
        kanji.type = type
        max_srl_kanji = dataframe.iloc[0]
        if max_srl_kanji[ExcelColumn.char] in categorization.queue.keys():
            categorization.queue[max_srl_kanji[ExcelColumn.char]].append(kanji)
        else:
            categorization.queue[max_srl_kanji[ExcelColumn.char]] = []
            categorization.queue[max_srl_kanji[ExcelColumn.char]].append(kanji)


def sixth_rule(kanji: Kanji, categorization: Categorization, source: Source):
    logger.info("6. rule - first condition")
    vr_cluster_1_2_3 = find_cluster_1_2_3_components(kanji.char, kanji, source)
    if vr_cluster_1_2_3 is None or vr_cluster_1_2_3.empty:
        logger.info("6. rule - second condition")
        vr_component2 = source.df_kanji[
            (source.df_kanji[ExcelColumn.component2] == kanji.component2)
            & (source.df_kanji[ExcelColumn.char] != kanji.char)
        ]
        if vr_component2 is None or vr_component2.empty:
            logger.info("6. rule - third condition")
            vr_component3 = source.df_kanji[
                (source.df_kanji[ExcelColumn.char] == kanji.component1)
                & (source.df_kanji[ExcelColumn.char] != kanji.char)
            ]
            if vr_component3 is None or vr_component3.empty:
                seventh_rule(kanji, categorization)
            else:
                categorize_srl(vr_component3, kanji, categorization, source, Constants.visual)
        else:
            categorize_srl(vr_component2, kanji, categorization, source, Constants.visual)
    else:
        categorize_srl(vr_cluster_1_2_3, kanji, categorization, source, Constants.visual)


def find_stem_cluster_all_components(opt_component: str, source: Source, priority: int) -> Optional[Stem]:
    component = is_empty_string(opt_component)
    if component:
        group = source.df_stem[
            (source.df_stem[ExcelColumn.stem_component1] == component) |
            (source.df_stem[ExcelColumn.stem_component2] == component) |
            (source.df_stem[ExcelColumn.stem_component3] == component) |
            (source.df_stem[ExcelColumn.stem_component4] == component) |
            (source.df_stem[ExcelColumn.stem_component5] == component) |
            (source.df_stem[ExcelColumn.stem_component6] == component)
            ][ExcelColumn.group]
        if len(group) == 1:
            return Stem(group.iloc[0], priority)
        elif len(group) == 0:
            return None
        else:
            logger.warning("stem groups > 1: {} {}".format(group, component))
    else:
        return None


def find_max_stem(stems: List[Stem]) -> Optional[Stem]:
    priority = -1
    max_stem = None
    for stem in stems:
        if stem is None:
            break
        elif stem.priority > priority:
            max_stem = stem
            priority = stem.priority

    return max_stem


def fifth_rule(kanji: Kanji, categorization: Categorization, source: Source):
    logger.info("5. rule")

    max_stem = find_max_stem(
        [
            find_stem_cluster_all_components(kanji.component1, source, 3),
            find_stem_cluster_all_components(kanji.component2, source, 2),
            find_stem_cluster_all_components(kanji.component3, source, 1)
        ]
    )

    if max_stem is None:
        sixth_rule(kanji, categorization, source)
    else:
        if kanji.srl == 1:
            kanji.type = Constants.form
        else:
            kanji.type = Constants.mean
        append_categorization(max_stem.group, kanji, False, categorization)


def fourth_rule(kanji: Kanji, categorization: Categorization, source: Source):
    logger.info("4. rule")

    vr_cluster = source.df_kanji[
        (source.df_kanji[ExcelColumn.char] == kanji.component2)
        | (source.df_kanji[ExcelColumn.component2] == kanji.component2)
        & (source.df_kanji[ExcelColumn.char] != kanji.char)
    ]
    if vr_cluster is None:
        logger.info("empty vr_cluster")
        fifth_rule(kanji, categorization, source)
    else:
        logger.info("vr clusters: {} components".format(len(vr_cluster)))
        find_onyomi(kanji, vr_cluster, categorization, source)


def categorize_queue(categorization: Categorization):
    ds = DisjointSet()
    for key in categorization.result:
        for kanji in categorization.result[key]:
            ds.union(kanji.char, key)
    for key in categorization.queue:
        for kanji in categorization.queue[key]:
            ds.union(kanji.char, key)

    print(ds)
    for key in categorization.queue:
        for kanji in categorization.queue[key]:
            categorization.result[ds.find(kanji.char)].append(kanji)


def categorize_kanji(kanji: Kanji, categorization: Categorization, source: Source):
    first_rule = find_keyword(kanji, source)
    second_rule = find_stem(kanji, source)

    if first_rule is not None:
        logger.info("1. rule")
        if kanji.type == Constants.mean:
            append_categorization(first_rule, kanji, False, categorization)
        elif kanji.type == Constants.special:
            append_categorization(Constants.special_grp, kanji, False, categorization)
        elif kanji.type == Constants.other:
            append_categorization(Constants.other_grp, kanji, False, categorization)
        else:
            print("ERROR: missing grp")
    elif second_rule is not None:
        logger.info("2. rule")
        if kanji.type == Constants.stem:
            append_categorization(second_rule, kanji, True, categorization)
        else:
            print("ERROR: missing rule")
    else:
        components = source.df_kanji[source.df_kanji[ExcelColumn.component2] == kanji.char]
        logger.info("components count: " + str(len(components.index)))
        if components.empty:
            fourth_rule(kanji, categorization, source)
        else:
            logger.info("3. rule")
            vr_crowns = kanji.on_reading.split(ExcelColumn.on_reading_delimiter)
            onyomi = components[components[ExcelColumn.on_reading].isin(vr_crowns)]
            if onyomi.empty:
                logger.info("onyomi empty")
                fourth_rule(kanji, categorization, source)
            else:
                logger.info("3. rule a) b)")
                if len(onyomi.index) > 1:
                    logger.info("kanji > 1")
                    max_srl_kanji = onyomi[onyomi[ExcelColumn.srl] == onyomi[ExcelColumn.srl].max()].iloc[0]
                    kanji.tags.append(Constants.crown_tag)
                    kanji.type = Constants.vr

                    if max_srl_kanji[ExcelColumn.char] in categorization.queue.keys():
                        categorization.queue[max_srl_kanji[ExcelColumn.char]].append(kanji)
                    else:
                        categorization.queue[max_srl_kanji[ExcelColumn.char]] = []
                        categorization.queue[max_srl_kanji[ExcelColumn.char]].append(kanji)
                else:
                    logger.info("kanji = 1")
                    kanji.tags.append(Constants.crown_tag)
                    kanji.type = Constants.vr
                    max_srl_kanji = onyomi.iloc[0]
                    if max_srl_kanji[ExcelColumn.char] in categorization.queue.keys():
                        categorization.queue[onyomi.iloc[0][ExcelColumn.char]].append(kanji)
                    else:
                        categorization.queue[onyomi.iloc[0][ExcelColumn.char]] = []
                        categorization.queue[onyomi.iloc[0][ExcelColumn.char]].append(kanji)
