import algorithm

source = algorithm.read_excel("1500 KANJI COMPONENTS - ver. 1.2.xlsx")

categorization = algorithm.init_categorization(source)

# algorithm.categorize_kanji(source.df_kanji[source.df_kanji["CHAR"] == '憶'].iloc[0], categorization, source)
# algorithm.categorize_kanji(source.df_kanji[source.df_kanji["CHAR"] == '屋'].iloc[0], categorization, source)
# algorithm.categorize_kanji(source.df_kanji[source.df_kanji["CHAR"] == '億'].iloc[0], categorization, source)

for i in range(len(source.df_kanji)):
    kanji = source.df_kanji.loc[i]
    # print(kanji["CHAR"])
    algorithm.categorize_kanji(kanji, categorization, source)

algorithm.categorize_queue(categorization)

print("categorization")
for key in categorization.result:
    print(key)
    for ch in categorization.result[key]:
        print(ch["CHAR"])

print("queue_categorization")
for key in categorization.queue:
    print("key: ", key)
    for ch in categorization.queue[key]:
        print(ch["CHAR"])
    print("----")
