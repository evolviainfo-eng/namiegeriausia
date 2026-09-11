# -*- coding: utf-8 -*-
"""Generate index + project pages for NAMIE geriausia."""
import json, os, glob, datetime
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = json.load(open(os.path.join(ROOT, 'assets/projects.json')))
DOMAIN = 'https://namiegeriausia.lt'

import re
def widths_for(name):
    fs = glob.glob(os.path.join(ROOT, f'img/{name}-*.webp'))
    ws = []
    for f in fs:
        m = re.fullmatch(re.escape(name) + r'-(\d+)\.webp', os.path.basename(f))
        if m: ws.append(int(m.group(1)))
    return sorted(ws)

def srcset(name):
    return ', '.join(f'/img/{name}-{w}.webp {w}w' for w in widths_for(name))

from PIL import Image as _Im
import io, base64
_dim_cache = {}
def dims(name):
    if name not in _dim_cache:
        ws = widths_for(name)
        with _Im.open(os.path.join(ROOT, f'img/{name}-{ws[-1]}.webp')) as im:
            _dim_cache[name] = im.size
    return _dim_cache[name]

_lqip_cache = {}
def lqip(name):
    """20px-wide inline webp: blur-up placeholder painted as the img background."""
    if name not in _lqip_cache:
        ws = widths_for(name)
        with _Im.open(os.path.join(ROOT, f'img/{name}-{ws[0]}.webp')) as im:
            im = im.convert('RGB')
            t = im.resize((20, max(1, round(im.height * 20 / im.width))), _Im.LANCZOS)
            b = io.BytesIO(); t.save(b, 'WEBP', quality=32, method=6)
            _lqip_cache[name] = base64.b64encode(b.getvalue()).decode()
    return _lqip_cache[name]

def img_tag(name, alt, sizes, cls='', lazy=True, ar=None):
    ws = widths_for(name)
    if not ws:
        raise SystemExit(f'missing image {name}')
    mid = ws[min(1, len(ws) - 1)]
    w, h = dims(name)
    l = ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"'
    styles = []
    if ar: styles.append(f'aspect-ratio:{ar}')
    if lazy:
        styles.append(f"background-image:url(data:image/webp;base64,{lqip(name)});background-size:cover;background-position:center")
    a = f' style="{";".join(styles)}"' if styles else ''
    c = f' class="{cls}"' if cls else ''
    return (f'<img{c} src="/img/{name}-{mid}.webp" srcset="{srcset(name)}" '
            f'sizes="{sizes}" alt="{alt}"{l}{a} width="{w}" height="{h}">')

HEAD = '''<!DOCTYPE html>
<html lang="lt">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<meta name="theme-color" content="#F4F0EB">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{domain}/og.jpg">
<meta property="og:locale" content="lt_LT">
<link rel="icon" type="image/png" sizes="32x32" href="/img/mark-32.png">
<link rel="apple-touch-icon" href="/img/mark-180.png">
<link rel="preload" as="font" type="font/woff2" href="/assets/fonts/outfit-300-latin.woff2" crossorigin>
<link rel="preload" as="font" type="font/woff2" href="/assets/fonts/outfit-300-latin-ext.woff2" crossorigin>
{preload}
<link rel="stylesheet" href="/css/site.css">
{schema}
</head>
<body>
<a class="skip" href="#turinys">Pereiti prie turinio</a>
<header class="nav">
  <div class="wrap">
    <a class="brand" href="/" aria-label="NAMIE geriausia, į pradžią">
      <img class="mk" src="/img/logo-mark.png" alt="" width="354" height="347">
      <span class="bw">
        <img src="/img/word-namie.png" alt="NAMIE" width="808" height="116">
        <img src="/img/word-geriausia.png" alt="geriausia" width="803" height="64">
      </span>
    </a>
    <nav aria-label="Pagrindinė navigacija">
      <ul>
        <li class="hm"><a class="tlink" href="/#projektai">Projektai</a></li>
        <li class="hm"><a class="tlink" href="/#paslaugos">Paslaugos</a></li>
        <li class="hm"><a class="tlink" href="/#kontaktai">Kontaktai</a></li>
        <li><a class="call" href="tel:+37068020901">+370 680 20901</a></li>
      </ul>
    </nav>
  </div>
</header>
<main id="turinys">
'''

