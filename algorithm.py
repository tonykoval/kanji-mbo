import pandas
import logging
from disjoint_set import DisjointSet

from model import Source, Categorization, Constants, Kanji

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)-4s %(message)s', datefmt='%m/%d %H:%M:%S')


def set_logging_level(state):
    logger.setLevel(state)


def read_kanji(row: pandas.DataFrame) -> Kanji:
    return Kanji(
        char=row["CHAR"],
        component1=row["COMPONENTS1"],
        component2=row["COMPONENTS2"],
        component3=row["COMPONENTS3"],
        component4=row["COMPONENTS4"],
        component5=row["COMPONENTS5"],
        on_reading=row["ON READING"],
        kun_reading=row["KUN READING"],
        keyword=row["KEYWORD"],
        srl=int(row["SRL"]),
        type=row["TYPE"],
        freq=int(row["FREQ"]),
        tags=list(row["TAGS"])
    )


def read_kanji_char(char: str, source: Source) -> Kanji:
    row = source.df_kanji[source.df_kanji["CHAR"] == char].iloc[0]
    return read_kanji(row)


def read_excel(filename: str) -> Source:
    df_kanji = pandas.read_excel(filename, sheet_name="MAIN")
    df_kanji.columns = ["CHAR", "COMPONENTS1", "COMPONENTS2", "COMPONENTS3", "COMPONENTS4", "COMPONENTS5", "ON READING",
                        "KUN READING", "KEYWORD", "SRL", "TYPE", "FREQ", "TAGS"]
    df_kanji.fillna('', inplace=True)

    df_keyword = pandas.read_excel(filename, sheet_name="keyword.list")

    df_stem = pandas.read_excel(filename, sheet_name="stem.list")
    return Source(df_kanji, df_keyword, df_stem)


def init_categorization(source: Source) -> Categorization:
    categorization = {}

    for grp in source.df_keyword["GROUP"].unique():
        categorization[grp] = []

    for grp in source.df_stem["GROUP"].unique():
        categorization[grp] = []

    categorization[Constants.other_grp] = []
    categorization[Constants.special_grp] = []
    categorization[Constants.visual_grp] = []

    queue = {}
    return Categorization(categorization, queue)


def find_keyword(kanji: Kanji, source: Source) -> str:
    group = source.df_keyword[source.df_keyword["KEYWORD"] == kanji.keyword]["GROUP"]
    if group.empty:
        return "none"
    else:
        return group.iloc[0]


def find_stem(kanji: Kanji, source: Source) -> str:
    group = source.df_stem[source.df_stem["STEM KANJI"] == kanji.char]["GROUP"]
    if group.empty:
        return "none"
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


def get_kanji_component(component: str, kanji: Kanji) -> str:
    if component == "COMPONENTS1":
        return kanji.component1
    elif component == "COMPONENTS2":
        return kanji.component2
    elif component == "COMPONENTS3":
        return kanji.component3
    elif component == "COMPONENTS4":
        return kanji.component4
    elif component == "COMPONENTS5":
        return kanji.component5
    else:
        return "missing component"


def find_cluster_1_2_components(component: str, kanji: Kanji, source: Source) -> pandas.DataFrame:
    kanji_component = get_kanji_component(component, kanji)
    return source.df_kanji[
        ((source.df_kanji["COMPONENTS1"] == kanji_component) |
         (source.df_kanji["COMPONENTS2"] == kanji_component))
        & (source.df_kanji["CHAR"] != kanji.char)
        ]


def find_cluster_components(component: str, kanji: Kanji, source: Source) -> pandas.DataFrame:
    kanji_component = get_kanji_component(component, kanji)
    return source.df_kanji[
        ((source.df_kanji["COMPONENTS2"] == kanji_component) |
         (source.df_kanji["COMPONENTS3"] == kanji_component) |
         (source.df_kanji["COMPONENTS4"] == kanji_component) |
         (source.df_kanji["COMPONENTS5"] == kanji_component))
        & (source.df_kanji["CHAR"] != kanji.char)
        ]


def find_cluster_all_components(component: str, kanji: Kanji, source: Source) -> pandas.DataFrame:
    kanji_component = get_kanji_component(component, kanji)
    return source.df_kanji[
        ((source.df_kanji["COMPONENTS1"] == kanji_component) |
         (source.df_kanji["COMPONENTS2"] == kanji_component) |
         (source.df_kanji["COMPONENTS3"] == kanji_component) |
         (source.df_kanji["COMPONENTS4"] == kanji_component) |
         (source.df_kanji["COMPONENTS5"] == kanji_component))
        & (source.df_kanji["CHAR"] != kanji.char)
        ]


