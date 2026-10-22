"""Build the Rotterdam deck slides in the Journey Coach GDS style."""
import html
import re
from pathlib import Path

# Run from anywhere: python3 docs/drupalcon-rotterdam/build_deck.py
OUT = Path(__file__).resolve().parents[2] / 'web' / 'drupalcon-rotterdam'
ORIG_INDEX = OUT / 'index.html'  # the presenter checklist is kept as written; only its frame is rebuilt
REPO = 'https://github.com/digitaljourneycoach/localgov-ai-demo'
W = 'https://drupal-ai-workshop.ddev.site'
L = 'https://localgov-ai-demo.ddev.site'

ICONS = {
    'ext': 'M13.5 6H5.25A2.25 2.25 0 0 0 3 8.25v10.5A2.25 2.25 0 0 0 5.25 21h10.5A2.25 2.25 0 0 0 18 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25',
    'right': 'M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3',
    'left': 'M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18',
    'check': 'm4.5 12.75 6 6 9-13.5',
}


def icon(name):
    return ('<svg class="icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="{ICONS[name]}"/></svg>')


def btn(label, href, live=True, ghost=False):
    cls = 'btn' + (' live' if live else '') + (' ghost' if ghost else '')
    return (f'<a class="{cls}" href="{href}" target="_blank" rel="noopener">{label} {icon("ext")}'
            '<span class="sr" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)"> (opens in a new tab)</span></a>')


HEAD = '''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{title} · DrupalCon Rotterdam update</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap">
<link rel="stylesheet" href="deck.css">
</head>
'''

TOPBAR = '''<header class="topbar">
  <span class="brand"><img src="img/djc-logo-full.svg" alt="Digital Journey Coach"><span class="event">DrupalCon Rotterdam to LocalGov Drupal</span></span>
  <span class="section-tag">{tag}</span>
</header>
'''

SR = 'position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)'

# (file, section, nav class, tram label, header tag, main html, notes)
S = []


def slide(file, section, navcls, label, tag, main, notes):
    S.append(dict(file=file, section=section, navcls=navcls, label=label, tag=tag, main=main, notes=notes))


slide('01-title.html', 'intro', '', 'What I brought back', 'LocalGov Drupal webinar', f'''
<div class="title-wrap">
  <div>
    <p class="kicker">Back from DrupalCon Rotterdam</p>
    <h1>Three AI demos for <span class="hl">council websites</span></h1>
    <p class="lede">What I learned at the Drupal AI workshop, and what it can already do on a LocalGov Drupal site. No code, and a person stays in charge.</p>
    <p class="small"><b>David Bishop</b> · Digital Journey Coach</p>
  </div>
  <div class="summary" aria-label="This talk at a glance">
    <dl>
      <div><dt>Length</dt><dd>7 minutes</dd></div>
      <div><dt>Live demos</dt><dd>3<span>on real Drupal websites</span></dd></div>
      <div><dt>Who presses publish</dt><dd>You<span>every time</span></dd></div>
    </dl>
  </div>
</div>''', [
    'Hello. A quick update from DrupalCon Rotterdam.',
    'I did the hands-on Drupal AI workshop, then tried the same ideas on LocalGov Drupal.',
    'Promise: no code, three short demos, done in seven minutes.',
])

slide('02-route.html', 'intro', '', "Today's demos", "Today's demos", f'''
<p class="kicker">Today's demos</p>
<h2>Three demos, about two minutes each</h2>
<div class="grid g3">
  <div class="card stop w"><span class="num">1</span><h3>Ask the website a question</h3><p>Residents ask in their own words and get an answer from your own pages, with links.</p></div>
  <div class="card stop t"><span class="num">2</span><h3>Check a page against your style guide</h3><p>The AI spots mistakes and suggests fixes before a page goes live.</p></div>
  <div class="card stop b"><span class="num">3</span><h3>Ask an assistant to update the site</h3><p>Put up an alert banner by asking for it in plain English.</p></div>
</div>
<p class="callout" style="margin-top:1.4rem"><b>Good to know:</b> it's all free and open source. Some of it is still early, test-stage software. A person always checks the work and presses publish.</p>
''', [
    "Set expectations: this is a look at what's possible, not something to put live on Monday.",
    'Everything here is open source and builds on the Drupal AI module.',
])