FOOT = '''</main>
<footer class="foot">
  <div class="wrap">
    <div class="fg">
      <div class="fl"><img src="/img/logo-lockup.png" alt="NAMIE geriausia" width="808" height="644"></div>
      <div class="fc">
        Interjero dizaino studija<br>
        Vilniaus g. 18, Senamiestis, Vilnius<br>
        <a href="tel:+37068020901">+370 680 20901</a><br>
        <a href="mailto:brigita@namiegeriausia.lt">brigita@namiegeriausia.lt</a>
      </div>
      <nav class="fn" aria-label="Papildoma navigacija">
        <ul>
          <li><a class="tlink" href="/#projektai">Projektai</a></li>
          <li><a class="tlink" href="/#paslaugos">Paslaugos</a></li>
          <li><a class="tlink" href="https://www.instagram.com/namiegeriausia/" rel="noopener" target="_blank">Instagram</a></li>
          <li><a class="tlink" href="https://www.facebook.com/namiegeriausia/" rel="noopener" target="_blank">Facebook</a></li>
        </ul>
      </nav>
    </div>
    <div class="legal">
      <span>© 2026 NAMIE geriausia</span>
    </div>
  </div>
</footer>
<script src="/js/site.js" defer></script>
</body>
</html>
'''

# ---------------------------------------------------------------- index
biz_schema = '''<script type="application/ld+json">
{"@context":"https://schema.org","@type":"ProfessionalService",
"name":"NAMIE geriausia","description":"Interjero dizaino studija Vilniuje: projektavimas, 3D vizualizacijos, autorinė priežiūra ir pilnas įrengimas.",
"url":"https://namiegeriausia.lt","telephone":"+37068020901","email":"brigita@namiegeriausia.lt",
"founder":{"@type":"Person","name":"Brigita Dikevičė"},
"address":{"@type":"PostalAddress","streetAddress":"Vilniaus g. 18","addressLocality":"Vilnius","postalCode":"LT-01402","addressCountry":"LT"},
"sameAs":["https://www.instagram.com/namiegeriausia/","https://www.facebook.com/namiegeriausia/"]}
</script>'''