def find_max_srv(dataframe: pandas.DataFrame):
    return dataframe[dataframe["SRL"] == dataframe["SRL"].max()].iloc[0]


def find_onyomi(kanji: Kanji, vr_cluster: pandas.DataFrame, categorization: Categorization,
                source: Source):
    vr_crowns = kanji.on_reading.split("、")
    onyomi = vr_cluster[vr_cluster["ON READING"].isin(vr_crowns)]
    if onyomi.empty:
        logger.info("4. rule - 3rd condition")
        vr_third_cluster = source.df_kanji[source.df_kanji["CHAR"] == kanji.component2]
        if len(vr_third_cluster.index) > 0:
            if len(vr_third_cluster.index) > 1:
                logger.info("kanji > 1")
                max_srl_kanji = find_max_srv(vr_third_cluster)
                kanji.type = "VR"

                if max_srl_kanji["CHAR"] in categorization.queue.keys():
                    categorization.queue[max_srl_kanji["CHAR"]].append(kanji)
                else:
                    categorization.queue[max_srl_kanji["CHAR"]] = []
                    categorization.queue[max_srl_kanji["CHAR"]].append(kanji)
            else:
                logger.info("kanji = 1")
                kanji.type = "VR"
                max_srl_kanji = vr_third_cluster.iloc[0]
                if max_srl_kanji["CHAR"] in categorization.queue.keys():
                    categorization.queue[vr_third_cluster.iloc[0]["CHAR"]].append(kanji)
                else:
                    categorization.queue[vr_third_cluster.iloc[0]["CHAR"]] = []
                    categorization.queue[vr_third_cluster.iloc[0]["CHAR"]].append(kanji)
        else:
            fifth_rule(kanji, categorization, source)
    else:
        if len(onyomi.index) > 1:
            logger.info("kanji > 1")
            max_srl_kanji = find_max_srv(onyomi)
            logger.info("max srl kanji: {}".format(max_srl_kanji["CHAR"]))
            kanji.type = "VR"

            if max_srl_kanji["CHAR"] in categorization.queue.keys():
                categorization.queue[max_srl_kanji["CHAR"]].append(kanji)
            else:
                categorization.queue[max_srl_kanji["CHAR"]] = []
                categorization.queue[max_srl_kanji["CHAR"]].append(kanji)
        else:
            logger.info("kanji = 1")
            kanji.type = "VR"
            max_srl_kanji = onyomi.iloc[0]
            if max_srl_kanji["CHAR"] in categorization.queue.keys():
                categorization.queue[onyomi.iloc[0]["CHAR"]].append(kanji)
            else:
                categorization.queue[onyomi.iloc[0]["CHAR"]] = []
                categorization.queue[onyomi.iloc[0]["CHAR"]].append(kanji)


def seventh_rule(kanji: Kanji, categorization: Categorization):
    logger.warning("TODO 7. rule")
    append_categorization(Constants.other_grp, kanji, False, categorization)


def sixth_rule(kanji: Kanji, categorization: Categorization, source: Source):
    logger.info("6. rule")
    vr_cluster_1_2 = pandas.concat([
        find_cluster_1_2_components("COMPONENTS1", kanji, source),
        find_cluster_1_2_components("COMPONENTS2", kanji, source)
    ])
    if vr_cluster_1_2.empty:
        seventh_rule(kanji, categorization)
    else:
        if len(vr_cluster_1_2.index) > 1:
            append_categorization(Constants.visual_grp, kanji, False, categorization)
        else:
            kanji.type = "VISUAL"
            max_srl_kanji = vr_cluster_1_2.iloc[0]
            if max_srl_kanji["CHAR"] in categorization.queue.keys():
                categorization.queue[vr_cluster_1_2.iloc[0]["CHAR"]].append(kanji)
            else:
                categorization.queue[vr_cluster_1_2.iloc[0]["CHAR"]] = []
                categorization.queue[vr_cluster_1_2.iloc[0]["CHAR"]].append(kanji)


