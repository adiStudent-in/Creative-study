# -*- coding: utf-8 -*-
"""Build Science chapter Notes.html pages from Notes.md (house template, cf. Ch-4).

Usage: python Science/_build_science_html.py
Reads:  Science/Ch - {3,6,13}/Notes.md
Writes: Science/Ch - {3,6,13}/Notes.html
"""
import os, re
import mistune

HERE = os.path.dirname(os.path.abspath(__file__))
md = mistune.create_markdown(plugins=['table'])

CHAPTERS = {
    3:  dict(title='Tissues in Action', sub='Chapter 3',
              accent='#3A7D44', accent_light='#E8F3E8',
              sidebar_bg='#1A2E1A', sidebar_text='#C4D4C0',
              hover='rgba(58,125,68,0.03)'),
    6:  dict(title='How Forces Affect Motion', sub='Chapter 6',
              accent='#C44536', accent_light='#F5E6E3',
              sidebar_bg='#1B1B2F', sidebar_text='#D4D0C9',
              hover='rgba(196,69,54,0.03)'),
    13: dict(title='Earth as a System — Energy, Matter and Life', sub='Chapter 13',
              accent='#4E7696', accent_light='#E7EFF4',
              sidebar_bg='#1B2A3A', sidebar_text='#C9D4DC',
              hover='rgba(78,118,150,0.03)'),
}

