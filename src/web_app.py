"""Streamlit web UI for browsing kanji groups.

Run with: streamlit run src/web_app.py
"""

import sys
import os

# Ensure src/ is on the path
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import algorithm

DEFAULT_FILE = os.path.join(os.path.dirname(__file__), "..", "excel", "1500 KANJI COMPONENTS - ver. 1.3.xlsx")


@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def load_data(filepath):
    return algorithm.run_pipeline(filepath)


def main():
    st.set_page_config(page_title="Kanji MBO", page_icon="\u6f22", layout="wide")
    st.title("\u6f22 Kanji MBO Browser")

    filepath = st.sidebar.text_input("Excel file path", value=DEFAULT_FILE)

    try:
        categorization, source = load_data(filepath)
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return

    groups = sorted(categorization.result.keys())
    total_kanji = sum(len(v) for v in categorization.result.values())
    st.sidebar.metric("Total groups", len(groups))
    st.sidebar.metric("Total kanji", total_kanji)

    tab_groups, tab_search, tab_lookup = st.tabs(["Groups", "Search", "Lookup"])

    with tab_groups:
        selected_group = st.selectbox("Select a group", groups)
        if selected_group:
            kanji_list = categorization.result[selected_group]
            st.subheader(f"{selected_group} ({len(kanji_list)} kanji)")

            for k in sorted(kanji_list, key=lambda x: x.ref, reverse=True):
                with st.expander(f"{k.char}  \u2014  {k.keyword}"):
                    col1, col2, col3 = st.columns(3)
                    col1.markdown(f"**On'yomi:** {k.on_reading_str}")
                    col1.markdown(f"**Kun'yomi:** {k.kun_reading}")
                    col2.markdown(f"**Components:** {k.components_str}")
                    col2.markdown(f"**SRL:** {k.srl}")
                    col3.markdown(f"**Type:** {k.type}")
                    col3.markdown(f"**Frequency:** {k.freq}")
                    if k.ref != k.char:
                        col3.markdown(f"**Ref:** {k.ref}")

    with tab_search:
        query = st.text_input("Search by keyword or on'yomi reading")
        if query:
            results = []
            for group_name, kanji_list in categorization.result.items():
                for k in kanji_list:
                    if (query.lower() in k.keyword.lower()
                            or query in k.on_reading
                            or query == k.char):
                        results.append((group_name, k))
            st.write(f"Found {len(results)} results")
            for group_name, k in results:
                st.write(f"**{k.char}** \u2014 {k.keyword} | On: {k.on_reading_str} | Group: {group_name}")

    with tab_lookup:
        chars = st.text_input("Enter kanji characters (space-separated)")
        if chars:
            for char in chars.split():
                try:
                    k = algorithm.read_kanji_char(char, source)
                    st.markdown(f"""
| Field | Value |
|-------|-------|
| Character | {k.char} |
| Keyword | {k.keyword} |
| On'yomi | {k.on_reading_str} |
| Kun'yomi | {k.kun_reading} |
| Components | {k.components_str} |
| SRL | {k.srl} |
| Type | {k.type} |
| Frequency | {k.freq} |
| Group | {k.group} |
""")
                except (IndexError, KeyError):
                    st.warning(f"Kanji '{char}' not found in data")


if __name__ == "__main__":
    main()