slide('03-workshop.html', 'workshop', 'workshop', 'Demo 1: the workshop', 'Demo 1 · Ask a question', f'''
<div class="split">
  <div>
    <p class="kicker">Demo 1 · Where it started</p>
    <h2>A university website with AI built in</h2>
    <p>At DrupalCon, <b>1xINTERNET</b> ran a hands-on workshop. We each added AI features to a website for Northmoor University, which is made up.</p>
    <ul>
      <li>Swap "university" for "council": it's the same Drupal underneath</li>
      <li>4 short steps, each with a written guide</li>
      <li>Anyone can run it, with a free trial AI account</li>
    </ul>
    <div class="btnrow">{btn('Open Northmoor', W + '/')}{btn('Workshop guides', 'https://1xinternet.github.io/drupal_ai_workshop/', live=False, ghost=True)}</div>
  </div>
  <figure><img class="shot" src="img/front-page.jpg" alt="The Northmoor University sample website front page"><figcaption>The workshop website: 20 pages, made-up people and AI-generated photos.</figcaption></figure>
</div>''', [
    'The workshop materials are public, so any council team can run it themselves.',
    "Swap 'university' for 'council' in your head: same Drupal, same modules.",
])

slide('04-workshop-tour.html', 'workshop', 'workshop', 'Demo 1: live', 'Demo 1 · Ask a question', f'''
<p class="kicker">Demo 1 · Live</p>
<h2>Ask a question, get an answer from your own pages</h2>
<div class="grid g4">
  <div class="card feature"><span class="tag">Live demo</span><h3>Ask the website</h3>
    <p>Type a question in plain words. The answer comes from the site's own pages, with links to them.</p>
    <p class="council"><b>For a council:</b> "When is my brown bin collected?"</p>
    <div class="btnrow">{btn('Ask a question', W + '/ask')}</div></div>
  <div class="card"><h3>Alt text written for you</h3>
    <p>Every uploaded image gets a description for people using screen readers.</p>
    <p class="council"><b>For a council:</b> help with the accessibility regulations.</p>
    <div class="btnrow">{btn('Images', W + '/admin/content/media', live=False, ghost=True)}</div></div>
  <div class="card"><h3>Safety rules</h3>
    <p>Rules that stop risky questions and answers.</p>
    <p class="council"><b>For a council:</b> keep residents' personal details away from the AI.</p>
    <div class="btnrow">{btn('Safety rules', W + '/admin/config/ai/guardrails', live=False, ghost=True)}</div></div>
  <div class="card"><h3>A record of everything</h3>
    <p>Every question and every answer is saved.</p>
    <p class="council"><b>For a council:</b> an answer when someone asks "why did it say that?"</p>
    <div class="btnrow">{btn('The record', W + '/admin/config/ai/logging/collection', live=False, ghost=True)}</div></div>
</div>''', [
    "LIVE (about 60 seconds): click Ask a question. Use a suggested question, or type 'How much does it cost to study marine biology?'",
    'Point out the links: the answer comes from the website\'s own pages.',
    "Council angle: 'Imagine Ask the council: when is my brown bin collected?'",
    "If there's time, open The record: 'every question and answer is kept'.",
    'Backup if the site is slow: talk over the four cards.',
])

slide('05-content-review.html', 'review', 'review', 'Demo 2: content review', 'Demo 2 · Check a page', f'''
<div class="split">
  <div>
    <p class="kicker">Demo 2 · AI Content Review</p>
    <h2>A second pair of eyes for every page</h2>
    <p>Write your style guide down once. The AI checks a page against it, gives it a score, points to each mistake and suggests a fix. It never changes the page by itself.</p>
    <ol class="steps">
      <li>Choose which pages to check</li>
      <li>Write your house rules in plain English</li>
      <li>The AI gives a score and points out each mistake</li>
      <li>An editor decides what to change</li>
    </ol>
  </div>
  <div class="card feature">
    <h3>Why it matters for councils</h3>
    <ul style="margin:0">
      <li>30 editors, 1 style guide, checked the same way every time</li>
      <li>Plain English checked before a page goes live</li>
      <li>Find the pages that need the most work</li>
      <li>It only runs when someone asks. Nothing changes without an editor.</li>
    </ul>
  </div>
</div>''', [
    "Key message: the AI doesn't publish anything. It's a second pair of eyes.",
    "The 'house rules' are just your style guide written down. On LocalGov I've used the GOV.UK style rules.",
])

