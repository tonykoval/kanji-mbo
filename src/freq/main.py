import logging
import sys
from operator import attrgetter

from disjoint_set import DisjointSet

import src.freq.algorithm as algorithm

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