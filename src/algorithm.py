from typing import Optional, List

import pandas
from disjoint_set import DisjointSet

from model import Source, Categorization, Constants, Kanji, ExcelColumn, Stem
from data_loader import read_kanji, read_kanji_dataframe, read_kanji_char, read_excel
from core import (
    is_empty_string, set_logging_level, logger,
    find_kanji_on_reading as _find_kanji_on_reading,
    find_cluster_1_2_3_components as _find_cluster_1_2_3_components,
)


def init_categorization(source: Source) -> Categorization:
    cat = Categorization()

    for grp in source.df_keyword[ExcelColumn.group].unique():
        cat.result.setdefault(grp, [])

    for grp in source.df_stem[ExcelColumn.group].unique():
        cat.result.setdefault(grp, [])

    cat.result.setdefault(Constants.other_grp, [])
    cat.result.setdefault(Constants.special_grp, [])

    for kanji, key in source.df_special[[ExcelColumn.kanji, ExcelColumn.key]].values:
        cat.queue[key].append(read_kanji_char(kanji, source))

    return cat


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


def find_special(kanji: Kanji, source: Source) -> Optional[str]:
    group = source.df_special[source.df_special[ExcelColumn.kanji] == kanji.char]
    if group.empty:
        return None
    else:
        return Constants.special_grp


def append_categorization(category: str, kanji: Kanji, is_first: bool, categorization: Categorization):
    if is_first:
        if kanji.char in categorization.queue:
            for ch in pandas.Series(categorization.queue[kanji.char]).drop_duplicates().tolist():
                ch.ref = kanji.char
                categorization.result[category].insert(0, ch)
            categorization.result[category].insert(0, kanji)
            del categorization.queue[kanji.char]
        else:
            categorization.result[category].insert(0, kanji)
    else:
        if kanji.char in categorization.queue:
            categorization.result[category].append(kanji)
            for ch in pandas.Series(categorization.queue[kanji.char]).drop_duplicates().tolist():
                ch.ref = kanji.char
                categorization.result[category].insert(0, ch)
            del categorization.queue[kanji.char]
        else:
            categorization.result[category].append(kanji)


def add_to_queue(kanji: Kanji, ref_char: str, categorization: Categorization):
    kanji.ref = ref_char
    categorization.queue.setdefault(ref_char, []).append(kanji)


def find_cluster_1_2_3_components(component: str, kanji: Kanji, source: Source) -> pandas.DataFrame:
    return _find_cluster_1_2_3_components(
        component, kanji.char, source.df_kanji,
        ExcelColumn.char, ExcelColumn.component1,
        ExcelColumn.component2, ExcelColumn.component3
    )


def find_max_srl(dataframe: pandas.DataFrame):
    return dataframe[dataframe[ExcelColumn.srl] == dataframe[ExcelColumn.srl].max()].iloc[0]


def find_max_srl_kanji(vr_cluster: List[Kanji]) -> Kanji:
    max_srl = -1
    res_kanji = None

    for kanji in vr_cluster:
        if kanji.srl > max_srl:
            max_srl = kanji.srl
            res_kanji = kanji

    return res_kanji


def find_kanji_on_reading(vr_cluster_kanji: List[Kanji], kanji: Kanji) -> List[Kanji]:
    return _find_kanji_on_reading(vr_cluster_kanji, kanji, lambda k: k.on_reading)


def find_onyomi(kanji: Kanji, vr_cluster: pandas.DataFrame, categorization: Categorization,
                source: Source):
    vr_cluster_kanji = read_kanji_dataframe(vr_cluster)
    onyomi = find_kanji_on_reading(vr_cluster_kanji, kanji)
    if len(onyomi) == 0:
        fifth_rule(kanji, categorization, source, False)
        return

    if len(onyomi) > 1:
        logger.info("kanji > 1")
        max_srl_kanji = find_max_srl_kanji(onyomi)
        if kanji.srl > max_srl_kanji.srl:
            fifth_rule(kanji, categorization, source, True)
            return
        logger.info("max srl kanji: {}".format(max_srl_kanji.char))
    else:
        logger.info("kanji = 1")
        logger.info("kanji srl: {}".format(kanji.srl))
        max_srl_kanji = onyomi[0]
        logger.info("max_srl_kanji srl: {}".format(max_srl_kanji.srl))
        if kanji.srl > max_srl_kanji.srl:
            fifth_rule(kanji, categorization, source, kanji.srl > 2)
            return

    kanji.type = Constants.vr
    add_to_queue(kanji, max_srl_kanji.char, categorization)


def seventh_rule(kanji: Kanji, categorization: Categorization):
    logger.info("7. rule")
    append_categorization(Constants.other_grp, kanji, False, categorization)


def categorize_srl(dataframe: pandas.DataFrame, kanji: Kanji, categorization: Categorization, source: Source, type: str):
    if len(dataframe.index) > 1:
        max_srl_kanji = find_max_srl(dataframe)
    else:
        max_srl_kanji = dataframe.iloc[0]
    kanji.type = type
    add_to_queue(kanji, max_srl_kanji[ExcelColumn.char], categorization)


