import re, sys, markdown, html
src, out = sys.argv[1], sys.argv[2]
md = open(src, encoding='utf-8').read()

# Pull title and the italic preface line off the top; drop horizontal rules (we page-break on Part headings instead)
lines = md.split('\n')
title = lines[0].lstrip('# ').strip()
rest = '\n'.join(lines[1:])
m = re.search(r'^\*(.+?)\*\s*$', rest, re.M)
preface = m.group(1) if m else ''
rest = rest.replace(m.group(0), '', 1) if m else rest
rest = re.sub(r'^---\s*$', '', rest, flags=re.M)

body = markdown.markdown(rest, extensions=['extra', 'sane_lists', 'smarty'])
pre = markdown.markdown(preface, extensions=['extra','smarty'])

# Contents: Parts and numbered observations
toc = []
for lvl, text in re.findall(r'^(##|###) (.+)$', rest, re.M):
    text = re.sub(r'[*`]', '', text).strip()
    toc.append((lvl, text))
toc_html = []
for lvl, text in toc:
    cls = 'part' if lvl == '##' else 'obs'
    toc_html.append(f'<li class="{cls}">{html.escape(text)}</li>')

css = """
@page { size: letter; margin: 1in 1.05in 1in 1.05in; }
html { font-size: 11.6pt; }
body { font-family: "Liberation Serif", "DejaVu Serif", Georgia, serif; line-height: 1.52; color: #111; margin: 0; }
p { margin: 0 0 0.75em 0; text-align: left; hyphens: auto; orphans: 3; widows: 3; }
h1, h2, h3 { font-family: "Liberation Serif", Georgia, serif; font-weight: normal; color: #111; page-break-after: avoid; }
h2 { font-size: 1.9rem; margin: 0 0 1.1em 0; padding-top: 0.2em; letter-spacing: 0.01em; }
h2.part { page-break-before: always; }
h3 { font-size: 1.22rem; margin: 1.6em 0 0.5em 0; line-height: 1.3; }
h3 + p { margin-top: 0; }
em { font-style: italic; }
strong { font-weight: bold; }
code { font-family: inherit; font-size: inherit; background: none; padding: 0; }
ul, ol { margin: 0.2em 0 0.9em 1.3em; padding: 0; }
li { margin: 0 0 0.45em 0; }
section.teaches p { margin-bottom: 0.95em; }
/* Title page */
.title { page-break-after: always; display: flex; flex-direction: column; justify-content: center; height: 8.4in; }
.title h1 { font-size: 2.6rem; line-height: 1.15; margin: 0 0 0.5em 0; }
.title .sub { font-size: 1.05rem; font-style: italic; color: #333; max-width: 5.6in; line-height: 1.5; }
.title .meta { margin-top: 2.8em; font-size: 0.95rem; color: #555; }
/* Contents */
.contents { page-break-after: always; }
.contents h2 { margin-bottom: 0.5em; }
.contents ul { list-style: none; margin: 0; }
.contents li.part { margin-top: 0.8em; font-size: 1.05rem; }
.contents li.obs { margin-left: 1.3em; font-size: 0.93rem; margin-bottom: 0.15em; line-height: 1.38; }
/* Pull-quote feel for the method section's first paragraph */
.lede { font-size: 1.04rem; }
"""

# Mark Part headings for page breaks
body = re.sub(r'<h2>(Part [^<]+)</h2>', r'<h2 class="part">\1</h2>', body)
body = re.sub(r'<h2>(Questions to argue with|Where to go next)</h2>', r'<h2 class="part">\1</h2>', body)

doc = f"""<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(title)}</title><style>{css}</style></head><body>
<div class="title">
  <h1>{html.escape(title)}</h1>
  <div class="sub">{pre}</div>
  <div class="meta">Read from the Project Gutenberg Complete Works. October 2026.</div>
</div>
<div class="contents"><h2>Contents</h2><ul>{''.join(toc_html)}</ul></div>
{body}
</body></html>"""
open(out, 'w', encoding='utf-8').write(doc)
print("html written", len(doc))
