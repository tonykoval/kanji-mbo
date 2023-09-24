import logging

import algorithm

algorithm.set_logging_level(logging.INFO)
# algorithm.set_logging_level(logging.WARNING)
# source = algorithm.read_excel("1500 KANJI COMPONENTS - ver. 1.3.xlsx")
source = algorithm.read_excel("2250 KANJI COMPONENTS - ver. 1.0.xlsx")

categorization = algorithm.init_categorization(source)
# {'磨', '麻', '摩'}

algorithm.categorize_kanji(algorithm.read_kanji_char("欧", source), categorization, source)
# algorithm.categorize_kanji(algorithm.read_kanji_char("麻", source), categorization, source)
# algorithm.categorize_kanji(algorithm.read_kanji_char("摩", source), categorization, source)
#
# for i in range(len(source.df_kanji)):
#     # print(i)
#     row = algorithm.read_kanji(source.df_kanji.loc[i])
#     # print(row.char)
#     algorithm.categorize_kanji(row, categorization, source)
#     print("-----------------")
#
# algorithm.categorize_queue(categorization)
#
# print("categorization")
# for key in categorization.result:
#      print(key)
#      for kanji in categorization.result[key]:
#         print(kanji.char)
#
# print("queue_categorization")
# for key in categorization.queue:
#      print("key: ", key)
#      for kanji in categorization.queue[key]:
#          print(kanji.char)
#      print("----")
