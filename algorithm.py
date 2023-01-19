import pandas
from typing import Tuple, Type

from model import Source, Categorization, Constants


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


def find_keyword(row: pandas.DataFrame, source: Source) -> str:
    group = source.df_keyword[source.df_keyword["KEYWORD"] == row["KEYWORD"]]["GROUP"]
    if group.empty:
        return "none"
    else:
        return group.iloc[0]


def find_stem(row: pandas.DataFrame, source: Source) -> str:
    group = source.df_stem[source.df_stem["STEM KANJI"] == row["CHAR"]]["GROUP"]
    if group.empty:
        return "none"
    else:
        return group.iloc[0]


def append_categorization(char: str, row: pandas.DataFrame, is_first: bool, categorization: Categorization):
    if is_first:
        if row["CHAR"] in categorization.queue.keys():
            for ch in categorization.queue[row["CHAR"]]:
                categorization.result[char].insert(0, ch)
            categorization.result[char].insert(0, row)
            del categorization.queue[row["CHAR"]]
        else:
            categorization.result[char].insert(0, row)
    else:
        if row["CHAR"] in categorization.queue.keys():
            categorization.result[char].append(row)
            for ch in categorization.queue[row["CHAR"]]:
                categorization.result[char].append(ch)
            del categorization.queue[row["CHAR"]]
        else:
            categorization.result[char].append(row)


def find_cluster_1_2_components(component: str, row: pandas.DataFrame, source: Source) -> pandas.DataFrame:
    return source.df_kanji[
        ((source.df_kanji["COMPONENTS1"] == row[component]) |
         (source.df_kanji["COMPONENTS2"] == row[component]))
        & (source.df_kanji["CHAR"] != row["CHAR"])
        ]


def find_cluster_components(component: str, row: pandas.DataFrame, source: Source) -> pandas.DataFrame:
    return source.df_kanji[
        ((source.df_kanji["COMPONENTS2"] == row[component]) |
         (source.df_kanji["COMPONENTS3"] == row[component]) |
         (source.df_kanji["COMPONENTS4"] == row[component]) |
         (source.df_kanji["COMPONENTS5"] == row[component]))
        & (source.df_kanji["CHAR"] != row["CHAR"])
        ]


def find_cluster_all_components(component: str, row: pandas.DataFrame, source: Source) -> pandas.DataFrame:
    return source.df_kanji[
        ((source.df_kanji["COMPONENTS1"] == row[component]) |
         (source.df_kanji["COMPONENTS2"] == row[component]) |
         (source.df_kanji["COMPONENTS3"] == row[component]) |
         (source.df_kanji["COMPONENTS4"] == row[component]) |
         (source.df_kanji["COMPONENTS5"] == row[component]))
        & (source.df_kanji["CHAR"] != row["CHAR"])
        ]


