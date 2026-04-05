"""Generate a static HTML site in docs/ from Excel kanji data."""

import json
import os
import sys
from html import escape

sys.path.insert(0, os.path.dirname(__file__))

import algorithm


def build_groups_data(categorization):
    groups = {}
    for group_name in sorted(categorization.result):
        kanji_list = sorted(categorization.result[group_name], key=lambda x: x.ref, reverse=True)
        groups[group_name] = [
            {
                "char": k.char,
                "ref": k.ref,
                "keyword": k.keyword,
                "on_reading": k.on_reading_str,
                "kun_reading": k.kun_reading,
                "components": k.components_str,
                "srl": k.srl,
                "type": k.type,
                "freq": k.freq,
                "group": k.group,
            }
            for k in kanji_list
        ]
    return groups


def generate_html(groups, title, filename):
    total_kanji = sum(len(v) for v in groups.values())
    groups_json = json.dumps(groups, ensure_ascii=False)
    title_esc = escape(title)

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title_esc}</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f1117; color: #e0e0e0; }}
.header {{ background: #161923; border-bottom: 1px solid #2a2d3a; padding: 16px 24px; position: sticky; top: 0; z-index: 100; }}
.header h1 {{ font-size: 20px; color: #fff; }}
.header .stats {{ font-size: 13px; color: #888; margin-top: 4px; }}
.container {{ display: flex; height: calc(100vh - 70px); }}
.sidebar {{ width: 280px; min-width: 280px; background: #161923; border-right: 1px solid #2a2d3a; overflow-y: auto; padding: 8px 0; }}
.sidebar input {{ width: calc(100% - 16px); margin: 8px; padding: 8px 12px; background: #1e2130; border: 1px solid #2a2d3a; border-radius: 6px; color: #e0e0e0; font-size: 14px; outline: none; }}
.sidebar input:focus {{ border-color: #4a9eff; }}
.sidebar .group-item {{ padding: 8px 16px; cursor: pointer; font-size: 14px; border-left: 3px solid transparent; }}
.sidebar .group-item:hover {{ background: #1e2130; }}
.sidebar .group-item.active {{ background: #1a2332; border-left-color: #4a9eff; color: #4a9eff; }}
.sidebar .group-item .count {{ float: right; color: #666; font-size: 12px; }}
.main {{ flex: 1; overflow-y: auto; padding: 24px; }}
.tabs {{ display: flex; gap: 4px; margin-bottom: 20px; }}
.tab {{ padding: 8px 16px; cursor: pointer; border-radius: 6px 6px 0 0; background: #1e2130; color: #888; font-size: 14px; border: 1px solid #2a2d3a; border-bottom: none; }}
.tab.active {{ background: #0f1117; color: #4a9eff; }}
.search-box {{ margin-bottom: 20px; }}
.search-box input {{ width: 100%; max-width: 500px; padding: 10px 14px; background: #1e2130; border: 1px solid #2a2d3a; border-radius: 6px; color: #e0e0e0; font-size: 15px; outline: none; }}
.search-box input:focus {{ border-color: #4a9eff; }}
.group-title {{ font-size: 18px; color: #fff; margin-bottom: 16px; }}
.group-title .count {{ color: #888; font-size: 14px; font-weight: normal; }}
.kanji-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 12px; }}
.kanji-card {{ background: #161923; border: 1px solid #2a2d3a; border-radius: 8px; padding: 16px; transition: border-color 0.2s; }}
.kanji-card:hover {{ border-color: #4a9eff; }}
.kanji-card .char {{ font-size: 42px; text-align: center; margin-bottom: 8px; color: #fff; }}
.kanji-card .keyword {{ text-align: center; font-size: 15px; color: #4a9eff; margin-bottom: 12px; }}
.kanji-card .details {{ font-size: 13px; color: #aaa; line-height: 1.8; }}
.kanji-card .details span.label {{ color: #666; }}
.search-result {{ padding: 10px 14px; background: #161923; border: 1px solid #2a2d3a; border-radius: 6px; margin-bottom: 8px; display: flex; align-items: center; gap: 16px; }}
.search-result .sr-char {{ font-size: 28px; color: #fff; min-width: 40px; text-align: center; }}
.search-result .sr-info {{ font-size: 14px; }}
.search-result .sr-info .sr-keyword {{ color: #4a9eff; }}
.search-result .sr-info .sr-meta {{ color: #888; font-size: 12px; }}
.empty {{ color: #666; padding: 40px; text-align: center; }}
</style>
</head>
<body>
<div class="header">
  <h1>\u6f22 {title_esc}</h1>
  <div class="stats">{len(groups)} groups &middot; {total_kanji} kanji &middot; Generated from {escape(filename)}</div>
</div>
<div class="container">
  <div class="sidebar">
    <input type="text" id="groupFilter" placeholder="Filter groups..." oninput="filterGroups()">
    <div id="groupList"></div>
  </div>
  <div class="main">
    <div class="tabs">
      <div class="tab active" onclick="switchTab('groups')">Groups</div>
      <div class="tab" onclick="switchTab('search')">Search</div>
    </div>
    <div id="groupsTab">
      <div id="groupContent"><div class="empty">Select a group from the sidebar</div></div>
    </div>
    <div id="searchTab" style="display:none">
      <div class="search-box"><input type="text" id="searchInput" placeholder="Search by kanji, keyword, or on'yomi..." oninput="doSearch()"></div>
      <div id="searchResults"><div class="empty">Type to search</div></div>
    </div>
  </div>
</div>
<script>
const DATA = {groups_json};
const groupNames = Object.keys(DATA);
let activeGroup = null;

function renderSidebar(filter) {{
  const list = document.getElementById('groupList');
  const f = (filter || '').toLowerCase();
  list.innerHTML = groupNames
    .filter(g => !f || g.toLowerCase().includes(f))
    .map(g => `<div class="group-item ${{g === activeGroup ? 'active' : ''}}" onclick="selectGroup('${{g.replace(/'/g, "\\\\'")}}')">
      ${{esc(g)}} <span class="count">${{DATA[g].length}}</span></div>`).join('');
}}

function selectGroup(name) {{
  activeGroup = name;
  renderSidebar(document.getElementById('groupFilter').value);
  const kanji = DATA[name];
  if (!kanji || kanji.length === 0) {{
    document.getElementById('groupContent').innerHTML = '<div class="empty">Empty group</div>';
    return;
  }}
  let html = `<div class="group-title">${{esc(name)}} <span class="count">(${{kanji.length}} kanji)</span></div><div class="kanji-grid">`;
  kanji.forEach(k => {{
    html += `<div class="kanji-card">
      <div class="char">${{esc(k.char)}}</div>
      <div class="keyword">${{esc(k.keyword)}}</div>
      <div class="details">
        <span class="label">On:</span> ${{esc(k.on_reading)}}<br>
        <span class="label">Kun:</span> ${{esc(k.kun_reading)}}<br>
        <span class="label">Components:</span> ${{esc(k.components)}}<br>
        <span class="label">SRL:</span> ${{k.srl}} &middot;
        <span class="label">Type:</span> ${{esc(k.type)}} &middot;
        <span class="label">Freq:</span> ${{k.freq}}
        ${{k.ref !== k.char ? '<br><span class="label">Ref:</span> ' + esc(k.ref) : ''}}
      </div>
    </div>`;
  }});
  html += '</div>';
  document.getElementById('groupContent').innerHTML = html;
}}

function filterGroups() {{
  renderSidebar(document.getElementById('groupFilter').value);
}}

function switchTab(tab) {{
  document.querySelectorAll('.tab').forEach((t, i) => {{
    t.classList.toggle('active', (tab === 'groups' && i === 0) || (tab === 'search' && i === 1));
  }});
  document.getElementById('groupsTab').style.display = tab === 'groups' ? '' : 'none';
  document.getElementById('searchTab').style.display = tab === 'search' ? '' : 'none';
  if (tab === 'search') document.getElementById('searchInput').focus();
}}

function doSearch() {{
  const q = document.getElementById('searchInput').value.trim().toLowerCase();
  const el = document.getElementById('searchResults');
  if (!q) {{ el.innerHTML = '<div class="empty">Type to search</div>'; return; }}
  let results = [];
  groupNames.forEach(g => {{
    DATA[g].forEach(k => {{
      if (k.char === q || k.keyword.toLowerCase().includes(q) || k.on_reading.includes(q)) {{
        results.push({{ ...k, groupName: g }});
      }}
    }});
  }});
  if (results.length === 0) {{ el.innerHTML = '<div class="empty">No results</div>'; return; }}
  el.innerHTML = results.slice(0, 200).map(k =>
    `<div class="search-result">
      <div class="sr-char">${{esc(k.char)}}</div>
      <div class="sr-info">
        <span class="sr-keyword">${{esc(k.keyword)}}</span> &middot; On: ${{esc(k.on_reading)}}
        <div class="sr-meta">Group: ${{esc(k.groupName)}} &middot; SRL: ${{k.srl}} &middot; Freq: ${{k.freq}}</div>
      </div>
    </div>`
  ).join('') + (results.length > 200 ? `<div class="empty">${{results.length - 200}} more results...</div>` : '');
}}

function esc(s) {{ const d = document.createElement('div'); d.textContent = s || ''; return d.innerHTML; }}

renderSidebar();
if (groupNames.length > 0) selectGroup(groupNames[0]);
</script>
</body>
</html>"""


def main():
    docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
    os.makedirs(docs_dir, exist_ok=True)

    excel_dir = os.path.join(os.path.dirname(__file__), "..", "excel")

    files = [
        ("1500 KANJI COMPONENTS - ver. 1.3.xlsx", "Kanji MBO — 1500 Kanji"),
        ("2250 KANJI COMPONENTS - ver. 1.0.xlsx", "Kanji MBO — 2250 Kanji"),
    ]

    generated = []
    for filename, title in files:
        filepath = os.path.join(excel_dir, filename)
        if not os.path.exists(filepath):
            print(f"Skipping {filename} (not found)")
            continue

        print(f"Processing {filename}...")
        categorization, source = algorithm.run_pipeline(filepath)
        groups = build_groups_data(categorization)

        safe_name = filename.replace(" ", "_").replace(".", "_").replace("-", "_").lower()
        html_name = safe_name.rsplit("_xlsx", 1)[0] + ".html"
        html_path = os.path.join(docs_dir, html_name)

        html = generate_html(groups, title, filename)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)

        total = sum(len(v) for v in groups.values())
        print(f"  -> {html_name} ({len(groups)} groups, {total} kanji)")
        generated.append((html_name, title, len(groups), total))

    # Generate index page
    index_html = generate_index(generated)
    index_path = os.path.join(docs_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_html)
    print(f"  -> index.html")
    print("Done!")


def generate_index(pages):
    links = ""
    for html_name, title, num_groups, num_kanji in pages:
        links += f"""
        <a href="{html_name}" class="card">
          <div class="card-title">{escape(title)}</div>
          <div class="card-stats">{num_groups} groups &middot; {num_kanji} kanji</div>
        </a>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Kanji MBO</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f1117; color: #e0e0e0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }}
.page {{ text-align: center; padding: 40px; }}
h1 {{ font-size: 48px; margin-bottom: 8px; color: #fff; }}
.subtitle {{ color: #888; margin-bottom: 40px; font-size: 16px; }}
.cards {{ display: flex; gap: 20px; flex-wrap: wrap; justify-content: center; }}
.card {{ display: block; background: #161923; border: 1px solid #2a2d3a; border-radius: 12px; padding: 32px 40px; text-decoration: none; color: inherit; transition: border-color 0.2s, transform 0.2s; }}
.card:hover {{ border-color: #4a9eff; transform: translateY(-2px); }}
.card-title {{ font-size: 18px; color: #4a9eff; margin-bottom: 8px; }}
.card-stats {{ font-size: 14px; color: #888; }}
</style>
</head>
<body>
<div class="page">
  <h1>\u6f22 Kanji MBO</h1>
  <p class="subtitle">Kanji categorization by meaning, reading, and component similarity</p>
  <div class="cards">{links}
  </div>
</div>
</body>
</html>"""


if __name__ == "__main__":
    main()
