from typing import Optional

import pandas
import logging
from disjoint_set import DisjointSet

from model import Source, Categorization, Constants, Kanji, ExcelColumn

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


def get_kanji_component(component: str, kanji: Kanji) -> Optional[str]:
    if component == ExcelColumn.component1:
        return kanji.component1
    elif component == ExcelColumn.component2:
        return kanji.component2
    elif component == ExcelColumn.component3:
        return kanji.component3
    elif component == ExcelColumn.component4:
        return kanji.component4
    elif component == ExcelColumn.component5:
        return kanji.component5
    else:
        return None


def find_cluster_1_2_components(component: str, kanji: Kanji, source: Source) -> pandas.DataFrame:
    kanji_component = get_kanji_component(component, kanji)
    if kanji_component is not None:
        return source.df_kanji[
            ((source.df_kanji[ExcelColumn.component1] == kanji_component) |
             (source.df_kanji[ExcelColumn.component2] == kanji_component))
            & (source.df_kanji[ExcelColumn.char] != kanji.char)
            ]


def find_cluster_components(component: str, kanji: Kanji, source: Source) -> pandas.DataFrame:
    kanji_component = get_kanji_component(component, kanji)
    if kanji_component is not None:
        return source.df_kanji[
            ((source.df_kanji[ExcelColumn.component2] == kanji_component) |
             (source.df_kanji[ExcelColumn.component3] == kanji_component) |
             (source.df_kanji[ExcelColumn.component4] == kanji_component) |
             (source.df_kanji[ExcelColumn.component5] == kanji_component))
            & (source.df_kanji[ExcelColumn.char] != kanji.char)
            ]


def find_cluster_all_components(component: str, kanji: Kanji, source: Source) -> pandas.DataFrame:
    kanji_component = get_kanji_component(component, kanji)
    if kanji_component is not None:
        return source.df_kanji[
            ((source.df_kanji[ExcelColumn.component1] == kanji_component) |
             (source.df_kanji[ExcelColumn.component2] == kanji_component) |
             (source.df_kanji[ExcelColumn.component3] == kanji_component) |
             (source.df_kanji[ExcelColumn.component4] == kanji_component) |
             (source.df_kanji[ExcelColumn.component5] == kanji_component))
            & (source.df_kanji[ExcelColumn.char] != kanji.char)
            ]


def find_max_srv(dataframe: pandas.DataFrame):
    return dataframe[dataframe[ExcelColumn.srl] == dataframe[ExcelColumn.srl].max()].iloc[0]


def find_onyomi(kanji: Kanji, vr_cluster: pandas.DataFrame, categorization: Categorization,
                source: Source):
    vr_crowns = kanji.on_reading.split(ExcelColumn.on_reading_delimiter)
    onyomi = vr_cluster[vr_cluster[ExcelColumn.on_reading].isin(vr_crowns)]
    if onyomi.empty:
        logger.info("4. rule - 3rd condition")
        vr_third_cluster = source.df_kanji[source.df_kanji[ExcelColumn.char] == kanji.component2]
        if len(vr_third_cluster.index) > 0:
            if len(vr_third_cluster.index) > 1:
                logger.info("kanji > 1")
                max_srl_kanji = find_max_srv(vr_third_cluster)
                kanji.type = Constants.vr

                if max_srl_kanji[ExcelColumn.char] in categorization.queue.keys():
                    categorization.queue[max_srl_kanji[ExcelColumn.char]].append(kanji)
                else:
                    categorization.queue[max_srl_kanji[ExcelColumn.char]] = []
                    categorization.queue[max_srl_kanji[ExcelColumn.char]].append(kanji)
            else:
                logger.info("kanji = 1")
                kanji.type = Constants.vr
                max_srl_kanji = vr_third_cluster.iloc[0]
                if max_srl_kanji[ExcelColumn.char] in categorization.queue.keys():
                    categorization.queue[vr_third_cluster.iloc[0][ExcelColumn.char]].append(kanji)
                else:
                    categorization.queue[vr_third_cluster.iloc[0][ExcelColumn.char]] = []
                    categorization.queue[vr_third_cluster.iloc[0][ExcelColumn.char]].append(kanji)
        else:
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
                categorization.queue[onyomi.iloc[0][ExcelColumn.char]].append(kanji)
            else:
                categorization.queue[onyomi.iloc[0][ExcelColumn.char]] = []
                categorization.queue[onyomi.iloc[0][ExcelColumn.char]].append(kanji)