CSS_TPL = r"""
:root {
  --bg: #FCFBF9;
  --surface: #FFFFFF;
  --text: #1B1B2F;
  --text-muted: #6B6B7B;
  --accent: __ACCENT__;
  --accent-light: __ACCENT_LIGHT__;
  --green: #2D6A4F;
  --green-light: #E8F3EE;
  --border: #E8E4DF;
  --sidebar-bg: __SIDEBAR_BG__;
  --sidebar-text: __SIDEBAR_TEXT__;
  --sidebar-active: #FFFFFF;
  --warm-highlight: #FDF6E3;
  --card-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06);
  --radius: 8px;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth;font-size:16px}
body{
  font-family:'Plus Jakarta Sans',system-ui,-apple-system,sans-serif;
  background:var(--bg);
  color:var(--text);
  line-height:1.75;
  -webkit-font-smoothing:antialiased;
}
::selection{background:var(--accent);color:#fff}

/* Layout */
.wrapper{display:flex;min-height:100vh}

/* Sidebar */
.sidebar{
  width:260px;flex-shrink:0;
  background:var(--sidebar-bg);
  color:var(--sidebar-text);
  padding:2rem 1.5rem;
  position:sticky;top:0;height:100vh;overflow-y:auto;
  display:flex;flex-direction:column;
  z-index:10;
}
.sidebar-logo{
  font-family:'DM Serif Display',serif;
  font-size:1.1rem;color:#fff;margin-bottom:2rem;
  letter-spacing:-0.01em;
}
.sidebar-logo small{
  display:block;
  font-family:'Plus Jakarta Sans',sans-serif;
  font-size:0.7rem;font-weight:400;
  color:var(--sidebar-text);margin-top:0.15rem;
  letter-spacing:0.02em;
}
.sidebar nav{flex:1}
.sidebar nav a{
  display:block;
  color:var(--sidebar-text);text-decoration:none;
  font-size:0.8rem;font-weight:500;
  padding:0.4rem 0.75rem;margin-bottom:0.15rem;
  border-radius:6px;
  transition:all 0.2s;
  line-height:1.4;
}
.sidebar nav a:hover{color:#fff;background:rgba(255,255,255,0.06)}
.sidebar nav a.active{color:#fff;background:rgba(255,255,255,0.1);font-weight:600}
.sidebar .meta{
  font-size:0.7rem;color:rgba(255,255,255,0.3);
  border-top:1px solid rgba(255,255,255,0.06);
  padding-top:1rem;margin-top:auto;
}

/* Main */
.main{flex:1;max-width:calc(100% - 260px)}
.content{padding:3rem 4rem 4rem;max-width:780px;margin:0 auto}

/* Headings */
h1{
  font-family:'DM Serif Display',serif;
  font-size:2.6rem;font-weight:400;
  line-height:1.2;letter-spacing:-0.02em;
  margin-bottom:0.25rem;color:var(--text);
}
.subtitle{
  font-size:0.85rem;color:var(--text-muted);
  margin-bottom:2.5rem;font-weight:400;
  border-bottom:1px solid var(--border);
  padding-bottom:1.5rem;
}
h2{
  font-family:'DM Serif Display',serif;
  font-size:1.6rem;font-weight:400;
  margin:2.5rem 0 1rem;letter-spacing:-0.01em;
  line-height:1.3;color:var(--text);
  scroll-margin-top:2rem;
}
h2 .num{color:var(--accent);margin-right:0.3rem}
h3{
  font-family:'Plus Jakarta Sans',sans-serif;
  font-size:1rem;font-weight:700;
  margin:1.5rem 0 0.5rem;letter-spacing:-0.01em;
  color:var(--text);
}
h4{
  font-family:'Plus Jakarta Sans',sans-serif;
  font-size:0.9rem;font-weight:600;
  margin:1.2rem 0 0.4rem;color:var(--text);
}

/* Paragraphs & lists */
p{margin-bottom:0.75rem}
ul,ol{padding-left:1.25rem;margin-bottom:1rem}
li{margin-bottom:0.25rem}
li > ul, li > ol{margin-bottom:0.25rem;margin-top:0.25rem}
strong{font-weight:600;color:var(--text)}
em{font-style:italic}
code{font-family:'JetBrains Mono',Consolas,monospace;font-size:0.85em;background:#F0EEE9;padding:0.12em 0.35em;border-radius:4px}
a{color:var(--accent)}

/* Tables */
table{
  width:100%;border-collapse:collapse;
  margin:1rem 0;font-size:0.875rem;
  border-radius:var(--radius);overflow:hidden;
  box-shadow:var(--card-shadow);
}
thead{background:var(--sidebar-bg);color:#fff}
th{padding:0.6rem 1rem;text-align:left;font-weight:600;font-size:0.8rem;letter-spacing:0.03em;text-transform:uppercase}
td{padding:0.55rem 1rem;border-bottom:1px solid var(--border)}
tbody tr:last-child td{border-bottom:none}
tbody tr:hover{background:__HOVER__}
tbody tr:nth-child(even){background:rgba(0,0,0,0.015)}

/* Blockquotes (Competency Questions & Notes) */
blockquote{
  margin:1.25rem 0;padding:1rem 1.25rem;
  border-radius:var(--radius);
  font-size:0.875rem;line-height:1.65;
}
blockquote:not(.history){
  background:var(--warm-highlight);
  border-left:3px solid var(--accent);
}
blockquote:not(.history) strong:first-child{color:var(--accent)}
blockquote.history{
  background:var(--green-light);
  border-left:3px solid var(--green);
}

/* Worked Example */
.worked-example{
  background:var(--surface);border:1px solid var(--border);
  border-radius:var(--radius);padding:1.25rem 1.5rem;
  margin:1rem 0;box-shadow:var(--card-shadow);
}
.worked-example .label{
  font-size:0.7rem;font-weight:700;text-transform:uppercase;
  letter-spacing:0.05em;color:var(--text-muted);margin-bottom:0.35rem;
}
.worked-example p{margin-bottom:0.35rem}
.worked-example p:last-child{margin-bottom:0}

/* Math display */
.math-display{
  margin:0.75rem 0;overflow-x:auto;
  text-align:center;
}

/* Alert / warning box */
.alert{
  background:#FFF8F0;border-left:3px solid #E6A817;
  padding:0.75rem 1rem;border-radius:var(--radius);
  font-size:0.85rem;margin:0.75rem 0;
}

/* Formula box */
.formula-box{
  background:var(--surface);border:1px solid var(--border);
  border-radius:var(--radius);padding:1.5rem;
  margin:1rem 0;box-shadow:var(--card-shadow);
}
.formula-grid{
  display:grid;grid-template-columns:1fr 1fr;
  gap:0.5rem 1.5rem;
}
.formula-grid .item{display:flex;align-items:baseline;gap:0.5rem}
.formula-grid .item .label{font-size:0.78rem;color:var(--text-muted);min-width:7rem;font-weight:500}
.formula-grid .item .formula{font-weight:600}

/* Animations */
.fade-in{opacity:0;transform:translateY(12px);transition:opacity 0.5s ease,transform 0.5s ease}
.fade-in.visible{opacity:1;transform:translateY(0)}

/* Section dividers */
.section-divider{border:none;border-top:1px solid var(--border);margin:1rem 0}

/* Mobile toggle */
.sidebar-toggle{display:none;position:fixed;top:1rem;left:1rem;z-index:100;
  width:2.5rem;height:2.5rem;border:none;border-radius:8px;
  background:var(--sidebar-bg);color:#fff;font-size:1.2rem;
  cursor:pointer;align-items:center;justify-content:center;
}

/* Responsive */
@media(max-width:900px){
  .sidebar{position:fixed;left:-280px;transition:left 0.3s ease;z-index:99}
  .sidebar.open{left:0}
  .sidebar-toggle{display:flex}
  .main{max-width:100%}
  .content{padding:3rem 1.5rem}
  .formula-grid{grid-template-columns:1fr}
  h1{font-size:2rem}
}

@media(max-width:480px){
  .content{padding:2rem 1rem}
  h1{font-size:1.7rem}
  h2{font-size:1.3rem}
}
"""

