import json, html, os, re, zipfile
import xml.etree.ElementTree as ET

# ---------------------------------------------------------------- Texts from the Excel sheet
# tools/teksten.xlsx: column A is the ID (home.guitar, case.ikea.brief, contact.email, …), column F "Jouw tekst".
# A filled-in F overrides the text written in this file. Read with the standard library, no extra packages.
def read_texts(path='teksten.xlsx'):
    if not os.path.exists(path): return {}
    ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(path) as z:
        shared = []
        if 'xl/sharedStrings.xml' in z.namelist():
            for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', ns):
                shared.append(''.join(t.text or '' for t in si.iter('{%s}t' % ns['m'])))
        wb = ET.fromstring(z.read('xl/workbook.xml'))
        rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        rid = next(s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                   for s in wb.find('m:sheets', ns) if s.get('name') == 'Teksten')
        target = next(r.get('Target') for r in rels if r.get('Id') == rid).lstrip('/')
        sheet = ET.fromstring(z.read(target if target.startswith('xl/') else 'xl/' + target))
    def val(c):
        if c is None: return ''
        if c.get('t') == 's': return shared[int(c.find('m:v', ns).text)]
        if c.get('t') == 'inlineStr': return ''.join(t.text or '' for t in c.iter('{%s}t' % ns['m']))
        v = c.find('m:v', ns); return v.text if v is not None and v.text else ''
    out = {}
    for row in sheet.iter('{%s}row' % ns['m']):
        cells = {re.match(r'[A-Z]+', c.get('r')).group(0): c for c in row.findall('m:c', ns)}
        key, text = val(cells.get('A')).strip(), val(cells.get('F')).strip()
        if '.' in key and text: out[key] = text
    return out
TEXT = read_texts()
def tx(key, default):
    """The Excel text for key (HTML-escaped), or the default written in this file."""
    return html.escape(TEXT[key], quote=False) if key in TEXT else default
EMAIL = TEXT.get('contact.email', 'hello@example.com')
# LinkedIn profile. The Excel row contact.linkedin overrides it.
LINKEDIN = TEXT.get('contact.linkedin', 'https://www.linkedin.com/in/nickycorrelje/')
# The LinkedIn "in" mark in one colour (LinkedIn allows the logo in black / one colour when it links to a profile).
ICON_LINKEDIN = ('<svg aria-hidden="true" width="22" height="22" viewBox="0 0 24 24" fill="currentColor">'
                 '<path d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z"/></svg>')

H1 ="I'm Nicky. I combine <span class=\"tip\" tabindex=\"0\" data-tip=\"Currently at IKEA\">design and behavioural science</span> to make sustainable decisions easier."

def page(title, body, world=None):
    wd = f'<script type="application/json" id="world-data">{json.dumps(world)}</script>\n' if world else ''
    scripts = wd + '<script src="js/game.js"></script>\n<script src="js/config.js"></script>\n<script src="js/home.js"></script>\n<script src="js/tip.js"></script>\n<script src="js/router.js"></script>'
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} – Nicky's Desktop Adventures</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Silkscreen:wght@400;700&family=Catamaran:wght@400;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/site.css">
</head>
<body>
<div class="page"><div class="wrap">
<header class="site-header">
<a class="logo" href="index.html"><img src="assets/head.png" alt="">Nicky Correljé</a>
<a class="btn" href="index.html">About this project</a>
</header>
<h1 class="headline">{H1}</h1>
{body}
<footer class="site-footer">
<span class="talk">Let's talk.</span>
<span class="links"><a class="btn" href="mailto:{html.escape(EMAIL)}">Email me</a><a class="btn icon" href="{html.escape(LINKEDIN)}" target="_blank" rel="noopener" aria-label="LinkedIn" title="LinkedIn">{ICON_LINKEDIN}</a></span>
<small>© 2026 Nicky Correljé</small>
</footer>
</div></div>
{scripts}
</body>
</html>
'''

ICON_WORLD = ('<svg aria-hidden="true" width="22" height="22" viewBox="0 0 22 22" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="miter">'
              '<path d="M2 5 L8 3 L14 5 L20 3 V17 L14 19 L8 17 L2 19 Z"></path><path d="M8 3 V17 M14 5 V19"></path></svg>')
ICON_LIST = ('<svg aria-hidden="true" width="22" height="22" viewBox="0 0 22 22" fill="currentColor"><rect x="2" y="4" width="4" height="4"></rect>'
             '<rect x="9" y="5" width="11" height="2.5"></rect><rect x="2" y="9" width="4" height="4"></rect><rect x="9" y="10" width="11" height="2.5"></rect>'
             '<rect x="2" y="14" width="4" height="4"></rect><rect x="9" y="15" width="11" height="2.5"></rect></svg>')
WORLD_PAGE = {'About': 'index.html', 'Work': 'work.html'}           # About = my personal world (Utrecht)
LIST_PAGE = {'About': 'about-list.html', 'Work': 'work-list.html'}

def nav(active, view='world'):
    """Menu (About / Work) plus the map / list switch on the right. In the list view the menu stays in the list view."""
    pages = LIST_PAGE if view == 'list' else WORLD_PAGE
    items = ''.join(f'<a href="{pages[l]}"{" class=on aria-current=page" if l == active else ""}>{l}</a>' for l in ('About', 'Work'))
    switch = (f'<span class="views" role="group" aria-label="View">'
              f'<a href="{WORLD_PAGE[active]}" aria-label="World view" title="World view"{" class=on aria-current=page" if view == "world" else ""}>{ICON_WORLD}</a>'
              f'<a href="{LIST_PAGE[active]}" aria-label="List view" title="List view"{" class=on aria-current=page" if view == "list" else ""}>{ICON_LIST}</a></span>')
    return f'<nav class="menu" aria-label="Main">{items}{switch}</nav>'

def window(title, active, stage, aside, fit=False, view='world'):
    body_cls = 'window-body list-body' if view == 'list' else 'window-body' + (' fit' if fit else '')
    return f'''<div class="window">