notice_marks = [
    ('Christmas And New Year Bin Collections', 'Headings in sentence case'),
]
slide('06-spot-the-mistakes.html', 'review', 'review', 'Demo 2: spot the mistakes', 'Demo 2 · Check a page', '''
<div data-reveal-target>
  <div style="display:flex;justify-content:space-between;align-items:end;gap:1rem;flex-wrap:wrap">
    <div><p class="kicker">Demo 2 · Quick game</p><h2 style="margin-bottom:.3em">How many mistakes can you spot?</h2>
    <p class="small" style="margin:0 0 .8rem">A typical council page, checked against the GOV.UK style guide. You have 15 seconds. Put your number in the chat.</p></div>
    <div class="btnrow" style="margin:0 0 .8rem"><button class="btn" data-reveal type="button">Reveal the mistakes</button><span class="btn ghost score">15 found</span></div>
  </div>
  <div class="spot">
  <div class="notice">
      <h3><mark data-rule="Headings in sentence case">Christmas And New Year Bin Collections</mark><mark data-rule="No exclamation marks">!!</mark></h3>
      <p><mark data-rule="“Please note” adds nothing">Please note</mark> that due to the Christmas <mark data-rule="Write “and”, not “&amp;”">&amp;</mark> New Year <mark data-rule="“bank holidays” in lower case">Bank Holidays</mark>, collections will be one day late from Monday <mark data-rule="“21 December”, not “21st”">21st</mark> December <mark data-rule="Use “to” for ranges, not a dash">-</mark> Friday <mark data-rule="“1 January”, not “1st”">1st</mark> January.</p>
      <p><mark data-rule="“In order to” → “To”">In order to</mark> <mark data-rule="“utilise” → “use”">utilise</mark> the garden waste service, put your brown bin out by <mark data-rule="“7am”, not “7.00am”">7.00am</mark> <mark data-rule="Over 40 words: split it">on the morning of collection, otherwise we will be unable to empty it and you will need to wait until the next scheduled collection which may well be in the new year.</mark></p>
      <p>Real trees can be recycled, <mark data-rule="“for example”, not “e.g.”">e.g.</mark> left next to your green bin. For more information <mark data-rule="“Click here” tells you nothing">click here</mark>.</p>
      <p><mark data-rule="No block capitals">CONTAMINATED BINS WILL NOT BE EMPTIED.</mark></p>
  </div>
  <ol class="legend">
      <li>Headings in sentence case</li>
      <li>No exclamation marks</li>
      <li>“Please note” adds nothing</li>
      <li>Write “and”, not “&amp;”</li>
      <li>“bank holidays” in lower case</li>
      <li>“21 December”, not “21st”</li>
      <li>Use “to” for ranges, not a dash</li>
      <li>“1 January”, not “1st”</li>
      <li>“In order to” → “To”</li>
      <li>“utilise” → “use”</li>
      <li>“7am”, not “7.00am”</li>
      <li>Over 40 words: split it</li>
      <li>“for example”, not “e.g.”</li>
      <li>“Click here” tells you nothing</li>
      <li>No block capitals</li>
  </ol>
  </div>
</div>''', [
    '15 seconds: ask the audience to put a number in the chat.',
    'Press R (or the button) to reveal. There are 15.',
    "Then: 'a person takes a couple of minutes. The AI takes about 10 seconds. Let's see.'",
])