faq_items = [
    ("Nuo ko viskas prasideda?",
     "Nuo konsultacijos. Ji gali vykti ir objekte. Analizuojame erdvės architektūrą bei inžineriją, o svarbiausia, susipažįstame: gerai suprasti klientą ne mažiau svarbu nei suprasti patalpas."),
    ("Kas įeina į techninį projektą?",
     "Dešimt brėžinių grupių: nuo pertvarų ir durų angų plano iki plytelių klijavimo išklotinių. Pagal juos dirba apdailos meistrai ir baldininkai. Visas sąrašas pateiktas paslaugų skiltyje."),
    ("Kiek užtrunka parengti projektą?",
     "Techninių brėžinių paketas „Start“ parengiamas per 2–3 savaites. Pilno projekto su vizualizacijomis terminas priklauso nuo būsto ploto ir sprendimų apimties. Jį aptariame konsultacijos metu."),
    ("Ar padedate ir įrengiant?",
     "Taip, tai mūsų stiprybė. Autorinė priežiūra ir pilnas įrengimas: procesų valdymas, medžiagų užsakymas laiku, baldų gamybos organizavimas, atsakymai į meistrų klausimus ir netikėtų situacijų sprendimas iki pat raktų."),
]
faq_schema = json.dumps({
    "@context": "https://schema.org", "@type": "FAQPage",
    "mainEntity": [{"@type": "Question", "name": q,
                    "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq_items]
}, ensure_ascii=False)

hero_preload = '''<link rel="preload" as="image" media="(min-width:1025px)" imagesrcset="/img/hero-desk-1400.webp 1400w, /img/hero-desk-1900.webp 1900w, /img/hero-desk-2600.webp 2600w" imagesizes="100vw">
<link rel="preload" as="image" media="(max-width:600px)" imagesrcset="/img/hero-mob-760.webp 760w, /img/hero-mob-1100.webp 1100w" imagesizes="100vw">'''

covers_meta = {
    'misko-namai':    'Vilnius · pilnas įrengimas',
    'cashmere':       'Butas · pilnas įrengimas',
    'slaitines-lubos':'Butas · projektas ir realizacija',
    'mazas-butas':    'Butas · projektas ir realizacija',
    'azuolo-namai':   'Namas · pilnas įrengimas',
    'juodi-akcentai': 'Namas · pilnas įrengimas',
    'atostogu-namai': 'Lietuvos pajūris',
    'beige-namai':    'Butas · projektas ir realizacija',
}

def index_html():
    cards = []
    for n, p in enumerate(P):
        s = p['slug']
        cards.append(f'''<a class="pcard" href="/projektai/{s}/" aria-label="{p['title']}, atidaryti projekto puslapį">
  <figure>{img_tag('cover-' + s, p['title'] + ', įgyvendinto interjero fragmentas', '(max-width:760px) 92vw, 46vw', lazy=(n > 1))}</figure>
  <span class="cap"><span><span class="pt">{p['title']}</span><br><span class="pm">{covers_meta[s]}</span></span><span class="go">Žiūrėti projektą →</span></span>
</a>''')
    cards = '\n'.join(cards)

    hero = f'''<section class="hero plx">
  <picture>
    <source media="(max-width:600px)" srcset="/img/hero-mob-760.webp 760w, /img/hero-mob-1100.webp 1100w" sizes="100vw">
    <source media="(max-width:1024px)" srcset="/img/hero-tab-1000.webp 1000w, /img/hero-tab-1400.webp 1400w" sizes="100vw">
    <img src="/img/hero-desk-1900.webp" srcset="/img/hero-desk-1400.webp 1400w, /img/hero-desk-1900.webp 1900w, /img/hero-desk-2600.webp 2600w" sizes="100vw" alt="Miško namai: svetainė su žalia sofa ir miško vaizdu pro langus" fetchpriority="high" width="2600" height="1463">
  </picture>
  <div class="hc wrap">
    <h1><span class="hl"><span>Nuo idėjos iki</span></span><span class="hl"><span>įrengtų namų.</span></span></h1>
    <p class="hsub">Interjero dizaino studija Vilniuje. Projektavimas, vizualizacijos, autorinė priežiūra ir pilnas įrengimas. Viskas vienose rankose.</p>
    <div class="hcta">
      <a class="btn" href="#kontaktai">Užsakyti konsultaciją</a>
      <a class="tlink" href="#projektai" style="color:var(--paper)">Žiūrėti projektus</a>
    </div>
  </div>
  <p class="hloc">Miško namai · Vilnius<br>įgyvendintas projektas</p>
</section>'''

    mani = '''<section class="mani" aria-label="Studijos filosofija">
  <div class="wrap mg"><figure class="mq">
    <blockquote><p>„Prabanga – tai ne marmurinės plytelės ar auksinės rankenėlės. Tai kokybiškai apgalvoti sprendimai, kurie suteikia visapusišką komfortą. Įsiklausymas, supratimas ir tinkamiausio sprendimo atradimas. Prabanga – tai jausmas, kai sugrįžus supranti: visur gerai, bet <strong>NAMIE GERIAUSIA</strong>.“</p></blockquote>
    <figcaption>Brigita Dikevičė, studijos įkūrėja</figcaption>
  </figure></div>
</section>'''

    proj = f'''<section class="sec" id="projektai">
  <div class="wrap">
    <h2>Interjerai, kuriuose jau gyvenama</h2>
    <div class="pgrid">{cards}</div>
  </div>
</section>'''

    serv = '''<section class="sec" id="paslaugos">
  <div class="wrap">
    <h2>Viskas vienose rankose</h2>
    <p class="ssub">Interjero dizaineris nėra tik gražių daiktų ir spalvų parinkėjas. Tai procesas, kuriame kūryba kasdien susitinka su techninėmis žiniomis, vadyba ir dėmesiu detalėms.</p>
    <div class="serv">
      <div class="srow"><h3>Interjero projektavimas</h3><p>Analizė ir pažinimas, išplanavimas, techniniai brėžiniai. Svarbi kiekviena detalė: nuo sienos atspalvio ir grindų krypties iki jungiklio vietos ir kelių milimetrų baldo brėžinyje.</p></div>
      <div class="srow"><h3>3D vizualizacijos</h3><p>Fotorealistiški erdvių vaizdai, kuriais patikrinami sprendimai dar prieš perkant medžiagas. Ne kartą rezultatas pranoksta vizualizaciją.</p></div>
      <div class="srow"><h3>Autorinė priežiūra</h3><p>Lankomės objekte, atsakome į meistrų klausimus, laiku užsakome apdailos medžiagas ir sprendžiame netikėtas situacijas, kad „ne, negaliu“ virstų „gerai, padarom“.</p></div>
      <div class="srow"><h3>Pilnas įrengimas</h3><p>Nuo projekto iki raktų: apdailos ir baldininkų darbų koordinavimas, korpusinių baldų gamybos organizavimas, susitikimai salonuose ir nuolatinis ryšys su klientais.</p></div>
    </div>
    <div class="spec">
      <div class="sh">
        <h3>Techninis projektas, pagal kurį dirba meistrai</h3>
        <p>Brėžinių paketas „Start“ parengiamas per 2–3 savaites. Jis būtinas, jei norite įsirengti kokybiškai ir be klaidų, net ir be pilno dizaino projekto.</p>
      </div>
      <ul>
        <li>Pertvarų ir durų angų planas</li>
        <li>Detalusis baldų išdėstymo planas</li>
        <li>Santechnikos pririšimo planas</li>
        <li>Šviestuvų ir apšvietimo valdymo planas</li>
        <li>Lubų planas</li>
        <li>Difuzorių pririšimo planas</li>
        <li>Kištukinių lizdų planas</li>
        <li>Sienų dengimo planas</li>
        <li>Grindų klojimo planas</li>
        <li>Plytelių klijavimo išklotinės</li>
      </ul>
    </div>
  </div>
</section>'''

    proof = '''<section class="sec" aria-label="Atsiliepimai ir spauda">
  <div class="wrap proof">
    <div class="ph">
      <h2>Žinutės, kurios ateina projektų eigoje</h2>
      <div class="press">
        <h3>Spauda ir eteris</h3>
        <ul>
          <li>LRT <span>· pokalbis apie interjerą</span></li>
          <li>TV3 <span>· reportažai iš įgyvendintų projektų</span></li>
          <li>„Namas ir aš“ <span>· projekto publikacija</span></li>
          <li>„Mano namai“ <span>· projekto publikacija</span></li>
          <li>Salone del Mobile <span>· Milanas, 2025</span></li>
        </ul>
      </div>
    </div>
    <div class="quotes">
      <blockquote class="qt"><p>„Supratau, kaip reikia planuoti apšvietimą, kaip derinti spalvas, kaip meistrams pateikti brėžinius. Patarimai labai naudingi ir vertingi – meistrai dažniausiai pasako tik iš techninės pusės, o dizaineris pagalvoja ir apie grožį.“<br></p><footer>Gerda, vieša rekomendacija „Facebook“</footer></blockquote>
      <blockquote class="qt"><p>„Ačiū už kantrybę ir už tai, kad sukūrei mums namus. Mes jau nuotraukas žiūrim ir netikim, kaip dabar gražu, net nesitiki, kad sunkiausias laikotarpis praeitas ir jau matosi toks nerealus rezultatas.“</p><footer>Klientės žinutė įrengimo eigoje</footer></blockquote>
      <blockquote class="qt"><p>„Šį kartą nejaučiu jokios įtampos, nepergyvenu, nes žinau, kad patekome į profesionalias rankas.“</p><footer>Klientės laiškas po projektavimo etapo</footer></blockquote>
    </div>
  </div>
</section>'''

    about = f'''<section class="sec" id="apie">
  <div class="wrap about">
    <figure>{img_tag('brigita', 'Interjero dizainerė Brigita Dikevičė', '(max-width:900px) 92vw, 42vw')}</figure>
    <div class="at">
      <h2>Dizainerė, kuri lieka iki raktų</h2>
      <p class="role">Brigita Dikevičė · interjero dizainerė, studijos įkūrėja</p>
      <p>Studija NAMIE geriausia įsikūrusi Vilniaus senamiestyje, o projektai driekiasi nuo sostinės iki Lietuvos pajūrio. Dirbame su butais ir namais, kuriems reikia ne tik gražaus vaizdo, bet ir tiksliai suplanuotos kasdienybės.</p>
      <p>Geras interjeras prasideda ne nuo dizaino, o nuo kokybiškai parengto techninio projekto, ir baigiasi ne vizualizacija, o įrengtais namais. Todėl liekame šalia per visą įrengimą: nieko nepamiršti, niekur nesuklysti ir laiku pastebėti tai, ko galbūt nepastebi niekas kitas.</p>
      <p>„Gražus interjeras matomas nuotraukose, o geras interjeras – jaučiamas jame gyvenant.“</p>
    </div>
  </div>
</section>'''

    faq_html = '\n'.join(
        f'<details><summary>{q}</summary><div class="fa"><p>{a}</p></div></details>'
        for q, a in faq_items)

    contact = f'''<section class="sec" id="kontaktai">
  <div class="wrap">
    <div class="contact">
      <div class="ch">
        <h2>Pradėkime nuo pokalbio</h2>
        <p class="ssub">Papasakokite apie savo būstą. Atsakysime, kaip galėtume padėti, ir sutarsime konsultacijos laiką.</p>
        <ul class="cl">
          <li><span class="lbl">Telefonas</span><a class="ulink" href="tel:+37068020901">+370 680 20901</a></li>
          <li><span class="lbl">El. paštas</span><a class="ulink" href="mailto:brigita@namiegeriausia.lt">brigita@namiegeriausia.lt</a></li>
          <li><span class="lbl">Studija</span>Vilniaus g. 18, Senamiestis, Vilnius</li>
          <li><span class="lbl">Instagram</span><a class="ulink" href="https://www.instagram.com/namiegeriausia/" rel="noopener" target="_blank">@namiegeriausia</a></li>
        </ul>
      </div>
      <form class="cform" id="cf" novalidate>
        <div class="fr"><label for="cf-name">Vardas</label><input id="cf-name" name="name" type="text" autocomplete="name" required></div>
        <div class="fr"><label for="cf-tel">Telefonas arba el. paštas</label><input id="cf-tel" name="contact" type="text" autocomplete="tel" required></div>
        <div class="fr"><label for="cf-msg">Trumpai apie būstą: miestas, plotas, etapas</label><textarea id="cf-msg" name="message" rows="4"></textarea></div>
        <button class="btn" type="submit">Gauti konsultaciją</button>
        <p class="fmsg" id="cf-note" aria-live="polite"></p>
      </form>
    </div>
    <div class="faq">
      <h3>Dažniausi klausimai</h3>
      {faq_html}
    </div>
  </div>
</section>'''

    head = HEAD.format(
        title='NAMIE geriausia · Interjero dizainas ir pilnas įrengimas Vilniuje',
        desc='Interjero projektavimas, 3D vizualizacijos, autorinė priežiūra ir pilnas įrengimas. Nuo idėjos iki įrengtų namų. Studija Vilniaus senamiestyje.',
        canon=DOMAIN + '/', domain=DOMAIN, preload=hero_preload,
        schema=biz_schema + f'\n<script type="application/ld+json">{faq_schema}</script>')
    return head + hero + mani + proj + serv + proof + about + contact + ig_strip() + FOOT


# ------------------------------------------------------- instagram strip
def ig_strip():
    """Self-hosted strip built from data/ig-feed.json (refreshed by fetch_ig.py).
    Renders nothing at all if the feed file is missing, never a broken section."""
    fp = os.path.join(ROOT, 'data/ig-feed.json')
    if not os.path.exists(fp):
        return ''
    feed = json.load(open(fp, encoding='utf-8'))
    posts = feed.get('posts', [])
    if not posts:
        return ''

    MON = ['sausio', 'vasario', 'kovo', 'balandžio', 'gegužės', 'birželio', 'liepos',
           'rugpjūčio', 'rugsėjo', 'spalio', 'lapkričio', 'gruodžio']

    HEART = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
             'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
             '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8l1 1.1L12 21l7.8-7.5 1-1.1a5.5 5.5 0 0 0 0-7.8z"/></svg>')
    BUBBLE = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
              'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
              '<path d="M21 11.5a8.4 8.4 0 0 1-9 8.4 9.5 9.5 0 0 1-3.5-.7L3 21l1.9-5a8.1 8.1 0 0 1-.9-4.5 8.4 8.4 0 0 1 8.5-8 8.4 8.4 0 0 1 8.5 8z"/></svg>')
    SEND = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            '<path d="M22 2 11 13"/><path d="M22 2 15 22l-4-9-9-4 20-7z"/></svg>')

    def tile(p):
        vid = '<span class="igv" aria-hidden="true"></span>' if p.get('video') else ''
        d = datetime.datetime.utcfromtimestamp(p['ts']) if p.get('ts') else None
        date = f'{MON[d.month - 1]} {d.day} d.' if d else ''
        cap = escape(p.get('caption', ''))
        alt = cap[:110] if cap else 'Įrašas iš studijos kasdienybės'
        return (f'<a class="igt" href="{p["url"]}" target="_blank" rel="noopener noreferrer" '
                f'aria-label="Žiūrėti įrašą Instagrame: {alt}">'
                f'<span class="igim" style="background-image:url(data:image/webp;base64,{p["blur"]})">'
                # One fixed source, no srcset: with srcset the duplicate track
                # resolved to different variants and several tiles never picked a
                # source at all, drifting in as blur mush. 640px covers 300px @2x
                # and the duplicate tiles are pure cache hits. Not lazy either:
                # native lazy-loading does not fire for a transform-driven track.
                f'<img src="/img/ig-{p["code"]}-900.webp" alt="{alt}" '
                f'decoding="async" width="900" height="900">{vid}</span>'
                f'<span class="igb">'
                f'<span class="igacts" aria-hidden="true">{HEART}{BUBBLE}{SEND}</span>'
                f'<span class="igcap">{cap}</span>'
                f'<span class="igdate">{date}</span>'
                f'</span></a>')

    tiles = ''.join(tile(p) for p in posts)
    # the track is duplicated so the drift can loop seamlessly; the copy is
    # hidden from assistive tech and from the tab order
    dup = tiles.replace('<a class="igt" href', '<a class="igt" tabindex="-1" aria-hidden="true" href')
    return f'''<section class="sec igs" id="instagram">
  <div class="wrap igh">
    <h2>Kasdienybė iš studijos</h2>
    <a class="ulink" href="https://www.instagram.com/{feed['handle']}/" rel="noopener" target="_blank">@{feed['handle']}</a>
  </div>
  <div class="igmask">
    <div class="igwrap">
      <div class="igtrack">{tiles}{dup}</div>
    </div>
  </div>
</section>'''