JS = r"""
// Sidebar toggle
document.getElementById('menuToggle').addEventListener('click', function(){
  document.getElementById('sidebar').classList.toggle('open');
});

// Close sidebar on link click (mobile)
document.querySelectorAll('.sidebar nav a').forEach(function(a){
  a.addEventListener('click', function(){
    document.getElementById('sidebar').classList.remove('open');
  });
});

// Intersection Observer for fade-in
var observer = new IntersectionObserver(function(entries){
  entries.forEach(function(e){
    if(e.isIntersecting){ e.target.classList.add('visible'); }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

document.querySelectorAll('.fade-in').forEach(function(el){ observer.observe(el); });

// Active section highlighting
var sections = document.querySelectorAll('section');
var links = document.querySelectorAll('.sidebar nav a');

window.addEventListener('scroll', function(){
  var current = '';
  sections.forEach(function(sec){
    var top = sec.offsetTop - 120;
    if(window.scrollY >= top) current = sec.getAttribute('id');
  });
  links.forEach(function(a){
    a.classList.toggle('active', a.getAttribute('href') === '#' + current);
  });
});

// Re-render KaTeX after page load
document.addEventListener('DOMContentLoaded', function(){
  if(window.renderMathInElement){
    renderMathInElement(document.body, {
      delimiters: [
        {left: '$$', right: '$$', display: true},
        {left: '$', right: '$', display: false}
      ]
    });
  }
});
"""

TPL = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__HEAD_TITLE__</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js" onload="renderMathInElement(document.body,{delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}]})"></script>
<style>__CSS__</style>
</head>
<body>

<button class="sidebar-toggle" id="menuToggle" aria-label="Toggle navigation">&#9776;</button>

<div class="wrapper">

<aside class="sidebar" id="sidebar">
  <div class="sidebar-logo">
    Class 9 Science
    <small>__CHAPTER_LABEL__</small>
  </div>
  <nav>
__SIDEBAR__
  </nav>
  <div class="meta">Revision Notes &middot; CBSE Class 9</div>
</aside>

<main class="main">
  <div class="content">

    <!-- Header -->
    <h1 class="fade-in">__H1__</h1>
    <p class="subtitle fade-in">__SUBTITLE__</p>

__BODY__

  </div>
</main>

</div>

<script>__JS__</script>