def find_onyomi(row: pandas.DataFrame, vr_cluster: pandas.DataFrame, categorization: Categorization,
                source: Source):
    vr_crowns = row["ON READING"].split("、")
    onyomi = vr_cluster[vr_cluster["ON READING"].isin(vr_crowns)]
    if onyomi.empty:
        #         print("4. rule - 3rd condition")
        vr_third_cluster = source.df_kanji[source.df_kanji["CHAR"] == row["COMPONENTS2"]]
        if len(vr_third_cluster.index) > 0:
            if len(vr_third_cluster.index) > 1:
                #                 print("kanji > 1")
                max_srl_kanji = vr_third_cluster[vr_third_cluster["SRL"] == vr_third_cluster["SRL"].max()].iloc[0]
                row["TYPE"] = "VR"

                if max_srl_kanji["CHAR"] in categorization.queue.keys():
                    categorization.queue[max_srl_kanji["CHAR"]].append(row)
                else:
                    categorization.queue[max_srl_kanji["CHAR"]] = []
                    categorization.queue[max_srl_kanji["CHAR"]].append(row)
            else:
                #                 print("kanji = 1")
                row["TYPE"] = "VR"
                max_srl_kanji = vr_third_cluster.iloc[0]
                if max_srl_kanji["CHAR"] in categorization.queue.keys():
                    categorization.queue[vr_third_cluster.iloc[0]["CHAR"]].append(row)
                else:
                    categorization.queue[vr_third_cluster.iloc[0]["CHAR"]] = []
                    categorization.queue[vr_third_cluster.iloc[0]["CHAR"]].append(row)
        else:
            fifth_rule(row, categorization, source)
    else:
        if len(onyomi.index) > 1:
            #             print("kanji > 1")
            max_srl_kanji = onyomi[onyomi["SRL"] == onyomi["SRL"].max()].iloc[0]
            row["TYPE"] = "VR"

            if max_srl_kanji["CHAR"] in categorization.queue.keys():
                categorization.queue[max_srl_kanji["CHAR"]].append(row)
            else:
                categorization.queue[max_srl_kanji["CHAR"]] = []
                categorization.queue[max_srl_kanji["CHAR"]].append(row)
        else:
            #             print("kanji = 1")
            row["TYPE"] = "VR"
            max_srl_kanji = onyomi.iloc[0]
            if max_srl_kanji["CHAR"] in categorization.queue.keys():
                categorization.queue[onyomi.iloc[0]["CHAR"]].append(row)
            else:
                categorization.queue[onyomi.iloc[0]["CHAR"]] = []
                categorization.queue[onyomi.iloc[0]["CHAR"]].append(row)


def seventh_rule(row: pandas.DataFrame, categorization: Categorization):
    #     print("TODO 7. rule")
    append_categorization(Constants.other_grp, row, False, categorization)


def sixth_rule(row: pandas.DataFrame, categorization: Categorization, source: Source):
    #     print("6. rule")
    vr_cluster_1_2 = pandas.concat([
        find_cluster_1_2_components("COMPONENTS1", row, source),
        find_cluster_1_2_components("COMPONENTS2", row, source)
    ])
    if vr_cluster_1_2.empty:
        seventh_rule(row, categorization)
    else:
        if len(vr_cluster_1_2.index) > 1:
            append_categorization(Constants.visual_grp, row, False, categorization)
        else:
            row["TYPE"] = "VISUAL"
            max_srl_kanji = vr_cluster_1_2.iloc[0]
            if max_srl_kanji["CHAR"] in categorization.queue.keys():
                categorization.queue[vr_cluster_1_2.iloc[0]["CHAR"]].append(row)
            else:
                categorization.queue[vr_cluster_1_2.iloc[0]["CHAR"]] = []
                categorization.queue[vr_cluster_1_2.iloc[0]["CHAR"]].append(row)


def fifth_rule(row: pandas.DataFrame, categorization: Categorization, source: Source):
    #     print("5. rule")
    group_stem = source.df_stem[
        (source.df_stem["STEM KANJI"] == row["COMPONENTS1"]) |
        (source.df_stem["STEM KANJI"] == row["COMPONENTS2"]) |
        (source.df_stem["STEM KANJI"] == row["COMPONENTS3"])
        ]["GROUP"]
    if group_stem.empty:
        sixth_rule(row, categorization, source)
    else:
        if row["SRL"] == 1:
            row["TYPE"] = "FORM"
        else:
            row["TYPE"] = "MEAN"
        if len(group_stem) == 1:
            append_categorization(group_stem.iloc[0], row, False, categorization)
        else:
            print("more stems TODO")