slide('07-content-review-live.html', 'review', 'review', 'Demo 2: live', 'Demo 2 · Check a page', f'''
<div class="split">
  <div>
    <p class="kicker">Demo 2 · Live on LocalGov Drupal</p>
    <h2>The same page, checked by AI</h2>
    <ol class="steps">
      <li>Open the page and click <b>AI Review</b>, then <b>Review</b></li>
      <li>About 10 seconds later: a score, and a pass or fail</li>
      <li>Each mistake is quoted, with a suggested fix</li>
      <li>The editor accepts or ignores each one and gets a to-do list</li>
      <li>Fix the page, check it again, and it passes</li>
    </ol>
    <div class="btnrow">{btn('The bin page', L + '/christmas-bin-collections')}{btn('Every page’s result', L + '/admin/content/ai-review')}</div>
    <p class="small" style="margin-top:.8rem">One list shows the result for every page, so you can see where to start.</p>
  </div>
  <figure><img class="shot" src="img/review-detail.png" alt="AI Content Review showing its explanation and suggested changes beside the page editor"><figcaption>Backup screenshot from the workshop: the explanation and suggested changes.</figcaption></figure>
</div>''', [
    'LIVE (about 60 seconds): open the bin page, click the AI Review tab, then Review.',
    "While it thinks: 'it's reading the page and our GOV.UK style rules.'",
    "Open a mistake and click 'Show proposed change'. Click Accept on one and show the to-do list (Improvement plan).",
    "DON'T click Apply: in this early version it replaces the whole page text.",
    "Finish on Every page's result: 'imagine this across 2,000 pages.'",
])

slide('08-mcp.html', 'mcp', 'mcp', 'Demo 3: an AI assistant', 'Demo 3 · Ask an assistant', '''
<div class="split">
  <div>
    <p class="kicker">Demo 3 · LocalGov MCP</p>
    <h2>Ask an assistant to update the website</h2>
    <p>AI assistants such as Claude, ChatGPT and Copilot can now use a website's tools, through a <span class="hl">universal plug</span> called MCP.</p>
    <p>I've built a free LocalGov Drupal add-on, <b>localgov_mcp</b>, that gives an assistant the everyday jobs a web editor does.</p>
    <p class="callout">Think of it as giving a temp a staff login, not the keys to the building.</p>
  </div>
  <div class="grid g2">
    <div class="card plain"><b>Pages</b><span class="small">find, draft and publish</span></div>
    <div class="card plain"><b>Alert banners</b><span class="small">put up and take down</span></div>
    <div class="card plain"><b>Scheduling</b><span class="small">go live or come down later</span></div>
    <div class="card plain"><b>Images</b><span class="small">find and upload</span></div>
    <div class="card plain"><b>Redirects</b><span class="small">fix broken links</span></div>
    <div class="card plain"><b>Locations</b><span class="small">venue addresses</span></div>
  </div>
</div>''', [
    "Keep it simple: MCP is the plug, my add-on is the set of tools behind the plug.",
    'The tools are written for LocalGov pages such as service pages, guides, directories, events and news.',
])

slide('09-mcp-storm.html', 'mcp', 'mcp', 'Demo 3: live', 'Demo 3 · Ask an assistant', f'''
<div class="split">
  <div>
    <p class="kicker">Demo 3 · Live</p>
    <h2>7am. Storm Brenda has flooded the leisure centre.</h2>
    <p>The comms officer is on the bus. Normally that means phoning whoever has a laptop. Instead, they just ask.</p>
    <div class="btnrow">{btn('Council homepage', L + '/')}{btn('Alert banners', L + '/admin/content/alert-banner')}{btn('Content', L + '/admin/content')}</div>
    <p class="small" style="margin-top:.8rem">Example conversation. The assistant's wording changes every time.</p>
  </div>
  <div class="chat">
    <div class="bubble me">Put up an alert banner saying the leisure centre is closed today because of flooding.</div>
    <div class="bubble ai">Done. I've created the banner "Leisure centre closed today". It isn't live yet. Shall I publish it?<span class="did">{icon('check')} Banner created, not live</span></div>
    <div class="bubble me">Yes, publish it. And take it down at 6pm.</div>
    <div class="bubble ai">It's live, and it will come down at 6pm today.<span class="did">{icon('check')} Banner live, ends at 6pm</span></div>
    <div class="bubble me">Now write a news story about it, but don't publish it.</div>
    <div class="bubble ai">I've saved a draft news story for a colleague to check.<span class="did">{icon('check')} Draft saved for checking</span></div>
  </div>
</div>''', [
    'LIVE (about 90 seconds): in the terminal, run npm run chat in the localgov_mcp client folder (or use Claude Desktop).',
    'Type the first message. Then click Council homepage and refresh to show the banner.',
    "Encore if there's time: 'Find any pages about blue badges and list them.'",
    'Backup: if the AI is slow, talk through the conversation on screen.',
])

