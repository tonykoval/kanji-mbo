import logging
from operator import attrgetter

from disjoint_set import DisjointSet

import src.freq.algorithm as algorithm

import sys

sys.stdout = open('output.txt', 'wt', encoding="utf-8")

algorithm.set_logging_level(logging.INFO)
list_kanji = algorithm.read_kanji_dataframe(algorithm.read_excel("1,200 KANJI.xlsx"))

result = []

for kanji in list_kanji:
    algorithm.categorize_kanji(kanji, result, list_kanji)

ds = DisjointSet()

for k in result:
    ds.union(k.char, k.ref)

print(ds)

num = 1
for r in ds.itersets(with_canonical_elements=False):
    # ds.find(r.char)
    res = []
    for ch in r:
        for k in list_kanji:
            if k.char == ch:
                res.append(k)
                break

    sorted_people = sorted(res, key=attrgetter('freq'))

    for ch in sorted_people:
        print(f'{num}: {ch.char}')
        num += 1
    # print(r)
    # for k, v in r:
    #     print(k, v)
    # print(f'{num}: {r.}')

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
