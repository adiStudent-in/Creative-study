# -*- coding: utf-8 -*-
"""
Build English chapter Notes.html pages from the paired markdown notes.

For each chapter folder English/Ch - N/ holding:
    English_ChN_Revision_Notes.md
    English_ChN_Summary_Notes.md
this script emits one self-contained page:
    English/Ch - N/Notes.html

Each page carries BOTH markdown files as two <section> layers (revision +
summary) toggled by buttons in the hero and in the sidebar. The design
mirrors the existing Science/Ch - 2/Notes.html house template but with the
English subject ('sage') accent so it matches the English index page.

Run:  python English/_build_html.py
"""
import os, re, json
import mistune

HERE = os.path.dirname(os.path.abspath(__file__))
md = mistune.create_markdown(plugins=['table', 'strikethrough'])

# ------------------------------------------------------------------ utils

def slugify(text, seen):
    base = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-') or 'sec'
    if base not in seen:
        seen.add(base)
        return base
    i = 2
    while f'{base}-{i}' in seen:
        i += 1
    s = f'{base}-{i}'
    seen.add(s)
    return s

def apply_heading_ids(html, prefix):
    seen = set()
    def repl(m):
        tag, inner = m.group(1), m.group(2)
        txt = re.sub(r'<[^>]+>', '', inner)
        txt = re.sub(r'&#x[0-9A-Fa-f]+;', '', txt)
        tid = slugify(prefix + '-' + txt, seen)
        return f'<h{tag} id="{tid}">{inner}</h{tag}>'
    return re.sub(r'<h([23])\b[^>]*>(.*?)</h\1>', repl, html, flags=re.S)

def wrap_tables(html):
    return re.sub(r'(<table>.*?</table>)', r'<div class="table-wrap">\1</div>', html, flags=re.S)

def split_front(text):
    lines = text.split('\n')
    h1 = sub = ''
    rest = []
    for line in lines:
        l = line.rstrip()
        if not h1 and l.startswith('# '):
            h1 = l[2:].strip()
        elif h1 and not sub and l.startswith('### '):
            sub = l[4:].strip()
        else:
            rest.append(line)
    body = '\n'.join(rest)
    body = re.sub(r'^\s*(---)[ \t]*\n+', '', body, count=1)
    return h1, sub, body

def render(text, prefix):
    h1, sub, body = split_front(text)
    html = md(body)
    html = apply_heading_ids(html, prefix)
    html = wrap_tables(html)
    return h1, sub, html

def toc_from(html):
    out = []
    for m in re.finditer(r'<h([23])\b[^>]*id="([^"]+)"[^>]*>(.*?)</h\1>', html, re.S):
        lvl = int(m.group(1)); tid = m.group(2)
        t = re.sub(r'<[^>]+>', '', m.group(3)).strip()
        out.append((lvl, tid, t))
    return out

# ---------------------------------------------------------------- metadata
CHAPTERS = {1: 'How I Taught My Grandmother to Read · Bharat Our Land',
             2: 'The Pot Maker · Gifts of Grace',
             3: 'Winds of Change · Canvas of Soil',
             4: 'Vitamin-M · I Cannot Remember My Mother'}