slide('10-safety.html', 'mcp', 'mcp', "Demo 3: who's in charge", 'Demo 3 · Ask an assistant', f'''
<p class="kicker">Demo 3 · Safety first</p>
<h2>Who's in charge? <span class="hl">Still you.</span></h2>
<div class="grid g4">
  <div class="card"><h3>Same login</h3><p>The assistant signs in as a real staff member, so it can only do what that person could do.</p></div>
  <div class="card"><h3>Drafts first</h3><p>Changes to pages are saved as drafts. Publishing needs the usual sign-off.</p></div>
  <div class="card"><h3>Switch jobs off</h3><p>Turn off anything you don't want an AI doing, with a tick box.</p></div>
  <div class="card"><h3>A full history</h3><p>Every change is kept in the page history, like any other edit.</p></div>
</div>
<div class="btnrow" style="margin-top:1rem">{btn('Tool settings', L + '/admin/config/services/localgov-mcp')}</div>
<p class="big fit" style="margin-top:1.2rem">A very fast new starter: <span class="hl">same permissions, same sign-off.</span></p>''', [
    'This is the slide for the information governance people.',
    'Show the tool settings page: switch any job off with a tick box.',
])

slide('11-next-stop.html', 'outro', '', 'What next', 'What next', f'''
<p class="kicker">What next</p>
<h2>Try it, then let's build the council version together</h2>
<div class="grid g2">
  <div class="card plain">
    <h3>Have a go</h3>
    <ul style="margin:0">
      <li>Run the workshop yourself: about an hour, with a free trial AI account</li>
      <li>Read about AI Content Review and the Drupal AI module</li>
      <li>localgov_mcp is coming to drupal.org. Ask me for an early look.</li>
    </ul>
    <div class="btnrow">{btn('Workshop', 'https://github.com/1xINTERNET/drupal_ai_workshop', live=False, ghost=True)}{btn('AI Content Review', 'https://www.drupal.org/project/ai_content_review', live=False, ghost=True)}{btn('Drupal AI', 'https://www.drupal.org/project/ai', live=False, ghost=True)}</div>
  </div>
  <div class="card feature">
    <h3>Ideas for us as a community</h3>
    <ul style="margin:0">
      <li>Shared <b>GOV.UK style rules</b> for AI Content Review, ready for any council to use</li>
      <li>"Ask the council" answers from LocalGov pages</li>
      <li>An agreed set of assistant jobs, and an "AI editor" role</li>
      <li>Shared safety rules, for example keeping residents' personal details out</li>
    </ul>
  </div>
</div>''', [
    'Call to action: who wants to work on shared GOV.UK style rules?',
    "It's all open source: build it once and every council benefits.",
])

slide('12-thanks.html', 'outro', '', 'Thank you', 'Thank you', f'''
<div class="title-wrap end">
  <div>
    <p class="kicker">Thank you</p>
    <h1>Bedankt. <span class="hl">Thank you.</span></h1>
    <p class="lede">Questions, ideas, or "please keep the AI away from our website"? All welcome.</p>
    <p><b>David Bishop</b> · Digital Journey Coach · digitaljourneycoach.com</p>
    <p class="small">Thanks to 1xINTERNET for the workshop, and to everyone who builds the Drupal AI and LocalGov Drupal modules.</p>
  </div>
  <div class="summary promo">
    <p class="kicker">Have a play</p>
    <h3>Get the demo council website</h3>
    <p>Everything you've seen today is in one free, public project: the LocalGov Drupal site, the AI features and these slides.</p>
    <p class="repo">github.com/digitaljourneycoach/<wbr>localgov-ai-demo</p>
    <ol class="steps">
      <li>Download it from GitHub</li>
      <li>Start it on your laptop with DDEV</li>
      <li>Try the demos, then break things safely</li>
    </ol>
    <div class="btnrow">{btn('Get it on GitHub', REPO, live=False)}</div>
  </div>
</div>''', [
    'Promote the repo: paste https://github.com/digitaljourneycoach/localgov-ai-demo into the webinar chat now.',
    "It's a full LocalGov Drupal site with the demos and these slides. Anyone with DDEV can run it on a laptop.",
    'Thank 1xINTERNET and the Drupal AI initiative.',
    'Point people to the LocalGov Drupal Slack for follow-ups.',
])