# ------------------------------------------------------------ project pages
def project_html(p, nxt):
    s = p['slug']
    n_img = len(p['images'])
    names = [f'{s}-{i:02d}' for i in range(n_img)]
    parts = []
    parts.append(f'''<div class="wrap phead">
  <p class="crumb"><a class="back" href="/#projektai">← Visi projektai</a></p>
  <h1>{p['lead']}</h1>
  <p class="pmeta">{p['title']} · {p['meta']}</p>
  <p class="lead">{p['intro']}</p>
</div>''')
    # gallery flow with interleaved notes
    notes = list(p.get('notes', []))
    body = []
    i = 0
    pat = 0
    alt = f'{p["title"]}: įgyvendinto interjero fragmentas'
    def g(k, sizes):
        return img_tag(names[k], alt, sizes, lazy=(k > 2))
    # steady rhythm: note-row -> pair -> full -> pair -> (repeat)
    while i < n_img:
        rem = n_img - i
        step = pat % 4
        if step == 0 and notes:
            nt = notes.pop(0)
            body.append(f'<figure class="l8n">{g(i, "(max-width:760px) 92vw, 62vw")}</figure>')
            body.append(f'<aside class="pnote"><h3>{nt["h"]}</h3><p>{nt["t"]}</p></aside>')
            i += 1
        elif step in (1, 3) and rem >= 2:
            body.append(f'<figure class="h6">{g(i, "(max-width:760px) 92vw, 46vw")}</figure>')
            body.append(f'<figure class="h6">{g(i+1, "(max-width:760px) 92vw, 46vw")}</figure>')
            i += 2
        else:
            body.append(f'<figure class="full plx">{g(i, "92vw")}</figure>')
            i += 1
        pat += 1
    # leftover notes: quiet single column rows
    for nt in notes:
        body.append(f'<aside class="pnote nl"><h3>{nt["h"]}</h3><p>{nt["t"]}</p></aside>')
    parts.append(f'<div class="wrap"><div class="pgal">{"".join(body)}</div></div>')
    # quote + credits
    q = f'<section class="pquote"><div class="wrap"><blockquote>„{p["quote"]}“</blockquote>'
    if p.get('partners'):
        q += '<p class="pcred"><b>Prisidėjo:</b> ' + ' · '.join(p['partners']) + '</p>'
    q += '</div></section>'
    parts.append(q)
    parts.append(f'''<section class="pnext"><div class="wrap pnrow">
  <a class="back" href="/#projektai">← Visi projektai</a>
  <a class="nx" href="/projektai/{nxt['slug']}/"><span class="nl">Kitas projektas</span><span class="nt">{nxt['title']} →</span></a>
</div></section>''')

    head = HEAD.format(
        title=f'{p["title"]} · NAMIE geriausia',
        desc=(p['intro'][:150] + '…') if len(p['intro']) > 152 else p['intro'],
        canon=f'{DOMAIN}/projektai/{s}/', domain=DOMAIN, preload='', schema='')
    return head + '\n'.join(parts) + FOOT

# ---------------------------------------------------------------- emit
open(os.path.join(ROOT, 'index.html'), 'w').write(index_html())
urls = [DOMAIN + '/']
for n, p in enumerate(P):
    nxt = P[(n + 1) % len(P)]
    d = os.path.join(ROOT, 'projektai', p['slug'])
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w').write(project_html(p, nxt))
    urls.append(f'{DOMAIN}/projektai/{p["slug"]}/')

sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
_lastmod = datetime.date.today().isoformat()
sm += '\n'.join(f'  <url><loc>{u}</loc><lastmod>{_lastmod}</lastmod></url>' for u in urls)
sm += '\n</urlset>\n'
open(os.path.join(ROOT, 'sitemap.xml'), 'w').write(sm)
open(os.path.join(ROOT, 'robots.txt'), 'w').write(
    'User-agent: *\nAllow: /\n\nSitemap: ' + DOMAIN + '/sitemap.xml\n')
print('index + %d project pages + sitemap written' % len(P))