# ---------------------------------------------------------------- template
CSS = r"""
:root {
  --bg:#F6F4EC; --surface:#fff; --text:#23281F; --text-muted:#6E7267;
  --accent:#4E724B; --accent-light:#E9F0E5;
  --accent2:#B98A2F; --accent2-light:#FAF3E0;
  --sidebar-bg:#26311F; --sidebar-text:#C7CDBE;
  --border:#E2E0D8; --card-shadow:0 1px 3px rgba(0,0,0,.04),0 1px 2px rgba(0,0,0,.06);
  --radius:8px;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth;font-size:16px;overflow-x:hidden}
body{font-family:'Plus Jakarta Sans',system-ui,-apple-system,sans-serif;background:var(--bg);color:var(--text);line-height:1.75;-webkit-font-smoothing:antialiased;overflow-x:hidden;width:100%}
::selection{background:var(--accent);color:#fff}
.wrapper{display:flex;min-height:100vh;width:100%;max-width:100vw}

.sidebar{width:260px;flex-shrink:0;background:var(--sidebar-bg);color:var(--sidebar-text);padding:2rem 1.25rem;position:fixed;top:0;left:0;height:100vh;overflow-y:auto;display:flex;flex-direction:column;z-index:10}
.sidebar-logo{font-family:'DM Serif Display',serif;font-size:1.05rem;color:#fff;margin-bottom:1.5rem;letter-spacing:-.01em}
.sidebar-logo small{display:block;font-family:'Plus Jakarta Sans',sans-serif;font-size:.68rem;font-weight:400;color:var(--sidebar-text);margin-top:.15rem}
.sidebar-toggle-view{display:flex;background:rgba(255,255,255,.06);border:none;margin-bottom:1.2rem;border-radius:8px;padding:3px;gap:3px}
.sidebar-toggle-view button{flex:1;border:none;background:transparent;color:var(--sidebar-text);font-family:'Plus Jakarta Sans',sans-serif;font-size:.68rem;font-weight:600;letter-spacing:.04em;padding:.38rem .4rem;border-radius:6px;cursor:pointer;transition:.2s}
.sidebar-toggle-view button.active{background:#fff;color:var(--sidebar-bg)}
.sidebar nav{flex:1}
.sidebar nav a{display:block;color:var(--sidebar-text);text-decoration:none;font-size:.78rem;font-weight:500;padding:.38rem .6rem;margin-bottom:.1rem;border-radius:6px;transition:all .2s;line-height:1.4;border-left:2px solid transparent}
.sidebar nav a:hover{color:#fff;background:rgba(255,255,255,.06)}
.sidebar nav a.active{color:#fff;background:rgba(255,255,255,.1);font-weight:600;border-left-color:var(--accent)}
.sidebar nav a.indent{padding-left:1.35rem}
.sidebar .meta{font-size:.68rem;color:rgba(255,255,255,.32);border-top:1px solid rgba(255,255,255,.06);padding-top:.9rem;margin-top:auto}

.main{flex:1;min-width:0;width:1px}
.content{padding:2.4rem 3rem 4rem;max-width:820px;margin:0 auto}

.mode-toggle{display:inline-flex;background:var(--surface);border:1px solid var(--border);border-radius:999px;padding:4px;gap:4px;margin-bottom:1.6rem;position:sticky;top:1rem;z-index:20}
.mode-toggle button{border:none;background:transparent;font-family:'Plus Jakarta Sans',sans-serif;font-size:.75rem;font-weight:600;letter-spacing:.03em;color:var(--text-muted);padding:.5rem 1.15rem;border-radius:999px;cursor:pointer;transition:all .25s}
.mode-toggle button.active{background:var(--accent);color:#fff}
.mode-toggle button:not(.active):hover{color:var(--accent);background:var(--accent-light)}

.view-block{display:none}
.view-block.active{display:block}

h1{font-family:'DM Serif Display',serif;font-size:2.5rem;font-weight:400;line-height:1.2;letter-spacing:-.02em;margin-bottom:.3rem;color:var(--text)}
.subtitle{font-size:.84rem;color:var(--text-muted);margin-bottom:2.4rem;font-weight:400;border-bottom:1px solid var(--border);padding-bottom:1.4rem}
h2{font-family:'DM Serif Display',serif;font-size:1.55rem;font-weight:400;margin:2.5rem 0 1rem;letter-spacing:-.01em;line-height:1.3;color:var(--text);scroll-margin-top:2rem}
h3{font-family:'Plus Jakarta Sans',sans-serif;font-size:1rem;font-weight:700;margin:1.5rem 0 .5rem;color:var(--text)}
h4{font-family:'Plus Jakarta Sans',sans-serif;font-size:.88rem;font-weight:600;margin:1.2rem 0 .4rem;color:var(--text)}
p{margin-bottom:.75rem}
ul,ol{padding-left:1.25rem;margin-bottom:1rem}
li{margin-bottom:.25rem}
strong{font-weight:600;color:var(--text)}
em{font-style:italic}
code{font-family:'JetBrains Mono',Consolas,monospace;font-size:.85em;background:#F0EFE7;padding:.12em .35em;border-radius:4px}

.table-wrap{width:100%;overflow-x:auto;margin:1rem 0;border-radius:var(--radius);box-shadow:var(--card-shadow);-webkit-overflow-scrolling:touch}
table{width:100%;border-collapse:collapse;font-size:.85rem}
thead{background:var(--sidebar-bg);color:#fff}
th{padding:.55rem .75rem;text-align:left;font-weight:600;font-size:.74rem;letter-spacing:.03em;text-transform:uppercase;white-space:nowrap}
td{padding:.5rem .75rem;border-bottom:1px solid var(--border);overflow-wrap:break-word;word-break:break-word}
tbody tr:last-child td{border-bottom:none}
tbody tr:nth-child(even){background:rgba(0,0,0,.015)}
tbody tr:hover{background:rgba(78,114,75,.05)}
@media(max-width:600px){th,td{padding:.4rem .5rem;font-size:.8rem}th{white-space:normal;font-size:.7rem}}

blockquote{margin:1.25rem 0;padding:1rem 1.25rem;border-radius:var(--radius);font-size:.88rem;line-height:1.65;background:var(--accent2-light);border-left:3px solid var(--accent2)}
blockquote strong:first-child{color:var(--accent2)}

hr{border:none;height:1px;background:var(--border);margin:2rem 0}

.fade-in{opacity:0;transform:translateY(12px);transition:opacity .5s ease,transform .5s ease}
.fade-in.visible{opacity:1;transform:translateY(0)}

.sidebar-toggle{display:none;position:fixed;top:1rem;left:1rem;z-index:100;width:2.5rem;height:2.5rem;border:none;border-radius:8px;background:var(--sidebar-bg);color:#fff;font-size:1.2rem;cursor:pointer}

@media(max-width:900px){
  .sidebar{position:fixed;left:-280px;transition:left .3s ease;z-index:99;height:100dvh}
  .sidebar.open{left:0}
  .sidebar-toggle{display:block}
  .main{max-width:100%}
  .content{padding:2rem 1.4rem}
  h1{font-size:2rem}
  h2{font-size:1.4rem}
}
@media(max-width:600px){
  .content{padding:1.4rem 1rem}
  h1{font-size:1.6rem}
  h2{font-size:1.2rem;margin:2rem 0 .75rem}
  h3{font-size:.9rem}
  ul,ol{padding-left:1rem}
  blockquote{padding:.75rem 1rem;font-size:.83rem}
  .mode-toggle{position:static}
}
@media print{
  .sidebar,.sidebar-toggle,.mode-toggle{display:none}
  .content{max-width:100%;padding:1rem}
  .fade-in{opacity:1;transform:none}
  .view-block{display:block!important}
}
"""

