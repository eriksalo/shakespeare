"""Render THE-HUMAN-CONDITION.md as a dark, whitepaper-style single page.

Layout: hero (eyebrow, display title, subtitle, buttons, meta strip), then a two-column
body with a sticky table of contents on the left and one content card on the right.
Each ## heading becomes a numbered section; ### headings are sub-sections inside it.
"""
import re, sys, html, markdown

src, out = sys.argv[1], sys.argv[2]
md = open(src, encoding='utf-8').read()
lines = md.split('\n')
title = lines[0].lstrip('# ').strip()
rest = '\n'.join(lines[1:])
m = re.search(r'^\*(.+?)\*\s*$', rest, re.M)
preface = m.group(1) if m else ''
rest = rest.replace(m.group(0), '', 1) if m else rest
rest = re.sub(r'^---\s*$', '', rest, flags=re.M)

REPO = 'https://github.com/eriksalo/shakespeare'
preface = (preface
           .replace('`corpus/works/`', f'[the corpus]({REPO}/tree/main/corpus/works)')
           .replace('the per-play notes in `notes/`', f'[the per-play notes]({REPO}/tree/main/notes)'))
rest = rest.replace('`notes/`', f'[`notes/`]({REPO}/tree/main/notes)')

words = len(re.findall(r"\w+", rest))
minutes = max(1, round(words / 230))

