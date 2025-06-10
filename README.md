# Kanji Ordering Algorithm for Doctoral Research

This project was created as part of my doctoral thesis investigating the long-term effect of multicriteria-based ordering on the retention rate of the Japanese logographic script known as *kanji*. The main goal was to reproduce the ordering algorithm I used to manually order 2,000 and 1,500 kanji. The semantic-based ordering system was subsequently utilized to order as many as 2,250 kanji, followed by a version ordering 1,200 kanji based on usage frequency and phonetic reliability (kanji with the same component and the same Sino-Japanese reading, or *on’yomi*, grouped together, regardless of usage frequency).

Considering how time-consuming it was to reorder 1,500 kanji based on the principles I had used to manually order 2,000 kanji (in the MBO version 5.9 presented in my master’s thesis), I concluded it would be useful to create an automated version of the ordering system. This would allow others to apply multicriterial ordering to a different number of kanji without repeating the manual process.

With the help of my colleague Anton, we managed to automate the ordering for up to 2,250 kanji and even developed a modified ordering system for 1,200 kanji. However, several limitations became apparent:

### Key Limitations

1. **Scalability Issues**  
   The original semantic-based ordering system (used for 1,500 and 2,250 kanji) should not be applied to fewer than 1,000 kanji. The more kanji included, the more effective the multicriterial system becomes. It may even be beneficial for native Japanese speakers studying for **Kanji Kentei Level 1**, which covers over 6,000 kanji.

2. **System Adaptation**  
   When applying the system to significantly different kanji counts, some modifications are likely necessary — such as changes in group structure or character decomposition. For example, applying the system designed for 1,500–2,250 kanji to a set of 1,800 kanji can lead to a higher number of “OTHER”-type kanji and similar issues.

3. **Automation Limitations**  
   While partial automation was achieved, complete automation was hindered by two main challenges:
   - **Character decomposition**
   - **Ordering within semantic groups and subgroups**

   While decomposition might be solvable via neural networks, the semantic-based ordering of chief ("MEAN"-type) kanji remains more difficult. For now, the algorithm's main function is **categorization** rather than precise ordering — though certain kanji types are indeed ordered.

---

## How to Use

If you're interested in ordering a kanji set (ideally over 1,000 kanji) using either the **multicriterial** (1,500 or 2,250 kanji) or **frequency-based** (1,200 kanji) method:

1. Create an Excel file with the **same column structure** as one of the original lists.
2. Copy the data from the respective list into your Excel file.

### Notes on Frequency Data

Kanji frequency numbers were calculated using **seven different frequency databases**, including:
- Shibano’s Google Data
- Matsushita’s Character Database

For more details, refer to:
- *“How Reliable and Consistent Are Kanji Frequency Databases?”*
- *“2242 Kanji Frequency List ver. 1.1”* — available on my [ResearchGate profile](https://www.researchgate.net/publication/357159664_2242_Kanji_Frequency_List_ver_11/)

### Notes on Readings

While nearly all official readings are included in the 2,250-kanji Excel list, some readings were excluded from:
- the 1,500-kanji list
- and even more from the 1,200-kanji list

This editorial decision is discussed in the article:  
*“How Many Jōyō Kanji Readings Are Rarely Used?”*

---

## How to Run the Algorithm

*(To be added)*