JS = r"""
(function(){
  const revBtn = document.getElementById('revBtn');
  const sumBtn = document.getElementById('sumBtn');
  const srevBtn = document.getElementById('srevBtn');
  const ssumBtn = document.getElementById('ssumBtn');
  const rev = document.getElementById('view-rev');
  const sum = document.getElementById('view-sum');
  const toc = document.getElementById('toc');

  const TOC = { rev: __TOC_REV__, sum: __TOC_SUM__ };
  const topButtons = [revBtn, sumBtn];
  const sideButtons = [srevBtn, ssumBtn];
  let current = 'rev';

  function buildToc(view){
    const items = TOC[view];
    if(!items){ toc.innerHTML = ''; return; }
    toc.innerHTML = items.map(function(a){
      return '<a href="#' + a.h + '" data-h>' + a.t + '</a>';
    }).join('\n');
    attachSpy(items);
  }

  let spyItems = [];
  function attachSpy(items){
    spyItems = items;
    const els = items.map(a => document.getElementById(a.h)).filter(Boolean);
    const links = toc.querySelectorAll('a[data-h]');
    function onScroll(){
      let cur = '';
      els.forEach(el => { if(window.scrollY >= el.offsetTop - 150) cur = el.id; });
      links.forEach(a => a.classList.toggle('active', a.getAttribute('href') === '#' + cur));
    }
    window.removeEventListener('scroll', onScroll);
    window.addEventListener('scroll', onScroll);
    onScroll();
  }

  function setView(view){
    if(view === current) return;
    current = view;
    rev.classList.toggle('active', view === 'rev');
    sum.classList.toggle('active', view === 'sum');
    topButtons.forEach(b => b.classList.toggle('active', b.dataset.view === view));
    sideButtons.forEach(b => b.classList.toggle('active', b.dataset.view === view));
    buildToc(view);
    document.getElementById('sidebar').classList.remove('open');
  }

  topButtons.forEach(b => b.addEventListener('click', () => setView(b.dataset.view)));
  sideButtons.forEach(b => b.addEventListener('click', () => setView(b.dataset.view)));

  document.getElementById('menuToggle').addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('open');
  });
  toc.addEventListener('click', e => {
    if(e.target.matches('a[data-h]')) document.getElementById('sidebar').classList.remove('open');
  });

  const io = new IntersectionObserver(es => {
    es.forEach(x => { if(x.isIntersecting){ x.target.classList.add('visible'); io.unobserve(x.target); } });
  }, { threshold: 0.08, rootMargin: '0px 0px -60px 0px' });
  document.querySelectorAll('.fade-in').forEach(el => io.observe(el));

  buildToc('rev');
})();
"""