def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', re.sub(r'[*`]', '', s).lower()).strip('-')[:60]

# Split the markdown into ## sections so each can be wrapped and numbered.
parts = re.split(r'^(## .+)$', rest, flags=re.M)
sections = []  # (title, slug, body_md)
for i in range(1, len(parts), 2):
    t = parts[i][3:].strip()
    sections.append((t, slug(t), parts[i + 1]))

ext = ['extra', 'sane_lists', 'smarty']
sec_html = []
toc_html = []
for n, (t, s, body_md) in enumerate(sections, 1):
    body = markdown.markdown(body_md, extensions=ext)
    # Give ### headings ids and a styled number if they start with "N."
    def h3(mo):
        text = mo.group(1)
        plain = re.sub(r'<[^>]+>', '', text)
        sid = slug(plain)
        num = re.match(r'\s*(\d+)\.\s*(.*)', text, re.S)
        if num:
            return f'<h3 id="{sid}"><span class="n">{num.group(1)}</span>{num.group(2)}</h3>'
        return f'<h3 id="{sid}">{text}</h3>'
    body = re.sub(r'<h3>(.*?)</h3>', h3, body, flags=re.S)
    subs = re.findall(r'<h3 id="([^"]+)">(?:<span class="n">(\d+)</span>)?(.*?)</h3>', body, re.S)
    sub_toc = ''.join(
        f'<li><a href="#{sid}">{(sn + ". ") if sn else ""}{html.escape(re.sub(r"<[^>]+>", "", st))}</a></li>'
        for sid, sn, st in subs)
    toc_html.append(
        f'<li class="sec" data-for="{s}"><a href="#{s}"><span class="num">{n:02d}</span>{html.escape(t)}</a>'
        + (f'<ul class="subs">{sub_toc}</ul>' if sub_toc else '') + '</li>')
    sec_html.append(
        f'<section id="{s}" class="sec"><div class="sec-head"><span class="badge">{n:02d}</span>'
        f'<h2>{html.escape(t)}</h2></div>{body}</section>')

pre_html = markdown.markdown(preface, extensions=ext)

css = """
:root{
  --bg:#0a0d14;--bg2:#0e1420;--card:#111827;--card2:#0f172a;--line:#1f2937;--line2:#273244;
  --fg:#e6e9ef;--fg2:#c3cad6;--muted:#8b97a4;--amber:#e79f23;--amber2:#f2a133;--amber-soft:rgba(231,159,35,.12);
  --display:"Red Hat Display",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --body:"Red Hat Text",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --maxw:1280px;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--body);font-size:17px;line-height:1.65}
a{color:var(--amber2);text-decoration:none}
a:hover{text-decoration:underline}
.wrap{max-width:var(--maxw);margin:0 auto;padding:0 32px}

/* top bar */
.topbar{border-bottom:1px solid var(--line);background:rgba(10,13,20,.85);backdrop-filter:blur(8px);position:sticky;top:0;z-index:20}
.topbar .wrap{display:flex;align-items:center;justify-content:space-between;height:64px}
.brand{font-family:var(--display);font-weight:700;letter-spacing:.12em;font-size:15px;color:var(--fg)}
.brand small{display:block;font-weight:500;letter-spacing:.22em;font-size:9px;color:var(--amber);margin-top:2px}
.topbar nav a{color:var(--fg2);font-size:14px;margin-left:22px}
.topbar nav a.btn{margin-left:18px}

/* hero */
.hero{background:radial-gradient(900px 400px at 15% 0%,#15213a 0%,rgba(21,33,58,0) 70%),linear-gradient(180deg,#0b1220 0%,var(--bg) 100%);border-bottom:1px solid var(--line);padding:64px 0 48px}
.eyebrow{font-family:var(--body);font-size:12px;letter-spacing:.32em;text-transform:uppercase;color:var(--fg2);margin:0 0 22px}
.hero h1{font-family:var(--display);font-weight:800;text-transform:uppercase;letter-spacing:.02em;font-size:clamp(34px,5.2vw,68px);line-height:1.05;margin:0 0 18px;color:#fff}
.hero .sub{font-size:clamp(17px,1.6vw,22px);color:var(--fg2);margin:0 0 30px;max-width:900px}
.hero .sub a{color:var(--amber2)}
.btns{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:28px}
.btn{display:inline-block;padding:12px 24px;border-radius:999px;font-weight:600;font-size:15px;border:1px solid var(--line2);color:var(--fg);background:transparent}
.btn:hover{text-decoration:none;border-color:#3b475c;background:#131b2a}
.btn.primary{background:var(--amber);border-color:var(--amber);color:#1a1200}
.btn.primary:hover{background:var(--amber2)}
.meta{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:24px;background:var(--card2);border:1px solid var(--line);border-radius:14px;padding:22px 24px}
.meta div span{display:block;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-bottom:6px}
.meta div b{font-weight:500;color:var(--fg2)}

/* two-column body */
.body{display:grid;grid-template-columns:320px minmax(0,1fr);gap:40px;padding:56px 0 96px;align-items:start}
.toc{position:sticky;top:88px;background:var(--card);border:1px solid var(--line);border-radius:16px;padding:22px 20px;max-height:calc(100vh - 110px);overflow:auto}
.toc h4{font-family:var(--display);font-weight:600;font-size:19px;margin:0 0 14px;color:#fff}
.toc ul{list-style:none;margin:0;padding:0}
.toc li.sec>a{display:block;padding:10px 12px;border-radius:8px;color:var(--fg2);font-size:15px;line-height:1.35;border-left:2px solid transparent}
.toc li.sec>a .num{display:none}
.toc li.sec.active>a{background:var(--amber-soft);color:var(--amber2);border-left-color:var(--amber)}
.toc li.sec>a:hover{text-decoration:none;background:#151d2c}
.toc ul.subs{display:none;margin:2px 0 8px 14px;border-left:1px solid var(--line2)}
.toc li.sec.active ul.subs{display:block}
.toc ul.subs a{display:block;padding:5px 12px;font-size:13px;line-height:1.35;color:var(--muted)}
.toc ul.subs a:hover,.toc ul.subs a.active{color:var(--fg);text-decoration:none}

.card{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:40px 44px}
section.sec{padding:8px 0 40px}
section.sec+section.sec{padding-top:40px}
.sec-head{display:flex;align-items:center;gap:18px;border-bottom:1px solid var(--line2);padding-bottom:16px;margin-bottom:26px}
.badge{flex:0 0 auto;width:54px;height:54px;border-radius:12px;border:1px solid var(--line2);background:#0b111c;color:var(--amber);font-family:var(--display);font-weight:700;font-size:15px;display:grid;place-items:center}
.sec h2{font-family:var(--display);font-weight:600;font-size:clamp(26px,2.6vw,36px);line-height:1.15;margin:0;color:#fff}
.sec h3{font-family:var(--display);font-weight:600;font-size:21px;line-height:1.3;margin:38px 0 12px;color:#fff;scroll-margin-top:96px;display:flex;gap:14px;align-items:baseline}
.sec h3 .n{flex:0 0 auto;color:var(--amber);font-size:14px;font-weight:700;letter-spacing:.04em;min-width:1.6em}
.sec h3+p{margin-top:0}
.sec p{margin:0 0 1.1em;color:var(--fg2);font-size:17px}
.sec p strong{color:var(--fg);font-weight:600}
.sec em{font-style:italic}
.sec code{font-family:inherit;font-size:inherit;background:none;padding:0;color:inherit}
.sec ul,.sec ol{margin:.2em 0 1.2em 1.25em;padding:0;color:var(--fg2)}
.sec li{margin-bottom:.6em}
section.sec{scroll-margin-top:84px}

footer{border-top:1px solid var(--line);color:var(--muted);font-size:14px;padding:28px 0 48px}
footer .wrap{display:flex;flex-wrap:wrap;gap:12px 32px;justify-content:space-between}

@media (max-width:980px){
  .body{grid-template-columns:1fr;gap:24px;padding-top:32px}
  .toc{position:static;max-height:none}
  .toc ul.subs{display:none !important}
  .card{padding:26px 22px}
  .topbar nav a:not(.btn){display:none}
}
@media (max-width:600px){
  .wrap{padding:0 16px}
  .hero{padding:40px 0 32px}
  .meta{grid-template-columns:1fr;gap:16px}
  .sec-head{gap:12px}.badge{width:44px;height:44px;border-radius:10px}
  .sec h3{font-size:19px}
  body{font-size:16px}.sec p{font-size:16px}
}
"""

js = """
(function(){
  var secs=[].slice.call(document.querySelectorAll('section.sec'));
  var items={};[].slice.call(document.querySelectorAll('.toc li.sec')).forEach(function(li){items[li.dataset.for]=li});
  var subs={};[].slice.call(document.querySelectorAll('.toc ul.subs a')).forEach(function(a){subs[a.getAttribute('href').slice(1)]=a});
  var h3s=[].slice.call(document.querySelectorAll('section.sec h3[id]'));
  function update(){
    var y=window.scrollY+120, cur=secs[0], curh3=null;
    secs.forEach(function(s){if(s.offsetTop<=y)cur=s});
    h3s.forEach(function(h){if(h.offsetTop<=y)curh3=h});
    Object.keys(items).forEach(function(k){items[k].classList.toggle('active',cur&&cur.id===k)});
    Object.keys(subs).forEach(function(k){subs[k].classList.toggle('active',!!curh3&&curh3.id===k&&cur.contains(curh3))});
  }
  window.addEventListener('scroll',update,{passive:true});window.addEventListener('resize',update);update();
})();
"""

doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="A reading of the whole of Shakespeare, from the text alone, for what it observes about being human.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Red+Hat+Display:wght@500;600;700;800&family=Red+Hat+Text:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<style>{css}</style></head><body>
<div class="topbar"><div class="wrap">
  <a class="brand" href="#">BARD<small>SALO · CLOUD</small></a>
  <nav><a href="#{sections[0][1]}">Read</a><a href="{REPO}/tree/main/notes">Notes</a><a href="{REPO}/tree/main/corpus/works">Corpus</a><a class="btn primary" href="THE-HUMAN-CONDITION.pdf">Download PDF</a></nav>
</div></div>

<header class="hero"><div class="wrap">
  <p class="eyebrow">Essay · October 2026</p>
  <h1>{html.escape(title)}</h1>
  <div class="sub">{pre_html}</div>
  <div class="btns"><a class="btn primary" href="THE-HUMAN-CONDITION.pdf">Download PDF</a><a class="btn" href="{REPO}/tree/main/notes">Per-play notes</a><a class="btn" href="{REPO}">Source on GitHub</a></div>
  <div class="meta">
    <div><span>Reading time</span><b>{minutes} minute read</b></div>
    <div><span>Works read</span><b>All 44 plays and poems, in full</b></div>
    <div><span>Method</span><b>Text only · no outside criticism · act and scene cited</b></div>
    <div><span>Primary themes</span><b>Knowing vs. doing · Seeming vs. being · Time</b></div>
  </div>
</div></header>

<div class="wrap body">
  <aside class="toc"><h4>Table of Contents</h4><ul>{''.join(toc_html)}</ul></aside>
  <main class="card">{''.join(sec_html)}</main>
</div>

<footer><div class="wrap"><span>Read from the Project Gutenberg Complete Works (ebook #100). Every claim traces to lines in the plays.</span><span><a href="{REPO}">eriksalo/shakespeare</a></span></div></footer>
<script>{js}</script>
</body></html>"""
open(out, 'w', encoding='utf-8').write(doc)
print("web html written", len(doc), "words", words, "minutes", minutes)