def nav(i):
    n = len(S)
    prev = 'index.html' if i == 0 else S[i - 1]['file']
    nxt = S[i + 1]['file'] if i < n - 1 else None
    out = ['<nav class="deck-nav" aria-label="Slides">',
           f'  <a class="btn ghost navbtn" href="{prev}" rel="prev">{icon("left")} <span>Back</span></a>',
           '  <div>', '    <div class="tram">',
           f'      <span class="progress" style="width:{round(i / (n - 1) * 100, 2)}%"></span>']
    for j, s in enumerate(S):
        cls = ' '.join(c for c in [s['navcls'], 'done' if j < i else '', 'current' if j == i else ''] if c)
        cur = ' aria-current="page"' if j == i else ''
        lbl = html.escape(f"{j + 1}. {s['label']}")
        out.append(f'      <a class="{cls}" href="{s["file"]}"{cur}><span class="lbl">{lbl}</span>'
                   f'<span class="sr" style="{SR}">Slide {j + 1}: {html.escape(s["label"])}</span></a>')
    out += ['    </div>', f'    <div class="counter">{i + 1} / {n}</div>', '  </div>']
    if nxt:
        out.append(f'  <a class="btn navbtn" href="{nxt}" rel="next"><span>Next</span> {icon("right")}</a>')
    else:
        out.append(f'  <a class="btn navbtn" href="{S[0]["file"]}" aria-disabled="true"><span>Next</span> {icon("right")}</a>')
    out.append('</nav>')
    return '\n'.join(out)


def notes_html(items):
    lis = '\n'.join(f'<li>{html.escape(x)}</li>' for x in items)
    return f'<aside class="notes" aria-label="Speaker notes"><h4>Speaker notes · press N to hide</h4><ul>\n{lis}\n</ul></aside>'


FOOT = '<div class="keyhint">Arrow keys move · N notes · F full screen</div>\n<script src="deck.js"></script>\n</body>\n</html>\n'

for i, s in enumerate(S):
    prev = 'index.html' if i == 0 else S[i - 1]['file']
    nxt = S[i + 1]['file'] if i < len(S) - 1 else ''
    page = (HEAD.format(title=html.escape(s['label'])) +
            f'<body class="section-{s["section"]}" data-prev="{prev}" data-next="{nxt}" data-first="{S[0]["file"]}" data-last="{S[-1]["file"]}">\n' +
            TOPBAR.format(tag=html.escape(s['tag'])) +
            f'<main class="slide" id="main">{s["main"]}\n</main>\n' + nav(i) + '\n' + notes_html(s['notes']) + '\n' + FOOT)
    (OUT / s['file']).write_text(page, encoding='utf-8')

# Presenter checklist: keep its content, swap in the new head, header, icons and nav.
src = ORIG_INDEX.read_text(encoding='utf-8')
body_open = re.search(r'<body[^>]*>', src).group(0)
main = re.search(r'<main.*?</main>', src, re.S).group(0)
main = main.replace(' 🧰', '').replace('Pre-flight checks · do these before the webinar', 'Before the webinar')
main = main.replace('d11-localgov.ddev.site', 'localgov-ai-demo.ddev.site')
main = main.replace(' ↗</a>', ' ' + icon('ext') + '</a>').replace('Start the talk →', 'Start the talk ' + icon('right'))
tail = src[src.index('<aside'):src.index('<div class="keyhint">')]
nav0 = ('<nav class="deck-nav" aria-label="Slides">\n'
        f'  <span class="btn ghost navbtn" aria-disabled="true">{icon("left")} <span>Back</span></span>\n'
        '  <div><div class="counter">Presenter checklist</div></div>\n'
        f'  <a class="btn navbtn" href="01-title.html" rel="next"><span>Start the talk</span> {icon("right")}</a>\n</nav>')
page = (HEAD.format(title='Before you start') + body_open + '\n' +
        TOPBAR.format(tag='Presenter checklist · not for sharing') + main + '\n' + nav0 + '\n' + tail + FOOT)
(OUT / 'index.html').write_text(page, encoding='utf-8')
print('built', len(S) + 1, 'pages')