def seventh_rule(kanji: Kanji, categorization: Categorization):
    logger.warning("TODO 7. rule")
    append_categorization(Constants.other_grp, kanji, False, categorization)


def sixth_rule(kanji: Kanji, categorization: Categorization, source: Source):
    logger.info("6. rule")
    vr_cluster_1_2 = pandas.concat([
        find_cluster_1_2_components(ExcelColumn.component1, kanji, source),
        find_cluster_1_2_components(ExcelColumn.component2, kanji, source)
    ])
    if vr_cluster_1_2.empty:
        seventh_rule(kanji, categorization)
    else:
        if len(vr_cluster_1_2.index) > 1:
            append_categorization(Constants.visual_grp, kanji, False, categorization)
        else:
            kanji.type = Constants.visual
            max_srl_kanji = vr_cluster_1_2.iloc[0]
            if max_srl_kanji[ExcelColumn.char] in categorization.queue.keys():
                categorization.queue[vr_cluster_1_2.iloc[0][ExcelColumn.char]].append(kanji)
            else:
                categorization.queue[vr_cluster_1_2.iloc[0][ExcelColumn.char]] = []
                categorization.queue[vr_cluster_1_2.iloc[0][ExcelColumn.char]].append(kanji)


def fifth_rule(kanji: Kanji, categorization: Categorization, source: Source):
    logger.info("5. rule")
    group_stem = source.df_stem[
        (source.df_stem[ExcelColumn.stem_kanji] == kanji.component1) |
        (source.df_stem[ExcelColumn.stem_kanji] == kanji.component2) |
        (source.df_stem[ExcelColumn.stem_kanji] == kanji.component3)
        ][ExcelColumn.group]
    if group_stem.empty:
        sixth_rule(kanji, categorization, source)
    else:
        if kanji.srl == 1:
            kanji.type = Constants.form
        else:
            kanji.type = Constants.mean
        if len(group_stem) == 1:
            append_categorization(group_stem.iloc[0], kanji, False, categorization)
        else:
            logger.error("more stems")


def fourth_rule(kanji: Kanji, categorization: Categorization, source: Source):
    logger.info("4. rule")
    vr_cluster = pandas.concat([
        find_cluster_components(ExcelColumn.component2, kanji, source),
        find_cluster_components(ExcelColumn.component3, kanji, source),
        find_cluster_components(ExcelColumn.component4, kanji, source),
        find_cluster_components(ExcelColumn.component5, kanji, source)
    ])
    if vr_cluster.empty:
        vr_all_cluster = pandas.concat([
            find_cluster_all_components(ExcelColumn.component1, kanji, source),
            find_cluster_all_components(ExcelColumn.component2, kanji, source),
            find_cluster_all_components(ExcelColumn.component3, kanji, source),
            find_cluster_all_components(ExcelColumn.component4, kanji, source),
            find_cluster_all_components(ExcelColumn.component5, kanji, source)
        ])
        if vr_all_cluster.empty:
            fifth_rule(kanji, categorization, source)
        else:
            logger.info("vr all cluster")
            find_onyomi(kanji, vr_all_cluster, categorization, source)
    else:
        logger.info("vr clusters")
        find_onyomi(kanji, vr_cluster, categorization, source)


def categorize_queue(categorization: Categorization):
    ds = DisjointSet()
    for key in categorization.result:
        for char in categorization.result[key]:
            ds.union(char[ExcelColumn.char], key)
    for key in categorization.queue:
        for char in categorization.queue[key]:
            ds.union(char[ExcelColumn.char], key)

    print(ds)
    for key in categorization.queue:
        for char in categorization.queue[key]:
            categorization.result[ds.find(char[ExcelColumn.char])].append(char)


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
        components = source.df_kanji[
            (source.df_kanji[ExcelColumn.component1] == kanji.char) | (source.df_kanji[ExcelColumn.component2] == kanji.char)]
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
