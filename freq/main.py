import logging

import freq.algorithm as algorithm

import sys
sys.stdout = open('output.txt', 'wt', encoding="utf-8")

algorithm.set_logging_level(logging.INFO)
list_kanji = algorithm.read_kanji_dataframe(algorithm.read_excel("1,200 KANJI.xlsx"))

result = []

for kanji in list_kanji:
    algorithm.categorize_kanji(kanji, result, list_kanji)

num = 1
for res in result:
    print(f"{num}: {res.char} -> {res.ref}")
    num +=1

# for i in range(len(list_kanji)):
#     # print(i)
#     # print(row.kanji)
#     algorithm.categorize_kanji(row, result, source)
#     print("-----------------")

# print("categorization")
# for key in categorization.result:
#     print(key)
#     for kanji in sorted(categorization.result[key], key=lambda x: x.ref, reverse=True):
#         print(kanji.char, " (", kanji.ref, ")")
#
# print("subgroup categorization")
# for key in dict(sorted(categorization.result.items())):
#     print(key)
#     res = {}
#     for kanji in sorted(categorization.result[key], key=lambda x: x.ref, reverse=True):
#         if kanji.group == '':
#             kanji_group = "companion"
#         else:
#             kanji_group = kanji.group
#
#         if kanji_group in res.keys():
#             res[kanji_group].append(kanji.char)
#         else:
#             res[kanji_group] = [kanji.char]
#     print(dict(sorted(res.items())))

# print("queue_categorization")
# for key in categorization.queue:
#      print("key: ", key)
#      for kanji in categorization.queue[key]:
#          print(kanji.char)
#      print("----")