def fifth_rule(kanji: Kanji, categorization: Categorization, source: Source):
    logger.info("5. rule")
    group_stem = source.df_stem[
        (source.df_stem["STEM KANJI"] == kanji.component1) |
        (source.df_stem["STEM KANJI"] == kanji.component2) |
        (source.df_stem["STEM KANJI"] == kanji.component3)
        ]["GROUP"]
    if group_stem.empty:
        sixth_rule(kanji, categorization, source)
    else:
        if kanji.srl == 1:
            kanji.type = "FORM"
        else:
            kanji.type = "MEAN"
        if len(group_stem) == 1:
            append_categorization(group_stem.iloc[0], kanji, False, categorization)
        else:
            print("more stems TODO")


def fourth_rule(kanji: Kanji, categorization: Categorization, source: Source):
    logger.info("4. rule")
    vr_cluster = pandas.concat([
        find_cluster_components("COMPONENTS2", kanji, source),
        find_cluster_components("COMPONENTS3", kanji, source),
        find_cluster_components("COMPONENTS4", kanji, source),
        find_cluster_components("COMPONENTS5", kanji, source)
    ])
    if vr_cluster.empty:
        vr_all_cluster = pandas.concat([
            find_cluster_all_components("COMPONENTS1", kanji, source),
            find_cluster_all_components("COMPONENTS2", kanji, source),
            find_cluster_all_components("COMPONENTS3", kanji, source),
            find_cluster_all_components("COMPONENTS4", kanji, source),
            find_cluster_all_components("COMPONENTS5", kanji, source)
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
            ds.union(char["CHAR"], key)
    for key in categorization.queue:
        for char in categorization.queue[key]:
            ds.union(char["CHAR"], key)

    print(ds)
    for key in categorization.queue:
        for char in categorization.queue[key]:
            categorization.result[ds.find(char["CHAR"])].append(char)


def categorize_kanji(kanji: Kanji, categorization: Categorization, source: Source):
    first_rule = find_keyword(kanji, source)
    second_rule = find_stem(kanji, source)
    # TODO check elif
    if first_rule != "none":
        logger.info("1. rule")
        if kanji.type == "MEAN":
            append_categorization(first_rule, kanji, False, categorization)
        else:
            if kanji.type == "SPECIAL":
                append_categorization(Constants.special_grp, kanji, False, categorization)
            else:
                if kanji.type == "OTHER":
                    append_categorization(Constants.other_grp, kanji, False, categorization)
                else:
                    print("ERROR: missing grp")
    else:
        if second_rule != "none":
            logger.info("2. rule")
            if kanji.type == "STEM":
                append_categorization(second_rule, kanji, True, categorization)
            else:
                print("ERROR: missing rule")
        else:
            components = source.df_kanji[
                (source.df_kanji["COMPONENTS1"] == kanji.char) | (source.df_kanji["COMPONENTS2"] == kanji.char)]
            logger.info("components count: " + str(len(components.index)))
            if components.empty:
                fourth_rule(kanji, categorization, source)
            else:
                logger.info("3. rule")
                vr_crowns = kanji.on_reading.split("、")
                onyomi = components[components["ON READING"].isin(vr_crowns)]
                if onyomi.empty:
                    logger.info("onyomi empty")
                    fourth_rule(kanji, categorization, source)
                else:
                    logger.info("3. rule a) b)")
                    if len(onyomi.index) > 1:
                        logger.info("kanji > 1")
                        max_srl_kanji = onyomi[onyomi["SRL"] == onyomi["SRL"].max()].iloc[0]
                        kanji.tags.append("CROWN_TAG")
                        kanji.type = "VR"

                        if max_srl_kanji["CHAR"] in categorization.queue.keys():
                            categorization.queue[max_srl_kanji["CHAR"]].append(kanji)
                        else:
                            categorization.queue[max_srl_kanji["CHAR"]] = []
                            categorization.queue[max_srl_kanji["CHAR"]].append(kanji)
                    else:
                        logger.info("kanji = 1")
                        kanji.tags.append("CROWN_TAG")
                        kanji.type = "VR"
                        max_srl_kanji = onyomi.iloc[0]
                        if max_srl_kanji["CHAR"] in categorization.queue.keys():
                            categorization.queue[onyomi.iloc[0]["CHAR"]].append(kanji)
                        else:
                            categorization.queue[onyomi.iloc[0]["CHAR"]] = []
                            categorization.queue[onyomi.iloc[0]["CHAR"]].append(kanji)
