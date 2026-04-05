"""Export categorization results to Anki .apkg deck files."""

import genanki

# Stable IDs so re-exports update existing cards rather than creating duplicates
_MODEL_ID = 1607392319
_DECK_ID = 2059400110

_MODEL = genanki.Model(
    _MODEL_ID,
    "Kanji MBO",
    fields=[
        {"name": "Kanji"},
        {"name": "Keyword"},
        {"name": "OnYomi"},
        {"name": "KunYomi"},
        {"name": "Components"},
        {"name": "Group"},
        {"name": "SRL"},
        {"name": "Type"},
    ],
    templates=[
        {
            "name": "Kanji → Keyword",
            "qfmt": '<div style="font-size:72px;text-align:center;">{{Kanji}}</div>',
            "afmt": '{{FrontSide}}<hr id="answer">'
                    '<div style="text-align:center;">'
                    "<b>{{Keyword}}</b><br>"
                    "On: {{OnYomi}}<br>"
                    "Kun: {{KunYomi}}<br>"
                    "Components: {{Components}}<br>"
                    "Group: {{Group}} | Type: {{Type}}"
                    "</div>",
        },
        {
            "name": "Keyword → Kanji",
            "qfmt": '<div style="font-size:24px;text-align:center;">{{Keyword}}</div>',
            "afmt": '{{FrontSide}}<hr id="answer">'
                    '<div style="font-size:72px;text-align:center;">{{Kanji}}</div>'
                    '<div style="text-align:center;">'
                    "On: {{OnYomi}}<br>"
                    "Kun: {{KunYomi}}<br>"
                    "Components: {{Components}}"
                    "</div>",
        },
    ],
)


def export_categorization(categorization, output_path="kanji_mbo.apkg", deck_name="Kanji MBO"):
    deck = genanki.Deck(_DECK_ID, deck_name)

    for group_name in sorted(categorization.result):
        for kanji in categorization.result[group_name]:
            note = genanki.Note(
                model=_MODEL,
                fields=[
                    kanji.char,
                    kanji.keyword,
                    kanji.on_reading_str,
                    kanji.kun_reading,
                    kanji.components_str,
                    group_name,
                    str(kanji.srl),
                    kanji.type,
                ],
            )
            deck.add_note(note)

    package = genanki.Package(deck)
    package.write_to_file(output_path)
    return output_path