</body>
</html>
"""


def slugify(text, seen):
    base = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-') or 'sec'
    if base not in seen:
        seen.add(base)
        return base
    i = 2
    while '%s-%d' % (base, i) in seen:
        i += 1
    s = '%s-%d' % (base, i)
    seen.add(s)
    return s


def split_front(text):
    lines = text.split('\n')
    h1, rest, skipped_hr = '', [], False
    for line in lines:
        if not h1 and line.startswith('# '):
            h1 = line[2:].strip()
        elif h1 and not skipped_hr and line.strip() == '---':
            skipped_hr = True
        else:
            rest.append(line)
    return h1, '\n'.join(rest)


def build(ch):
    meta = CHAPTERS[ch]
    folder = os.path.join(HERE, 'Ch - %d' % ch)
    src = os.path.join(folder, 'Notes.md')
    text = open(src, encoding='utf-8').read()
    h1, body = split_front(text)
    html = md(body)

    # --- h2: ids + numbered spans -------------------------------------
    seen = set()
    toc = []

    def h2repl(m):
        inner = m.group(1)
        plain = re.sub(r'<[^>]+>', '', inner).strip()
        num, title = '', plain
        mnum = re.match(r'^(\d+)\.\s*(.*)$', plain)
        if mnum:
            num = mnum.group(1).zfill(2)
            title = mnum.group(2)
        sid = slugify(title, seen)
        toc.append((sid, title))
        if num:
            return '<h2 id="%s" class="fade-in"><span class="num">%s</span> %s</h2>' % (sid, num, inner.split('.', 1)[-1] if False else re.sub(r'^\d+\.\s*', '', inner))
        return '<h2 id="%s" class="fade-in"><span class="num">&#x1F4DA;</span> %s</h2>' % (sid, inner)

    html = re.sub(r'<h2>(.*?)</h2>', h2repl, html, flags=re.S)

    # --- wrap each h2 section in <section> ------------------------------
    parts = re.split(r'(<h2 id="[^"]+" class="fade-in">.*?</h2>)', html)
    out = [parts[0]]
    for i in range(1, len(parts), 2):
        head = parts[i]
        sid = re.search(r'id="([^"]+)"', head).group(1)
        chunk = parts[i + 1] if i + 1 < len(parts) else ''
        out.append('<section id="%s">\n%s\n%s\n</section>' % (sid, head, chunk))
    html = ''.join(out)

    # --- hr dividers ------------------------------------------------------
    html = re.sub(r'<hr\s*/?>', '<hr class="section-divider">', html)

    # --- math display paragraphs ------------------------------------------
    html = re.sub(r'<p>\s*\$\$(.*?)\$\$\s*</p>',
                  r'<div class="math-display fade-in">$$\1$$</div>', html, flags=re.S)

    # --- blockquotes: alert vs history vs competency -----------------------
    def bqrepl(m):
        inner = m.group(1)
        if '\u26a0' in inner or 'Important Rule' in inner or 'Valid only when' in inner:
            return '<div class="alert fade-in">%s</div>' % inner
        if '\U0001F4DC' in inner or 'Scientific Contribution' in inner or 'Aryabhat' in inner:
            return '<blockquote class="history fade-in">%s</blockquote>' % inner
        return '<blockquote class="fade-in">%s</blockquote>' % inner

    html = re.sub(r'<blockquote>(.*?)</blockquote>', bqrepl, html, flags=re.S)

    # --- worked examples ---------------------------------------------------
    def werepl(m):
        inner = m.group(1)
        return ('<div class="worked-example fade-in"><div class="label">Worked Example</div>'
                '<p><strong>Worked Example%s</p></div>' % inner)

    html = re.sub(r'<p><strong>Worked Example(.*?)</p>', werepl, html, flags=re.S)

    # --- fade-in on remaining blocks ---------------------------------------
    html = re.sub(r'<(h3|h4|p|ul|ol|table)((?![^>]*class)[^>]*)>',
                  r'<\1 class="fade-in"\2>', html)

    sidebar = '\n'.join('    <a href="#%s" data-section>%s</a>' % (s, t) for s, t in toc)

    css = (CSS_TPL.replace('__ACCENT__', meta['accent'])
                  .replace('__ACCENT_LIGHT__', meta['accent_light'])
                  .replace('__SIDEBAR_BG__', meta['sidebar_bg'])
                  .replace('__SIDEBAR_TEXT__', meta['sidebar_text'])
                  .replace('__HOVER__', meta['hover']))

    page = (TPL.replace('__HEAD_TITLE__', 'Ch %d \u2014 %s' % (ch, meta['title']))
               .replace('__CHAPTER_LABEL__', '%s \u00b7 %s' % (meta['sub'], meta['title']))
               .replace('__H1__', meta['title'])
               .replace('__SUBTITLE__', '%s \u2014 Revision Notes' % meta['sub'])
               .replace('__SIDEBAR__', sidebar)
               .replace('__BODY__', html)
               .replace('__CSS__', css)
               .replace('__JS__', JS))

    dst = os.path.join(folder, 'Notes.html')
    open(dst, 'w', encoding='utf-8').write(page)
    print('wrote %s (%d bytes, %d sections)' % (dst, len(page), len(toc)))


if __name__ == '__main__':
    for ch in CHAPTERS:
        p = os.path.join(HERE, 'Ch - %d' % ch, 'Notes.md')
        if os.path.exists(p):
            build(ch)
        else:
            print('skip ch %d (no Notes.md yet)' % ch)
