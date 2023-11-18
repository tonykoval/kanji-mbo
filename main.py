import logging

import algorithm

algorithm.set_logging_level(logging.INFO)
# algorithm.set_logging_level(logging.WARNING)
# source = algorithm.read_excel("1500 KANJI COMPONENTS - ver. 1.3.xlsx")
source = algorithm.read_excel("2250 KANJI COMPONENTS - ver. 1.0.xlsx")

categorization = algorithm.init_categorization(source)
# {'磨', '麻', '摩'}

# algorithm.categorize_kanji(algorithm.read_kanji_char("酢", source), categorization, source)
# algorithm.categorize_kanji(algorithm.read_kanji_char("麻", source), categorization, source)
# algorithm.categorize_kanji(algorithm.read_kanji_char("摩", source), categorization, source)
#
for i in range(len(source.df_kanji)):
    # print(i)
    row = algorithm.read_kanji(source.df_kanji.loc[i])
    # print(row.char)
    algorithm.categorize_kanji(row, categorization, source)
    print("-----------------")

algorithm.categorize_queue(categorization)

# print("categorization")
# for key in categorization.result:
#      print(key)
#      for kanji in sorted(categorization.result[key], key=lambda x: x.ref, reverse=True):
#         print(kanji.char, " (", kanji.ref, ")")

print("subgroup categorization")
for key in dict(sorted(categorization.result.items())):
    print(key)
    res = {}
    for kanji in sorted(categorization.result[key], key=lambda x: x.ref, reverse=True):
        if kanji.group == '':
            kanji_group = "companion"
        else:
            kanji_group = kanji.group

        if kanji_group in res.keys():
            res[kanji_group].append(kanji.char)
        else:
            res[kanji_group] = [kanji.char]
    print(dict(sorted(res.items())))

# print("queue_categorization")
# for key in categorization.queue:
#      print("key: ", key)
#      for kanji in categorization.queue[key]:
#          print(kanji.char)
#      print("----")
