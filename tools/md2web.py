import re, sys, markdown, html
src, out = sys.argv[1], sys.argv[2]
md = open(src, encoding='utf-8').read()
lines = md.split('\n')
title = lines[0].lstrip('# ').strip()
rest = '\n'.join(lines[1:])
m = re.search(r'^\*(.+?)\*\s*$', rest, re.M)
preface = m.group(1) if m else ''
rest = rest.replace(m.group(0), '', 1) if m else rest
rest = re.sub(r'^---\s*$', '', rest, flags=re.M)
# Make repo paths into links
preface = preface.replace('`corpus/works/`', '[the corpus](https://github.com/eriksalo/shakespeare/tree/main/corpus/works)').replace('the per-play notes in `notes/`', '[the per-play notes](https://github.com/eriksalo/shakespeare/tree/main/notes)')
rest = rest.replace('`notes/`', '[`notes/`](https://github.com/eriksalo/shakespeare/tree/main/notes)')

def slug(s): return re.sub(r'[^a-z0-9]+','-',re.sub(r'[*`]','',s).lower()).strip('-')[:60]
body = markdown.markdown(rest, extensions=['extra','sane_lists','smarty','toc'], extension_configs={'toc':{'slugify':lambda v,sep: slug(v),'anchorlink':False}})
pre = markdown.markdown(preface, extensions=['extra','smarty'])
toc=[]
for lvl, text in re.findall(r'^(##|###) (.+)$', rest, re.M):
    t=re.sub(r'[*`]','',text).strip(); toc.append((lvl,t,slug(t)))
toc_html=''.join(f'<li class="{"part" if l=="##" else "obs"}"><a href="#{s}">{html.escape(t)}</a></li>' for l,t,s in toc)

css = """
:root{--bg:#fbfaf7;--fg:#1c1b19;--muted:#6b675f;--rule:#e2ded5;--accent:#7a3b2e;--maxw:38rem}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#15161a;--fg:#e8e4dc;--muted:#9a958b;--rule:#2b2d33;--accent:#d98b6e}}
:root[data-theme=dark]{--bg:#15161a;--fg:#e8e4dc;--muted:#9a958b;--rule:#2b2d33;--accent:#d98b6e}
*{box-sizing:border-box}
html{font-size:clamp(17px,1.05vw + 12px,20px);-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font-family:"Iowan Old Style","Palatino Linotype","Book Antiqua",Palatino,Georgia,"Liberation Serif",serif;line-height:1.6}
main{max-width:var(--maxw);margin:0 auto;padding:0 16px 6rem}
header.title{padding:5rem 0 2.5rem;border-bottom:1px solid var(--rule);margin-bottom:2.5rem}
header.title h1{font-weight:400;font-size:2.4rem;line-height:1.15;margin:0 0 1rem;letter-spacing:-.01em}
header.title .sub{color:var(--muted);font-style:italic;font-size:1.02rem}
header.title .meta{margin-top:1.6rem;font-size:.9rem;color:var(--muted)}
header.title .meta a{margin-right:1.2rem}
a{color:var(--accent);text-decoration:none;border-bottom:1px solid color-mix(in srgb,var(--accent) 35%,transparent)}
a:hover{border-bottom-color:var(--accent)}
nav.contents{border-bottom:1px solid var(--rule);padding-bottom:2rem;margin-bottom:3rem}
nav.contents h2{font-size:1.1rem;font-weight:400;text-transform:uppercase;letter-spacing:.12em;color:var(--muted);margin:0 0 1rem}
nav.contents ul{list-style:none;margin:0;padding:0}
nav.contents li.part{margin-top:.9rem;font-size:1.05rem}
nav.contents li.obs{margin:.25rem 0 0 1.2rem;font-size:.95rem;line-height:1.45;color:var(--fg)}
nav.contents li a{border:none;color:inherit}
nav.contents li a:hover{color:var(--accent)}
h2{font-weight:400;font-size:1.9rem;line-height:1.2;margin:4rem 0 1.4rem;scroll-margin-top:1.5rem}
h3{font-weight:400;font-size:1.28rem;line-height:1.35;margin:2.6rem 0 .7rem;scroll-margin-top:1.5rem}
h3+p{margin-top:0}
p{margin:0 0 1.05rem;hyphens:auto}
em{font-style:italic}
strong{font-weight:600}
code{font-family:inherit;font-size:inherit;background:none;padding:0}
ul,ol{margin:.2rem 0 1.2rem 1.3rem;padding:0}
li{margin-bottom:.55rem}
footer{max-width:var(--maxw);margin:0 auto;padding:2rem 16px 4rem;border-top:1px solid var(--rule);color:var(--muted);font-size:.9rem}
.top{position:fixed;right:1rem;bottom:1rem;font-size:.85rem;background:var(--bg);border:1px solid var(--rule);padding:.4rem .7rem;border-radius:999px;opacity:.85}
@media (max-width:600px){header.title{padding-top:3rem}header.title h1{font-size:1.9rem}h2{font-size:1.55rem;margin-top:3rem}.top{display:none}}
"""
doc=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="A reading of the whole of Shakespeare, from the text alone, for what it observes about being human.">
<style>{css}</style></head><body>
<main>
<header class="title"><h1>{html.escape(title)}</h1><div class="sub">{pre}</div>
<div class="meta"><a href="THE-HUMAN-CONDITION.pdf">Download as PDF</a><a href="https://github.com/eriksalo/shakespeare">Source, notes, and corpus on GitHub</a></div></header>
<nav class="contents"><h2>Contents</h2><ul>{toc_html}</ul></nav>
{body}
</main>
<footer>Read from the Project Gutenberg Complete Works (ebook #100). October 2026. No outside criticism was used; every claim traces to lines in the plays.</footer>
<a class="top" href="#">Top</a>
</body></html>"""
open(out,'w',encoding='utf-8').write(doc); print("web html written", len(doc))