def fourth_rule(row: pandas.DataFrame, categorization: Categorization, source: Source):
    #     print("4. rule")
    vr_cluster = pandas.concat([
        find_cluster_components("COMPONENTS2", row, source),
        find_cluster_components("COMPONENTS3", row, source),
        find_cluster_components("COMPONENTS4", row, source),
        find_cluster_components("COMPONENTS5", row, source)
    ])
    if vr_cluster.empty:
        vr_all_cluster = pandas.concat([
            find_cluster_all_components("COMPONENTS1", row, source),
            find_cluster_all_components("COMPONENTS2", row, source),
            find_cluster_all_components("COMPONENTS3", row, source),
            find_cluster_all_components("COMPONENTS4", row, source),
            find_cluster_all_components("COMPONENTS5", row, source)
        ])
        if vr_all_cluster.empty:
            fifth_rule(row, categorization, source)
        else:
            #             print("vr all cluster")
            find_onyomi(row, vr_all_cluster, categorization, source)
    else:
        #         print("vr clusters")
        find_onyomi(row, vr_cluster, categorization, source)


def find_char_categorization(char: str, categorization: Categorization):
    for key in categorization.result:
        for ch in categorization.result[key]:
            if ch["CHAR"] == char:
                return key
            else:
                continue


def categorize_queue(categorization: Categorization):
    for key in categorization.queue:
        tmp = find_char_categorization(key, categorization)
        if tmp is None:
            print(key)
        else:
            tmp_dict = categorization.result[tmp]
            for ch in categorization.queue[key]:
                tmp_dict.append(ch)
            # categorization.result[tmp].deepcopy(tmp_dict)
            del categorization.queue[key]


def categorize_kanji(row: pandas.DataFrame, categorization: Categorization, source: Source):
    first_rule = find_keyword(row, source)
    second_rule = find_stem(row, source)
    if first_rule != "none":
        #         print("1. rule")
        if row["TYPE"] == "MEAN":
            append_categorization(first_rule, row, False, categorization)
        else:
            if row["TYPE"] == "SPECIAL":
                append_categorization(Constants.special_grp, row, False, categorization)
            else:
                if row["TYPE"] == "OTHER":
                    append_categorization(Constants.other_grp, row, False, categorization)
                else:
                    print("ERROR: missing grp")
    else:
        if second_rule != "none":
            #             print("2. rule")
            if row["TYPE"] == "STEM":
                append_categorization(second_rule, row, True, categorization)
            else:
                print("ERROR: missing rule")
        else:
            components = source.df_kanji[
                (source.df_kanji["COMPONENTS1"] == row["CHAR"]) | (source.df_kanji["COMPONENTS2"] == row["CHAR"])]
            #             print("components count: " + str(len(components.index)))
            if components.empty:
                fourth_rule(row, categorization, source)
            else:
                #                 print("3. rule")
                vr_crowns = row["ON READING"].split("、")
                #                 print(vr_crowns)
                onyomi = components[components["ON READING"].isin(vr_crowns)]
                if onyomi.empty:
                    #                     print("onyomi empty")
                    fourth_rule(row, categorization, source)
                else:
                    #                     print("3. rule a) b)")
                    if len(onyomi.index) > 1:
                        #                         print("kanji > 1")
                        #                         print(onyomi)
                        max_srl_kanji = onyomi[onyomi["SRL"] == onyomi["SRL"].max()].iloc[0]
                        row["TAG"] = "CROWN_TAG"
                        row["TYPE"] = "VR"

                        if max_srl_kanji["CHAR"] in categorization.queue.keys():
                            categorization.queue[max_srl_kanji["CHAR"]].append(row)
                        else:
                            categorization.queue[max_srl_kanji["CHAR"]] = []
                            categorization.queue[max_srl_kanji["CHAR"]].append(row)
                    else:
                        #                         print("kanji = 1")
                        row["TAG"] = "CROWN_TAG"
                        row["TYPE"] = "VR"
                        max_srl_kanji = onyomi.iloc[0]
                        if max_srl_kanji["CHAR"] in categorization.queue.keys():
                            categorization.queue[onyomi.iloc[0]["CHAR"]].append(row)
                        else:
                            categorization.queue[onyomi.iloc[0]["CHAR"]] = []
                            categorization.queue[onyomi.iloc[0]["CHAR"]].append(row)