def build_page(chapter):
    folder = os.path.join(HERE, f'Ch - {chapter}')
    rev_f = os.path.join(folder, f'English_Ch{chapter}_Revision_Notes.md')
    sum_f = os.path.join(folder, f'English_Ch{chapter}_Summary_Notes.md')
    rev_h1, rev_sub, rev_html = render(open(rev_f, encoding='utf-8').read(), 'rev')
    sum_h1, sum_sub, sum_html = render(open(sum_f, encoding='utf-8').read(), 'sum')

    rev_toc = [{'h': tid, 't': t} for lvl, tid, t in toc_from(rev_html) if lvl == 2]
    sum_toc = [{'h': tid, 't': t} for lvl, tid, t in toc_from(sum_html) if lvl == 2]

    # e.g. "English — Chapter 1: Revision Notes" (with 🚀 emoji removed)
    page_title = rev_h1.replace('📘', '').replace('🗂️', '').strip()
    page_title = re.sub(r'(?:\s*❌\s*)+', '', page_title).strip()
    page_title = re.sub(r'\s*Revision Notes\s*$', '', page_title).strip().rstrip(':').strip() or f'Chapter {chapter}'

    js = JS.replace('__TOC_REV__', json.dumps(rev_toc, ensure_ascii=False)) \
           .replace('__TOC_SUM__', json.dumps(sum_toc, ensure_ascii=False))

    page = TPL.format(
        title=page_title,
        chapter=chapter,
        subtitle_rev=rev_sub,
        subtitle_sum=sum_sub,
        rev_html=rev_html,
        sum_html=sum_html,
    )
    page = page.replace('__CSS__', CSS).replace('__JS__', js)
    return page

TPL = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
<style>__CSS__</style>
</head>
<body>

<button class="sidebar-toggle" id="menuToggle" aria-label="Toggle navigation">&#9776;</button>

<div class="wrapper">

<aside class="sidebar" id="sidebar">
  <div class="sidebar-logo">
    Class 9 English
    <small>Chapter {chapter} &middot; Revision &amp; Summary</small>
  </div>
  <div class="sidebar-toggle-view" role="tablist" aria-label="Notes view">
    <button id="srevBtn" class="active" data-view="rev">Revision</button>
    <button id="ssumBtn" data-view="sum">Summary</button>
  </div>
  <nav id="toc"></nav>
  <div class="meta">English &middot; Chapter {chapter} &middot; CBSE Class 9</div>
</aside>

<main class="main">
  <div class="content">

    <div class="mode-toggle" role="tablist" aria-label="Notes view">
      <button id="revBtn" class="active" data-view="rev">Revision Notes</button>
      <button id="sumBtn" data-view="sum">Summary</button>
    </div>

    <div class="view-block active" id="view-rev" data-block="rev">
      <h1 class="fade-in">{title}</h1>
      <p class="subtitle fade-in">{subtitle_rev}</p>
      {rev_html}
    </div>

    <div class="view-block" id="view-sum" data-block="sum">
      <h1 class="fade-in">{title}</h1>
      <p class="subtitle fade-in">{subtitle_sum}</p>
      {sum_html}
    </div>

  </div>
</main>

</div>

<script>__JS__</script>

</body>
</html>
"""

def main():
    for n in CHAPTERS:
        page = build_page(n)
        out = os.path.join(HERE, f'Ch - {n}', 'Notes.html')
        with open(out, 'w', encoding='utf-8') as f:
            f.write(page)
        print(f'wrote {out}  ({len(page)} bytes)')

if __name__ == '__main__':
    main()