<div class="titlebar"><span class="dots" aria-hidden="true"><i></i><i></i></span><span class="title">{html.escape(title)}</span></div>
{nav(active, view)}
<div class="{body_cls}">
{stage}
{aside}
</div>
</div>'''

def pill(text, href, left, top, cls=''):
    return f'<a class="pill {cls}" href="{href}" style="left:{left}%;top:{top}%">{text}</a>'
def sign(text, left, top, color='#fff'):
    return f'<span class="sign" style="left:{left}%;top:{top}%;color:{color}">{text}</span>'

def stage(img, alt, inner, w=320, h=224):
    return f'''<div class="stage" id="stage" role="application" aria-label="Walk with the arrow keys" style="aspect-ratio:{w}/{h}">
<img class="world" src="assets/{img}" alt="{html.escape(alt)}">
{inner}
<div class="hero" id="hero" role="img" aria-label="Nicky, walking"></div>
</div>'''

def pcard(title, badge, desc, href=None, feature=False):
    cls = 'card' + (' feature' if feature else '')
    b = f'<span class="badge">{badge}</span>' if badge else ''
    inner = f'<div class="card-head"><strong>{title}</strong>{b}</div><span class="desc">{desc}</span>'
    return f'<a class="{cls}" href="{href}">{inner}</a>' if href else f'<div class="{cls}">{inner}</div>'

# ---------------------------------------------------------------- Utrecht (start)
START = dict(
    w=320, h=224, bubble='above',
    spawns={'default': [148, 150, 'down'], 'klimhal': [65, 112, 'down'], 'home': [209, 114, 'down'], 'work': [148, 168, 'up']},
    solid=[[24, 72, 76, 50], [196, 60, 50, 64], [268, 38, 24, 98], [0, 184, 146, 24], [176, 184, 144, 24]]
          + [[tx + 2, ty + 6, 9, 10] for tx, ty in [(4,20),(34,30),(8,52),(110,40),(118,92),(150,20),(186,22),(252,14),(300,100),(6,156),(56,160),(110,156),(208,158),(262,160),(298,150),(14,208),(60,210),(240,212),(290,210)]],
    doors=[[67, 122, 20, 10, 'room-klimhal.html'], [211, 124, 20, 10, 'room-home.html'], [146, 212, 30, 12, 'work.html?from=utrecht']],
)
start_stage = stage('world-start.png',
  'Pixel-art Utrecht: a climbing hall on the left, my canal house on the right and the Dom tower. A canal with a bridge at the bottom leads to my work.',
  sign('KLIMHAL', 19.4, 34.2) + pill('Enter →', 'room-klimhal.html', 24, 55.8) + pill('Enter →', 'room-home.html', 69.1, 58)
  + '<span class="pill soon" style="left:87.2%;top:61%;background:var(--cream);color:var(--ink);border:2px solid var(--ink);border-style:solid">Utrecht based</span>'
  + pill('Go to work ↓', 'work.html?from=utrecht', 50, 88)
  + '<div class="bubble" id="bubble">' + tx('bubble.utrecht', 'Hi, I\'m Nicky! Walk into my home or the climbing hall to get to know me. Or cross the bridge to see my work.') + '</div>')
start_aside = '''<aside class="aside" aria-label="Places">
<div class="aside-head"><h2>Places</h2></div>
''' + pcard('Home', 'Enter', 'A canal house with records, a guitar, a sewing machine, two pets and a lot of plants. Walk in to get to know me.', 'room-home.html', True) \
    + pcard('Klimhal', 'Enter', 'Chalk, crash mats and friends. Walk in to meet them.', 'room-klimhal.html') \
    + pcard('Utrecht based', '', 'The reason this part of the map is Utrecht.') \
    + pcard('Go to work', '', 'The bridge at the bottom leads across the canal to my work.', 'work.html?from=utrecht') \
    + '<span class="hint">Walk with the arrow keys or W A S D. Doors lead inside.</span></aside>'
open('../index.html', 'w').write(page('Utrecht', window('Get to know me', 'About', start_stage, start_aside), START))

# ---------------------------------------------------------------- Work
WORK = dict(
    w=320, h=288, bubble='right',
    spawns={'default': [148, 70, 'down'], 'utrecht': [148, 70, 'down'], 'mclaren': [44, 206, 'down'], 'adidas': [99, 206, 'down'],
            'swifty': [194, 206, 'down'], 'ikea': [252, 124, 'down'], 'pledge': [43, 102, 'down']},
    solid=[[10, 66, 90, 46], [218, 66, 92, 68], [30, 172, 52, 42], [88, 174, 46, 40], [184, 174, 44, 40], [0, 34, 146, 22], [176, 34, 144, 22]]
          + [[tx + 2, ty + 6, 9, 10] for tx, ty in [(110,76),(122,118),(190,80),(196,122),(4,126),(8,176),(250,178),(290,182),(236,194),(300,126),(8,252),(60,256),(110,258),(206,256),(262,256),(298,252),(4,6),(60,8),(100,10),(200,8),(240,6),(290,12),(30,16)]],
    doors=[[46, 214, 20, 10, 'room-case.html'], [101, 214, 20, 10, 'room-adidas.html'], [196, 214, 20, 10, 'room-swifty.html'],
           [254, 134, 20, 10, 'room-ikea.html'], [45, 112, 20, 10, 'room-pledge.html'], [146, 30, 30, 14, 'index.html?from=work']],
)
work_inner = (sign('MCLAREN', 17.5, 61.5, '#2b2433') + sign('ADIDAS', 34.7, 62.2) + sign('SWIFTY', 64.4, 62.2) + sign('IKEA', 82.5, 29.5, '#0058a3') + sign('CLIMATE PLEDGE ARENA', 17.2, 32.3)
  + pill('Enter →', 'room-case.html', 17.5, 75) + pill('Enter →', 'room-adidas.html', 34.7, 75) + pill('Enter →', 'room-swifty.html', 64.4, 75)
  + pill('Enter →', 'room-ikea.html', 82.5, 48.1) + pill('Enter →', 'room-pledge.html', 17.2, 40.6)
  + '<a class="sign-link" href="index.html?from=work" aria-label="To Utrecht" style="left:59%;top:19.5%"><span class="plate">Utrecht <span>↑</span></span><span class="post"></span></a>'
  + '<span class="flag" style="left:70.3%;top:18.1%"></span><span class="flag" style="left:95.3%;top:18.1%"></span>'
  + '<div class="bubble" id="bubble">' + tx('bubble.work', 'My work from the last couple of years. Walk into a building!') + '</div>')
work_stage = stage('world-work.png', 'Pixel-art work world: Utrecht across a canal, then below the bridge the Climate Pledge Arena, a McLaren showroom, an adidas store, the Swifty bar and a big blue IKEA box.', work_inner, 320, 288)
skills = [('plant', 'var(--green-tint)', 'Immersing in new topics', 'Desk research, interviews, experts.'),
          ('sneaker', 'var(--peach)', 'Mapping behaviours', 'Which behaviour to change, and why.'),
          ('headphones', 'var(--rose)', 'Capturing ideas', 'Workshops that turn heads into shared ideas.'),
          ('leaf', 'var(--sky)', 'Designing interventions', 'Products, services, small nudges.'),
          ('scissors', 'var(--peach)', 'Making the intangible tangible', 'Sketches, flows and prototypes.'),
          ('spool', 'var(--green-tint)', 'Making the complex simple', 'Untangling rules into clear structures.')]
work_aside = '<aside class="aside tight" aria-label="My skills"><div class="aside-head"><h2>In my backpack</h2></div>' + ''.join(
    f'<div class="skill"><span class="ico" style="background:{bg}"><img src="assets/icon-{ic}.png" alt=""></span><span><strong>{t}</strong><small>{d}</small></span></div>' for ic, bg, t, d in skills) + '</aside>'
open('../work.html', 'w').write(page('Work', window('My work', 'Work', work_stage, work_aside), WORK))


# ---------------------------------------------------------------- Rooms with collectables (Home, Klimhal)
def hot(key, label, left, top, on=False):
    # The label is dark; only the hotspot of the item you are looking at is green (class "on", kept in step by js/home.js).
    return (f'<button class="hot{" on" if on else ""}" type="button" data-item="{key}" aria-label="{label}" style="left:{left}%;top:{top}%">'
            f'<span class="ring"></span><span class="dot"></span><span class="lab">{label}</span></button>')

SPIN = ('<div class="spin" id="spin" hidden><img src="assets/icon-vinyl.png" alt="">'
        '<span><small id="spin-label">Now spinning</small><strong id="spin-text">…</strong></span></div>')

def room(items, title, kind, world, img, alt, stage_extra, bubble, aside_title, back, extras=None, hotspot_first_green=True):
    extras = extras or {}
    inner = stage_extra + ''.join(hot(k, l, hs[0], hs[1], hotspot_first_green and i == 0) for i, (k, l, ic, hs, t) in enumerate(items))
    inner += back + f'<div class="bubble" id="bubble">{bubble}</div>'
    st = stage(img, alt, inner)
    tiles = ''.join(f'<button class="tile{" on" if i==0 else ""}" type="button" data-item="{k}" aria-pressed="{"true" if i==0 else "false"}"><img src="assets/icon-{ic}.png" alt=""><span>{l}</span></button>' for i, (k, l, ic, hs, t) in enumerate(items))
    details = ''.join(f'<div class="detail" data-item="{k}"{"" if i==0 else " hidden"}><strong>{l}</strong><p>{t}</p>{extras.get(k, "")}</div>' for i, (k, l, ic, hs, t) in enumerate(items))
    aside = (f'<aside class="aside" aria-label="{aside_title}"><div class="aside-in"><div class="aside-head"><h2>{aside_title}</h2></div>'
             f'<div class="tiles" tabindex="0" aria-label="Collectables">{tiles}</div><div class="detail-card">{details}</div></div></aside>')
    return window(title, 'About', st, aside, True)

# Home
HOME = dict(
    w=320, h=224, bubble='right',
    spawns={'default': [152, 176, 'up'], 'start': [154, 104, 'down']},
    solid=[[0, 0, 320, 84], [124, 62, 62, 40], [98, 70, 18, 26], [233, 70, 72, 37], [6, 80, 25, 49], [12, 134, 83, 51], [256, 144, 50, 76], [176, 160, 20, 14]],
    doors=[[132, 214, 56, 10, 'index.html?from=home']],
)
home_items = [  # key, label, icon, hotspot (left, top), text
 ('records', 'Records', 'vinyl', (47.8, 29.0), 'I own a (very) small vinyl collection. [ADD: what is on the turntable now.]'),
 ('guitar', 'Guitar', 'guitar', (33.1, 41.1), '[WRITE 1–2 SENTENCES: the guitar.]'),
 ('camera', 'Camera', 'camera', (60.9, 10.7), '[WRITE 1–2 SENTENCES: the film camera.]'),
 ('sewing', 'Sewing machine', 'spool', (82.5, 30.4), '[WRITE 1–2 SENTENCES: the sewing machine.]'),
 ('plants', 'Plants', 'plant', (87.5, 87.1), '[WRITE 1–2 SENTENCES: the plants.]'),
 ('cat', 'Black cat', 'cat', (21.2, 76.8), '[WRITE 1–2 SENTENCES: the cat.]'),
 ('dog', 'Red dog', 'dog', (59.1, 79.5), '[WRITE 1–2 SENTENCES: the dog.]'),
 ('utrecht', 'Utrecht', 'dom', (19.4, 28.6), '[WRITE 1–2 SENTENCES: why Utrecht.]'),
 ('mum', 'Mum & me', 'frame', (70.6, 22.8), '[WRITE 1–2 SENTENCES: the photo.]'),
 ('boyfriend', 'Boyfriend', 'boyfriend', (15.6, 67.0), '[WRITE 1–2 SENTENCES: your boyfriend.]'),
]
home_anim = ('<div class="anim cat cat-w" aria-hidden="true"></div><div class="anim cat cat-j" aria-hidden="true"></div><div class="anim dog" aria-hidden="true"></div><div class="anim vinyl" id="vinyl" aria-hidden="true"></div>'
             '<span class="note n1" aria-hidden="true">♪</span><span class="note n2" aria-hidden="true">♫</span>')
home_items = [(k, l, ic, hs, tx('home.' + k, t)) for k, l, ic, hs, t in home_items]
home_body = room(home_items, 'Home sweet home · Utrecht', 'home', HOME, 'world-home.png',
  'Pixel-art living room: a window with the Dom tower, a guitar, a record player, a film camera, a big framed photo of my mum and me, a sofa with my boyfriend and the black cat, a sewing machine, lots of plants and the red dog on the rug.',
  home_anim, tx('bubble.home', 'Hi! By day I\'m a Sr. Product UX Designer at IKEA. Alongside that I\'m studying climate psychology and behaviour. Click the green dots to get to know me better.'),
  'About me', pill('↓ Out to the street', 'index.html?from=home', 50, 91.5), extras={'records': SPIN})
open('../room-home.html', 'w').write(page('Home', home_body, HOME))

# Klimhal
KLIM = dict(
    w=320, h=224, bubble='right',
    # The art (assets/world-klimhal.png) comes from the design system: wall down to y 128, blue mats below.
    # The climber and belayer are drawn on top of it; [104, 138, 20, 14] is the belayer.
    spawns={'default': [152, 176, 'up'], 'start': [148, 140, 'down']},
    solid=[[0, 0, 320, 129], [208, 118, 22, 15], [104, 138, 20, 14], [20, 160, 65, 30], [224, 184, 19, 17], [268, 176, 47, 48]],
    doors=[[134, 214, 52, 10, 'index.html?from=klimhal']],
)
klim_items = [
 ('routes', 'Routes', 'routes', (87.5, 48.2), '[WRITE 1–2 SENTENCES: what you like about climbing.]'),
 ('friend', 'Friend', 'friend', (68.4, 58.5), '[WRITE 1–2 SENTENCES: who you climb with.]'),
 ('climbers', 'Climbing buddies', 'climbers', (40.6, 37.1), '[WRITE 1–2 SENTENCES: the two friends on the green route, who climbs and who belays.]'),
 ('gear', 'Gear', 'sneaker', (16.2, 79.0), '[WRITE 1–2 SENTENCES: shoes, harness, the bag.]'),
 ('chalk', 'Chalk', 'chalk', (72.8, 88.8), '[WRITE 1–2 SENTENCES: the chalk, the ritual.]'),
 ('outdoors', 'Outdoors', 'outdoors', (8.4, 47.8), '[WRITE 1–2 SENTENCES: climbing and being outside.]'),
]
klim_items = [(k, l, ic, hs, tx('klimhal.' + k, t)) for k, l, ic, hs, t in klim_items]
klim_body = room(klim_items, 'Klimhal', 'klimhal', KLIM, 'world-klimhal.png',
  'Pixel-art climbing hall: a wall with coloured holds and volumes, an outdoors poster, a climber in a pink shirt on the green route with her belayer below, my friend with a ponytail at the foot of the wall, a table with climbing shoes, a chalk bucket and a big plant on the blue mats.',
  '', tx('bubble.klimhal', 'Welcome to the climbing hall! This is where I switch off. Click the green dots to see what I get up to here.'),
  'Off the clock', pill('↓ Out to the street', 'index.html?from=klimhal', 50, 91.5))
open('../room-klimhal.html', 'w').write(page('Klimhal', klim_body, KLIM))

# ---------------------------------------------------------------- Case rooms (work)
# Each case room: the art from the design system (Nicky removed), a quest log in the side panel and one green
# dot per quest-log field. All texts live in CASES below; [WRITE: …] and [YEAR] are placeholders.
# My role sits right under the title; The result closes the case.
FIELDS = [('role', 'My role'), ('brief', 'The brief'), ('goal', 'The goal'), ('process', 'The process'), ('challenge', 'The challenge'), ('result', 'The result')]
RESULT = '[WRITE: the result]'
# A colleague's quote under a case: their face (cut from the room art, assets/avatar-*.png), their name and what they say.
# Excel IDs case.<id>.quote and case.<id>.quote_name. A case with no quote text shows no quote card.
QUOTE = '[WRITE: what this colleague says about working with you]'
QUOTE_NAME = '[NAME]'
CASES = {
 'ikea': dict(
    window='IKEA', back='work.html?from=ikea', img='room-ikea.png', w=288, h=208,
    alt='Pixel-art IKEA showroom: a sofa on a rug, a side table, a colourful collection display with a shopper next to it, shoppers in the aisle, someone sitting in the membership corner and the entrance doors with yellow arrows on the floor.',
    bubble='This is where I work now. Click a green dot to open one of my projects here.',
    # Three cases at IKEA (where I work): tabs above the quest log. Excel IDs: case.ikea1.*, case.ikea2.*, case.ikea3.*
    # Names, one-liners and role tags for the list view come from the concepts canvas (WorkList).
    projects=[dict(kicker='[WRITE: kind of project]', name=name, role='Sr. Product UX Designer', company='IKEA', year='[YEAR]',
                   text=dict(brief='[WRITE: the brief]', goal='[WRITE: the goal]', process='[WRITE: the process]', challenge='[WRITE: what made it hard]'),
                   line=line, tags=tags, org='IKEA', featured=(i == 0), draft=(i > 0),
                   avatar=avatar, quote=QUOTE, quote_name=QUOTE_NAME)
              for i, (name, line, tags, avatar) in enumerate([
                  ('Sofa (self)repair', 'Linked to my studies in climate psychology and behaviour. [WRITE 1 SENTENCE: the problem and what happened.]', ['Behaviour design'], 'avatar-ikea-sofa.png'),
                  ('Collections takeover', '[WRITE 1 SENTENCE, or remove this department.]', ['Product design'], 'avatar-ikea-collections.png'),
                  ('Membership space', '[WRITE 1 SENTENCE about the membership space.]', ['Product design'], 'avatar-ikea-membership.png')])],
    # The colleague by the plant stands on her own: she has her own dot, and her quote is about me, not about one case.
    # Excel IDs colleague.ikea.quote and colleague.ikea.name.
    lone=dict(avatar='avatar-ikea-plant.png', hot=(18.1, 87.0), quote='[WRITE: what this colleague says about you]', quote_name=QUOTE_NAME),
    # Collections (the display in the middle) moved 12 art px to the right; the shopper by it stands where the
    # man in the orange shirt stood, he now sits in the membership corner. The shelf with lamps and the plant are gone.
    # One dot per case, in the order of projects: the sofa, Collections (the display), the membership corner.
    case_hot=[(14.6, 59.0), (52.4, 52.4), (83.3, 88.5)],
    world=dict(spawns={'default': [133, 150, 'up']},
               solid=[[0, 0, 288, 54], [4, 60, 64, 38], [70, 58, 21, 34], [78, 118, 18, 12], [120, 58, 62, 52], [186, 108, 18, 12],
                      [42, 170, 22, 12], [0, 165, 47, 43], [196, 134, 89, 67]],
               doors=[[116, 196, 58, 12, 'work.html?from=ikea']])),
 'adidas': dict(
    window='adidas store', back='work.html?from=adidas', img='room-adidas.png', w=320, h=224,
    alt='Pixel-art sneaker store: a wall of sneakers, clothes racks, a table with shoes, a shop assistant at the counter and a big plant.',
    bubble='Welcome to the sneaker store! Click the green dots to read about this project.',
    kicker='[WRITE: kind of project]', name='B2B store experience',
    role='[WRITE: role]', company='[WRITE: company]', year='2018',
    text=dict(brief='[WRITE: the brief]', goal='[WRITE: the goal]', process='[WRITE: the process]', challenge='[WRITE: what made it hard]'),
    line='[WRITE 1 SENTENCE: the B2B project, with the sales rep in the store as the audience.]', tags=['UX design'], org='adidas',
    avatar='avatar-adidas.png',
    hot=dict(brief=(34.4, 32.6), goal=(48.8, 55.8), role=(83.1, 55.4), process=(17.5, 67.9), challenge=(79.7, 34.4), result=(90.6, 88.0)),
    world=dict(spawns={'default': [148, 176, 'up']},
               solid=[[0, 0, 320, 88], [112, 120, 89, 22], [20, 140, 72, 22], [228, 110, 77, 42], [270, 190, 45, 34]],
               doors=[[134, 214, 54, 10, 'work.html?from=adidas']])),
 'swifty': dict(
    window='Swifty bar', back='work.html?from=swifty', img='room-swifty.png', w=320, h=224,
    alt='Pixel-art bar: a bartender behind a long bar with bottles, bar stools, people at small round tables and a phone on one of the tables.',
    bubble='Welcome to the bar! Click the green dots to read about this project.',
    kicker='New app', name='Swifty',
    role='UX Designer', company='Media.Monks', year='2020',
    line='A bar app to order food and drinks, with loyalty points to collect and spend. Built from scratch in six weeks.',
    tags=['UX design', 'User journeys', 'Design system', 'Prototyping'], org='Heineken · Media.Monks', client='Heineken',
    text=dict(brief='An app that lets customers order food and drinks at the bar, with a loyalty system.', goal='[WRITE: the goal]',
              process='[WRITE: the process]', challenge='[WRITE: what made it hard]'),
    # The table by the door is gone (it was in the way out); its phone now lies by the table on the right.
    avatar='avatar-swifty.png',
    hot=dict(brief=(81.6, 88.0), goal=(31.2, 12.5), role=(46.9, 29.0), process=(37.5, 54.9), challenge=(71.2, 54.9), result=(93.4, 71.4)),
    world=dict(spawns={'default': [104, 174, 'up']},
               solid=[[0, 0, 320, 92], [76, 104, 13, 9], [148, 104, 13, 9], [184, 104, 13, 9], [110, 114, 20, 10], [218, 114, 20, 10],
                      [6, 140, 47, 14], [252, 140, 31, 19], [290, 150, 20, 10], [78, 194, 20, 10], [40, 195, 31, 14],
                      [236, 199, 31, 14]],
               doors=[[134, 214, 54, 10, 'work.html?from=swifty']])),
}

def project_texts(key, c):
    """The quest logs of a room: one per project, with the Excel texts applied. IDs: case.<room>.* or case.<room><n>.*"""
    many = 'projects' in c
    out = []
    for n, pr in enumerate(c['projects'] if many else [c], 1):
        pid = f'{key}{n}' if many else key
        pr = dict(pr, text=dict(pr['text']))
        pr['text'].setdefault('result', RESULT)
        for f in ('kicker', 'name', 'role', 'company', 'year', 'line', 'client', 'quote', 'quote_name', 'images'): pr[f] = tx(f'case.{pid}.{f}', pr.get(f, ''))
        for f in pr['text']: pr['text'][f] = tx(f'case.{pid}.{f}', pr['text'][f])
        out.append(pr)
    return out

def quote_card(avatar, text, name, attrs=''):
    """A colleague's quote: a white card under the quest log, their face on a tinted tile, the quote and their name."""
    if not text: return ''
    who = f'<figcaption>{name}</figcaption>' if name else ''
    return (f'<figure class="quote"{attrs}><span class="quote-ava"><img src="assets/{avatar}" alt=""></span>'
            f'<span class="quote-body"><blockquote>“{text}”</blockquote>{who}</span></figure>')

def case_media(images):
    """Pictures and gifs in a case: Excel case.<id>.images, one per line, 'file.gif | what it shows'. Files go in assets/cases/."""
    out = ''
    for line in html.unescape(images).splitlines():
        if not line.strip(): continue
        f, _, alt = line.partition('|'); f = f.strip()
        if not os.path.exists(f'../assets/cases/{f}'):
            print(f'  ! assets/cases/{f} not found, left out'); continue
        out += f'<img src="assets/cases/{html.escape(f)}" alt="{html.escape(alt.strip())}" loading="lazy">'
    return f'<div class="qmedia">{out}</div>' if out else ''

def case_room(key, c):
    projects = project_texts(key, c)
    world = dict(w=c['w'], h=c['h'], bubble='right', **c['world'])
    if 'case_hot' in c:   # a room with several cases: a dot per case opens that case (data-case = its number)
        inner = ''.join(hot(f'case-{n+1}', pr['name'] if '[' not in pr['name'] else f'Case {n+1}', *c['case_hot'][n], n == 0)
                        .replace('<button class="hot', f'<button data-case="{n+1}" class="hot', 1) for n, pr in enumerate(projects))
    else:
        inner = ''.join(hot(k, l, c['hot'][k][0], c['hot'][k][1]) for i, (k, l) in enumerate(FIELDS))
    lone = c.get('lone')
    if lone:   # the colleague on her own: her dot shows her quote (data-quote)
        lone_name = tx(f'colleague.{key}.name', lone['quote_name'])
        inner += hot('colleague', lone_name if '[' not in lone_name else 'Colleague', *lone['hot']).replace('<button class="hot', '<button data-quote="lone" class="hot', 1)
    inner += pill('↓ Back outside', c['back'], 50, 93) + f'<div class="bubble" id="bubble">{tx("bubble." + key, c["bubble"])}</div>'
    st = stage(c['img'], c['alt'], inner, c['w'], c['h'])
    def value(pr, k):
        return f'<strong>{pr["role"]}</strong> at {pr["company"]} · {pr["year"]}' if k == 'role' else pr['text'][k]
    logs = ''
    for n, pr in enumerate(projects):
        fields = ''.join(f'<div class="qf" data-item="{k}"><b>{l}</b><p>{value(pr, k)}</p></div>' for k, l in FIELDS)
        client = f' data-client="{pr["client"]}"' if pr.get('client') else ''
        logs += (f'<div class="quest" id="quest-{key}-{n+1}"{client}{" hidden" if n else ""}><span class="k">{pr["kicker"]}</span>'
                 f'<strong class="t">{pr["name"]}</strong>{fields}{case_media(pr.get("images", ""))}</div>')
        if pr.get('avatar'):
            logs += quote_card(pr['avatar'], pr['quote'], pr['quote_name'], f' data-for="quest-{key}-{n+1}"{" hidden" if n else ""}')
    if lone:
        logs += quote_card(lone['avatar'], tx(f'colleague.{key}.quote', lone['quote']), tx(f'colleague.{key}.name', lone['quote_name']), ' data-lone hidden')
    tabs = ''
    if len(projects) > 1:   # one tab per case; the label is the project name once it is filled in
        tabs = '<div class="qtabs" role="tablist" aria-label="Cases">' + ''.join(
            f'<button type="button" role="tab" class="qtab" aria-controls="quest-{key}-{n+1}" aria-selected="{"true" if n == 0 else "false"}">'
            f'{pr["name"] if "[" not in pr["name"] else f"Case {n+1}"}</button>' for n, pr in enumerate(projects)) + '</div>'
    aside = (f'<aside class="aside" aria-label="Quest log"><div class="aside-in"><div class="aside-head"><h2>Quest log</h2></div>'
             f'{tabs}{logs}</div></aside>')
    return window(c['window'], 'Work', st, aside, True), world

for key, c in CASES.items():
    body, world = case_room(key, c)
    open(f'../room-{key}.html', 'w').write(page(c['window'], body, world))

# ---------------------------------------------------------------- List views (About / Work)
# The quick version of the game, for people who would rather read than walk: from the concepts canvas (AboutList, WorkList).
# Every row opens its room. Texts come from the same lists as the rooms (and so from the Excel sheet).
TINTS = ['var(--green-tint)', 'var(--peach)', 'var(--rose)', 'var(--sky)']
def tag(t, bg='var(--green-tint)'):
    return f'<span class="tag" style="background:{bg}">{t}</span>'
def section(title, inner):
    return f'<section class="list-sec"><div class="list-head"><h2>{title}</h2></div>{inner}</section>'

about_rows = ''.join(
    f'<a class="row item" href="room-home.html"><span class="ico" style="background:{TINTS[i % 4]}"><img src="assets/icon-{ic}.png" alt=""></span>'
    f'<span class="txt"><strong>{l}</strong><span>{t}</span></span></a>' for i, (k, l, ic, hs, t) in enumerate(home_items))
klim_row = (f'<a class="row place" href="room-klimhal.html"><span class="name"><strong>Climbing at the Klimhal</strong><span>Utrecht</span></span>'
            f'<span class="line">{tx("list.klimhal", "[WRITE 1–2 SENTENCES: what you like about climbing, and who you climb with.]")}</span>'
            f'<span class="tags">{"".join(tag(l, "var(--peach)") for k, l, ic, hs, t in klim_items)}</span><span class="go">Open room →</span></a>')
about_body = (f'<p class="list-intro">{tx("list.about.intro", "Hi! By day I&#39;m a Sr. Product UX Designer at IKEA. Alongside that I&#39;m studying climate psychology and behaviour. This is the quick version of who I am off the clock. Prefer to explore? Switch back to my home with the map icon.")}</p>'
              + section('Off the clock', f'<div class="items">{about_rows}</div>')
              + section('Out and about', f'<div class="rows">{klim_row}</div>'))
open('../about-list.html', 'w').write(page('About', window('Home sweet home · list view', 'About', about_body, '', view='list')))

def case_row(href, year, name, org, line, tags, featured=False, draft=False):
    feat = ' <span class="tag" style="background:var(--focus)">Featured</span>' if featured else ''
    return (f'<a class="row case{" draft" if draft else ""}" href="{href}"><span class="year">{year}</span>'
            f'<span class="name"><strong>{name}{feat}</strong><span>{org}</span></span><span class="line">{line}</span>'
            f'<span class="tags">{"".join(tag(t) for t in tags)}</span><span class="go">Open room →</span></a>')
COLS = '<div class="cols" aria-hidden="true"><span class="year">Year</span><span class="name">Case</span><span class="line">In one line</span><span class="tags">My role</span><span class="go"></span></div>'
ikea_rows = ''.join(case_row(f'room-ikea.html#case-{n}', pr['year'], pr['name'], pr['org'], pr['line'], pr['tags'], pr['featured'], pr['draft'])
                    for n, pr in enumerate(project_texts('ikea', CASES['ikea']), 1))
def single(key):
    pr = project_texts(key, CASES[key])[0]
    return case_row(f'room-{key}.html', pr['year'], pr['name'], pr['org'], pr['line'], pr['tags'])
before = (case_row('room-pledge.html', '2021', 'The Climate Pledge', 'Climate Pledge',
                   tx('list.pledge', 'Getting as many brands as possible to reach their climate goals ten years ahead of the Paris goals.'), ['UX design'])
          + single('swifty')
          + case_row('room-case.html', '2019', 'McLaren platform redesign', 'McLaren',
                     tx('list.mclaren', 'Redesigning cars.mclaren.com for both visitors and CMS authors.'), ['UX design'])
          + single('adidas'))
skill_rows = ''.join(f'<div class="skill"><span class="ico" style="background:{bg}"><img src="assets/icon-{ic}.png" alt=""></span><span><strong>{t}</strong><small>{d}</small></span></div>'
                     for ic, bg, t, d in skills)
work_body = (f'<p class="list-intro">{tx("list.work.intro", "The quick version of my work, newest first. Every row opens its room in the game, if you would like the full story. Prefer to explore? Switch back to the world with the map icon.")}</p>'
             + section('At IKEA', f'<div class="rows">{COLS}{ikea_rows}</div>')
             + section('Before IKEA', f'<div class="rows">{COLS}{before}</div>')
             + section('In my backpack', f'<div class="skills">{skill_rows}</div>'))
open('../work-list.html', 'w').write(page('Work', window('Work · list view', 'Work', work_body, '', view='list')))

# ---------------------------------------------------------------- Room placeholders (next step)
rooms = {'case': ('McLaren showroom', 'work.html?from=mclaren'), 'pledge': ('The Climate Pledge', 'work.html?from=pledge')}
for key, (name, back) in rooms.items():
    stub = f'<div class="stub"><h2>{name}</h2><p>This room is the next one to be built.</p><a class="btn" href="{back}">↓ Back outside</a></div>'
    open(f'../room-{key}.html', 'w').write(page(name, window(name, 'Work', stub, '')))
for f, t in (('about.html', 'room-home.html'), ('project.html', 'index.html')):
    open(f'../{f}', 'w').write(f'<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url={t}"><a href="{t}">Continue</a>')

# ---------------------------------------------------------------- Cache busting
# Every image, stylesheet and script gets ?v=<first 8 characters of its content hash>. A changed file gets a new
# address, so browsers (and visitors who came before) always load the new version; unchanged files stay cached.
import glob, hashlib, re
def stamp(path):
    with open('../' + path, 'rb') as fh: return path + '?v=' + hashlib.sha1(fh.read()).hexdigest()[:8]
# First the images inside the stylesheet, so the stylesheet's own stamp includes them.
css = open('../css/site.css').read()
css = re.sub(r'url\(\.\./(assets/[^)?]+)(\?v=\w+)?\)', lambda m: 'url(../' + stamp(m.group(1)) + ')', css)
open('../css/site.css', 'w').write(css)
for f in glob.glob('../*.html'):
    s = open(f).read()
    s = re.sub(r'(src|href)="((?:assets|css|js)/[^"?]+)(\?v=\w+)?"', lambda m: f'{m.group(1)}="{stamp(m.group(2))}"', s)
    open(f, 'w').write(s)
print('built')