def sixth_rule(kanji: Kanji, categorization: Categorization, source: Source):
    logger.info("6. rule - first condition")
    # rewrite rule
    vr_cluster_1_2_3 = find_cluster_1_2_3_components(kanji.char, kanji, source)
    if vr_cluster_1_2_3 is None or vr_cluster_1_2_3.empty:
        logger.info("6. rule - second condition")
        component2 = is_empty_string(kanji.component2)
        if component2 is not None:
            vr_component2 = source.df_kanji[
                (source.df_kanji[ExcelColumn.component2] == kanji.component2)
                & (source.df_kanji[ExcelColumn.char] != kanji.char)
            ]
        else:
            vr_component2 = None
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


def find_stem_variations(opt_component: str, source: Source, priority: int) -> Optional[Stem]:
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
        if stem is not None and stem.priority > priority:
            max_stem = stem
            priority = stem.priority

    return max_stem


def fifth_rule(kanji: Kanji, categorization: Categorization, source: Source, ignore_srl: bool):
    logger.info("5. rule")

    max_stem = find_max_stem(
        [
            find_stem_variations(kanji.component1, source, 3),
            find_stem_variations(kanji.component2, source, 2),
            find_stem_variations(kanji.component3, source, 1)
        ]
    )

    if max_stem is None:
        sixth_rule(kanji, categorization, source)
    else:
        if ignore_srl:
            kanji.type = Constants.mean
        else:
            if kanji.srl == 1:
                kanji.type = Constants.form
            else:
                kanji.type = Constants.mean
        append_categorization(max_stem.group, kanji, False, categorization)


def fourth_rule(kanji: Kanji, categorization: Categorization, source: Source):
    logger.info("4. rule")
    kanji_comp2 = is_empty_string(kanji.component2)
    if kanji_comp2 is not None:
        vr_cluster = source.df_kanji[
            ((source.df_kanji[ExcelColumn.char] == kanji.component2)
             | (source.df_kanji[ExcelColumn.component2] == kanji.component2))
            & (source.df_kanji[ExcelColumn.char] != kanji.char)
        ]
        if vr_cluster is None:
            logger.info("empty vr_cluster")
            fifth_rule(kanji, categorization, source, False)
        else:
            logger.info("vr clusters: {} components".format(len(vr_cluster)))
            find_onyomi(kanji, vr_cluster, categorization, source)
    else:
        fifth_rule(kanji, categorization, source, False)


def categorize_queue(categorization: Categorization):
    del categorization.result[Constants.special_grp]

    ds = DisjointSet()
    for key in categorization.result:
        for kanji in categorization.result[key]:
            ds.union(kanji.char, key)
    for key in categorization.queue:
        for kanji in categorization.queue[key]:
            ds.union(kanji.char, key)

    logger.info(ds)
    for key in categorization.queue:
        for kanji in categorization.queue[key]:
            categorization.result[ds.find(kanji.char)].append(kanji)


def categorize_kanji(kanji: Kanji, categorization: Categorization, source: Source):
    first_rule = find_keyword(kanji, source)
    second_rule = find_stem(kanji, source)
    special_rule = find_special(kanji, source)

    if first_rule is not None:
        logger.info("1. rule")
        if kanji.type == Constants.mean:
            append_categorization(first_rule, kanji, False, categorization)
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
    elif special_rule is not None:
        logger.info("special")
        append_categorization(special_rule, kanji, False, categorization)
    else:
        components = source.df_kanji[source.df_kanji[ExcelColumn.component2] == kanji.char]
        logger.info("components count: " + str(len(components.index)))
        if components.empty:
            fourth_rule(kanji, categorization, source)
        else:
            logger.info("3. rule")
            components_kanji = read_kanji_dataframe(components)
            onyomi = find_kanji_on_reading(components_kanji, kanji)
            if len(onyomi) == 0:
                logger.info("onyomi empty")
                fourth_rule(kanji, categorization, source)
            else:
                logger.info("3. rule a) b)")
                if len(onyomi) > 1:
                    logger.info("kanji > 1")
                    max_srl_kanji = find_max_srl_kanji(onyomi)
                else:
                    logger.info("kanji = 1")
                    max_srl_kanji = onyomi[0]

                kanji.tags.append(Constants.crown_tag)
                kanji.type = Constants.vr
                if kanji.srl > max_srl_kanji.srl:
                    fourth_rule(kanji, categorization, source)
                else:
                    add_to_queue(kanji, max_srl_kanji.char, categorization)


def run_pipeline(filepath: str, log_level=None) -> tuple:
    """Run the full categorization pipeline. Returns (categorization, source)."""
    import logging
    set_logging_level(log_level or logging.WARNING)
    source = read_excel(filepath)
    categorization = init_categorization(source)
    for kanji in read_kanji_dataframe(source.df_kanji):
        categorize_kanji(kanji, categorization, source)
    categorize_queue(categorization)
    return categorization, source
