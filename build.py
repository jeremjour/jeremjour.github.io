#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generateur du site jeremjour.com

Usage :  python3 build.py

Lit  site.config.json  +  src/base.html  (charte : CSS, nav, footer, lightbox)
Produit :
    index.html                    accueil (mosaique = accueil.selection)
    albums/index.html             liste des albums
    albums/<slug>/index.html      une page par album
    sitemap.xml                   toutes les URLs

Ne touche jamais aux dossiers photos/ et evenements/.
"""
import json, os, re, sys, datetime, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.join(ROOT, 'site.config.json')
BASE = os.path.join(ROOT, 'src', 'base.html')


def load():
    with open(CFG, encoding='utf-8') as f:
        cfg = json.load(f)
    with open(BASE, encoding='utf-8') as f:
        base = f.read()
    autodetect(cfg)
    return cfg, base


EXT = ('.avif', '.jpg', '.jpeg', '.png', '.webp')


def autodetect(cfg):
    """Ajoute automatiquement les photos deposees dans photos/<slug>/ et non
    encore listees dans la config. Rien a editer a la main pour un ajout simple."""
    nouveau = 0
    for a in cfg['albums']:
        dossier = a.get('dossier', f"photos/{a['slug']}")
        chemin = os.path.join(ROOT, dossier)
        if not os.path.isdir(chemin):
            continue
        deja = {p['src'] for p in a['photos']}
        trouves = sorted(f for f in os.listdir(chemin)
                         if f.lower().endswith(EXT) and not f.startswith('.'))
        for f in trouves:
            src = f"{dossier}/{f}"
            if src in deja:
                continue
            a['photos'].append({
                'src': src,
                'label': a['titre'],
                'alt': f"{a['titre']} — {a.get('sous_titre','')}".strip(' —'),
            })
            nouveau += 1
            print(f"  + detectee : {src}  (album {a['titre']})")
    if nouveau:
        print(f"  {nouveau} photo(s) ajoutee(s) automatiquement\n")

    # evenements : meme principe
    chemin = os.path.join(ROOT, 'evenements')
    if os.path.isdir(chemin):
        deja = {p['src'] for p in cfg['evenements']}
        for f in sorted(os.listdir(chemin)):
            if not f.lower().endswith(EXT) or f.startswith('.'):
                continue
            src = f"evenements/{f}"
            if src not in deja:
                cfg['evenements'].append(
                    {'src': src, 'label': 'ÉVÉNEMENT', 'alt': 'Reportage événementiel — Jérém'})
                print(f"  + detectee : {src}  (evenements)")


def thumb(src):
    """photos/islande/x.avif -> photos/thumbs/x.avif"""
    d, n = os.path.split(src)
    top = d.split('/')[0]
    return f"{top}/thumbs/{n}"


def esc(s):
    return (s or '').replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')


# ---------------------------------------------------------------- fragments

def nav(active, depth):
    """depth = nombre de niveaux sous la racine (0 pour /, 2 pour /albums/slug/)"""
    home = '/' if depth else './'
    items = [('albums', 'Albums', '/albums/'),
             ('videos', 'Vidéos', '/#videos' if depth else '#videos'),
             ('evenements', 'Événements', '/#evenements' if depth else '#evenements'),
             ('contact', 'Contact', '/#contact' if depth else '#contact')]
    lis, mob = [], []
    for key, txt, href in items:
        cls = ' class="active"' if key == active else ''
        onclick = ''
        if not depth and key in ('videos', 'evenements', 'contact'):
            onclick = f" onclick=\"showSection('{key}');return false;\""
        lis.append(f'<li><a href="{href}"{onclick} id="tab-{key}"{cls}>{txt}</a></li>')
        onclick_m = onclick.replace('return false;', 'closeMobileMenu();return false;') if onclick else ''
        mob.append(f'<li><a href="{href}"{onclick_m} id="mob-tab-{key}"{cls}>{txt}</a></li>')
    return f'''<nav>
  <a href="{home}" class="nav-logo">Jerem</a>
  <ul class="nav-links">{''.join(lis)}</ul>
  <button class="nav-hamburger" id="nav-hamburger" onclick="toggleMobileMenu()" aria-label="Menu"><span></span><span></span><span></span></button>
</nav>
<ul class="nav-mobile-menu" id="nav-mobile-menu">{''.join(mob)}</ul>'''


def head(cfg, titre, desc, canonical, extra_css=''):
    s = cfg['site']
    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(titre)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="author" content="Jérém — @jeremjour">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{esc(titre)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{s['url']}/preview.jpg">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="website">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="Jérém — Photographie & Nature">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(titre)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{s['url']}/preview.jpg">
<meta name="geo.region" content="FR-NAQ">
<meta name="geo.placename" content="Bordeaux, Nouvelle-Aquitaine">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@300;400;500;600&family=Lora:ital,wght@0,400;1,400&family=Inter:wght@300;400&family=Cormorant+Garamond:wght@300;400;600&display=swap" rel="stylesheet">
<style>{CSS}{extra_css}</style>
<script async src="https://www.googletagmanager.com/gtag/js?id={s['analytics']}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{s['analytics']}');</script>
</head>
<body>'''


FOOTER = '''<footer>
  <span>© 2026 Jérém</span>
  <span>Photographie &amp; Vidéographie</span>
</footer>'''


LIGHTBOX = '''<div class="lightbox" id="lightbox">
  <button class="lightbox-close" onclick="closeLightbox()" aria-label="Fermer">&#10005;</button>
  <span class="lightbox-counter" id="lightbox-counter"></span>
  <div class="lightbox-imgwrap" onclick="lightboxClickNav(event)"><img id="lightbox-img" alt=""></div>
  <span class="lightbox-caption" id="lightbox-caption"></span>
</div>'''


JS_COMMON = '''
function toggleMobileMenu(){var b=document.getElementById('nav-hamburger'),m=document.getElementById('nav-mobile-menu');b.classList.toggle('open');m.classList.toggle('open');}
function closeMobileMenu(){document.getElementById('nav-hamburger').classList.remove('open');document.getElementById('nav-mobile-menu').classList.remove('open');}
var lbIdx=0,activeGal=[];
function lbl(p){return p.label||'';}
function updateCtr(){document.getElementById('lightbox-counter').textContent=(lbIdx+1)+' / '+activeGal.length;}
function preload(i){[(i-1+activeGal.length)%activeGal.length,(i+1)%activeGal.length].forEach(function(j){var x=new Image();x.src='/'+activeGal[j].src;});}
function openLightbox(i,gal){activeGal=gal||activeGal;lbIdx=i;var p=activeGal[i];document.getElementById('lightbox-img').src='/'+p.src;document.getElementById('lightbox-img').alt=p.alt||'';document.getElementById('lightbox-caption').textContent=lbl(p);updateCtr();preload(i);document.getElementById('lightbox').classList.add('active');document.body.style.overflow='hidden';}
function lightboxNav(d){if(!activeGal.length)return;var w=document.getElementById('lightbox-img').parentElement;lbIdx=(lbIdx+d+activeGal.length)%activeGal.length;var p=activeGal[lbIdx];document.getElementById('lightbox-img').src='/'+p.src;document.getElementById('lightbox-img').alt=p.alt||'';document.getElementById('lightbox-caption').textContent=lbl(p);updateCtr();preload(lbIdx);w.style.transition='none';w.style.transform='';w.style.opacity='';}
function lightboxClickNav(e){lightboxNav(e.offsetX<e.currentTarget.offsetWidth/2?-1:1);}
function closeLightbox(){document.getElementById('lightbox').classList.remove('active');document.body.style.overflow='';}
document.addEventListener('keydown',function(e){if(e.key==='Escape')closeLightbox();if(e.key==='ArrowRight')lightboxNav(1);if(e.key==='ArrowLeft')lightboxNav(-1);});
(function(){var lb=document.getElementById('lightbox');if(!lb)return;var w=document.getElementById('lightbox-img').parentElement,sx=0,sy=0,ax=null;
lb.addEventListener('touchstart',function(e){sx=e.touches[0].clientX;sy=e.touches[0].clientY;ax=null;w.style.transition='none';},{passive:true});
lb.addEventListener('touchmove',function(e){var dx=e.touches[0].clientX-sx,dy=e.touches[0].clientY-sy;if(!ax&&(Math.abs(dx)>8||Math.abs(dy)>8))ax=Math.abs(dx)>Math.abs(dy)?'x':'y';if(ax==='x'){w.style.transform='translateX('+dx+'px)';w.style.opacity=String(Math.max(.3,1-Math.abs(dx)/(window.innerWidth*.8)));}else if(ax==='y'){w.style.transform='translateY('+dy*.4+'px)';w.style.opacity=String(Math.max(.3,1-Math.abs(dy)/300));}},{passive:true});
lb.addEventListener('touchend',function(e){var dx=e.changedTouches[0].clientX-sx,dy=e.changedTouches[0].clientY-sy;w.style.transition='';if(ax==='x'&&Math.abs(dx)>60){lightboxNav(dx<0?1:-1);}else if(ax==='y'&&Math.abs(dy)>90){closeLightbox();}w.style.transform='';w.style.opacity='';},{passive:true});})();
'''


def grid(items, gal_var):
    """Grille de vignettes cliquables."""
    out = []
    for i, p in enumerate(items):
        out.append(
            f'<div class="gallery-item" onclick="openLightbox({i},{gal_var})">'
            f'<img src="/{thumb(p["src"])}" alt="{esc(p.get("alt",""))}" width="500" height="667" loading="lazy">'
            f'<div class="gallery-item-overlay"><span class="gallery-label">{esc(p.get("label",""))}</span></div>'
            f'</div>')
    return ''.join(out)


# ---------------------------------------------------------------- pages

def page_accueil(cfg):
    s = cfg['site']
    index = {p['src']: p for a in cfg['albums'] for p in a['photos']}
    sel = [index[src] for src in cfg['accueil']['selection'] if src in index]
    manquants = [src for src in cfg['accueil']['selection'] if src not in index]
    for m in manquants:
        print(f"  ! accueil: {m} n'appartient a aucun album -> ignoree")

    ev = cfg['evenements']
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "ProfilePage", "mainEntity": {"@id": s['url'] + "/#jerem"}},
            {"@type": "Person", "@id": s['url'] + "/#jerem", "name": "Jérém",
             "alternateName": "jeremjour",
             "description": "Photographe et vidéaste drone — nature, paysages et Pyrénées. Basé à Bordeaux, Nouvelle-Aquitaine.",
             "url": s['url'], "image": s['url'] + "/preview.jpg",
             "sameAs": ["https://www.instagram.com/jeremjour", "https://www.instagram.com/jeremjour.live"],
             "jobTitle": "Photographe & Vidéaste Drone",
             "knowsAbout": ["Photographie de nature", "Photographie de paysage", "Vidéo par drone",
                            "Reportage événementiel", "Pyrénées", "Islande"],
             "address": {"@type": "PostalAddress", "addressLocality": "Bordeaux",
                         "addressRegion": "Nouvelle-Aquitaine", "addressCountry": "FR"}},
            {"@type": "ProfessionalService", "@id": s['url'] + "/#service",
             "name": "Jérém — Photographie & Drone", "founder": {"@id": s['url'] + "/#jerem"},
             "url": s['url'], "image": s['url'] + "/preview.jpg",
             "email": "jeremjour.drone@gmail.com", "priceRange": "$$",
             "address": {"@type": "PostalAddress", "addressLocality": "Bordeaux",
                         "addressRegion": "Nouvelle-Aquitaine", "addressCountry": "FR"},
             "areaServed": [{"@type": "AdministrativeArea", "name": n} for n in
                            ["Gironde", "Landes", "Pyrénées-Atlantiques", "Nouvelle-Aquitaine"]],
             "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Prestations", "itemListElement": [
                 {"@type": "Offer", "itemOffered": {"@type": "Service", "name": n}} for n in
                 ["Photographie de nature et de paysage", "Reportage photo et vidéo d'événements",
                  "Prises de vue aériennes immobilier et tourisme"]]}}
        ]}

    vids = cfg.get('videos', [])
    vid_html = ('<div class="empty-note">Vidéo à venir</div>' if not vids else ''.join(
        f'<div class="video-item {"portrait" if v.get("format")=="portrait" else "landscape"}" '
        f'onclick="openVideoLightbox(\'{v["id"]}\',this)"><div class="video-inner">'
        f'<div class="video-play"><svg width="14" height="14" viewBox="0 0 14 14"><polygon points="3,1 13,7 3,13"/></svg></div>'
        f'<span class="video-label">{esc(v.get("label",""))}</span></div></div>' for v in vids))

    html = head(cfg, s['titre'], s['description'], s['url'] + '/')
    html += f'''
{nav(None, 0)}
<section id="photos">
  <h1 class="sr-only">Jérém — Photographe &amp; Pilote Drone</h1>
  <div class="gallery-grid">{grid(sel, 'PHOTOS')}</div>
</section>

<section id="videos" class="hidden">
  <h2 class="sr-only">Vidéos drone et nature</h2>
  <div class="video-grid">{vid_html}</div>
</section>

<section id="evenements" class="hidden">
  <h2 class="sr-only">Photographie d'événements</h2>
  <div class="gallery-grid">{grid(ev, 'EVENEMENTS')}</div>
</section>

{CONTACT_SECTION}
{FOOTER}
{LIGHTBOX}
<div class="video-lightbox" id="video-lightbox">
  <button class="lightbox-close" onclick="closeVideoLightbox()" aria-label="Fermer">&#10005;</button>
  <div class="video-lightbox-inner" id="vlb-inner"><div class="video-lightbox-ratio" id="vlb-ratio"><iframe id="vlb-iframe" allow="autoplay; encrypted-media" allowfullscreen></iframe></div></div>
</div>
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, indent=1)}</script>
<script>
const PHOTOS={json.dumps(sel, ensure_ascii=False)};
const EVENEMENTS={json.dumps(ev, ensure_ascii=False)};
{JS_COMMON}
const sections=['photos','videos','evenements','contact'];
function showSection(id,updateHash){{
  if(sections.indexOf(id)===-1)id='photos';
  sections.forEach(function(sname){{
    var sec=document.getElementById(sname),tab=document.getElementById('tab-'+sname),mob=document.getElementById('mob-tab-'+sname);
    if(sname===id){{sec.classList.remove('hidden');if(tab)tab.classList.add('active');if(mob)mob.classList.add('active');
      sec.querySelectorAll('.reveal').forEach(function(el,i){{setTimeout(function(){{el.classList.add('visible');}},i*60);}});}}
    else{{sec.classList.add('hidden');if(tab)tab.classList.remove('active');if(mob)mob.classList.remove('active');}}
  }});
  if(updateHash!==false){{
    if(('#'+id)!==location.hash&&!(id==='photos'&&!location.hash))
      history.pushState({{section:id}},'',(id==='photos')?location.pathname:'#'+id);
  }}
  window.scrollTo({{top:0,behavior:'smooth'}});
}}
function sectionFromHash(){{var h=(location.hash||'').replace('#','');return sections.indexOf(h)!==-1?h:'photos';}}
function openVideoLightbox(id,item){{if(!id)return;var ip=item.classList.contains('portrait'),inn=document.getElementById('vlb-inner'),rat=document.getElementById('vlb-ratio'),ifr=document.getElementById('vlb-iframe');inn.className='video-lightbox-inner'+(ip?' portrait':'');rat.className='video-lightbox-ratio'+(ip?' portrait':'');ifr.src='https://www.youtube.com/embed/'+id+'?autoplay=1&rel=0&playsinline=1';document.getElementById('video-lightbox').classList.add('active');document.body.style.overflow='hidden';}}
function closeVideoLightbox(){{document.getElementById('video-lightbox').classList.remove('active');document.getElementById('vlb-iframe').src='';document.body.style.overflow='';}}
document.addEventListener('keydown',function(e){{if(e.key==='Escape')closeVideoLightbox();}});
(function(){{var st=sectionFromHash();showSection(st,false);
document.querySelectorAll('#'+st+' .reveal').forEach(function(el,i){{setTimeout(function(){{el.classList.add('visible');}},100+i*60);}});}})();
window.addEventListener('popstate',function(){{showSection(sectionFromHash(),false);}});
(function(){{var u='jeremjour.drone',d='gmail.com';['email-link','email-link-2'].forEach(function(id){{var a=document.getElementById(id);if(a)a.href='mailto:'+u+'@'+d;}});}})();
</script>
</body>
</html>'''
    return html


def page_albums_index(cfg):
    s = cfg['site']
    cards = []
    for a in cfg['albums']:
        cards.append(f'''<a class="album-card" href="/albums/{a['slug']}/">
      <div class="album-cover"><img src="/{thumb(a['couverture'])}" alt="{esc(a['titre'])} — {esc(a['sous_titre'])}" width="500" height="667" loading="lazy"></div>
      <div class="album-meta"><h2>{esc(a['titre'])}</h2><span class="album-sub">{esc(a['sous_titre'])}</span><span class="album-count">{len(a['photos'])} photos</span></div>
    </a>''')
    desc = "Albums photo de Jérém — Islande, Pyrénées, Monténégro, Croatie. Paysages et nature, au sol et par drone."
    schema = {"@context": "https://schema.org", "@type": "CollectionPage",
              "name": "Albums", "description": desc, "url": s['url'] + '/albums/',
              "hasPart": [{"@type": "ImageGallery", "name": a['titre'],
                           "description": a['description'],
                           "url": f"{s['url']}/albums/{a['slug']}/"} for a in cfg['albums']]}
    html = head(cfg, "Albums — Jérém | jeremjour.com", desc, s['url'] + '/albums/')
    html += f'''
{nav('albums', 2)}
<section class="page">
  <h1 class="sr-only">Albums</h1>
  <div class="album-grid">{''.join(cards)}</div>
</section>
{FOOTER}
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, indent=1)}</script>
<script>{JS_COMMON}</script>
</body>
</html>'''
    return html


def page_album(cfg, a):
    s = cfg['site']
    titre = f"{a['titre']} — Albums | Jérém"
    schema = {"@context": "https://schema.org", "@type": "ImageGallery",
              "name": a['titre'], "description": a['description'],
              "url": f"{s['url']}/albums/{a['slug']}/",
              "image": [f"{s['url']}/{p['src']}" for p in a['photos']]}
    html = head(cfg, titre, a['description'], f"{s['url']}/albums/{a['slug']}/")
    html += f'''
{nav('albums', 2)}
<section class="page">
  <a class="back-link" href="/albums/">← Albums</a>
  <h1 class="page-title">{esc(a['titre'])}</h1>
  <p class="page-sub">{esc(a['sous_titre'])} · {len(a['photos'])} photos</p>
  <div class="gallery-grid">{grid(a['photos'], 'GAL')}</div>
</section>
{FOOTER}
{LIGHTBOX}
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, indent=1)}</script>
<script>
const GAL={json.dumps(a['photos'], ensure_ascii=False)};
{JS_COMMON}
activeGal=GAL;
</script>
</body>
</html>'''
    return html


def sitemap(cfg):
    s = cfg['site']
    today = datetime.date.today().isoformat()
    urls = [(s['url'] + '/', '1.0', 'monthly'), (s['url'] + '/albums/', '0.9', 'monthly')]
    urls += [(f"{s['url']}/albums/{a['slug']}/", '0.8', 'monthly') for a in cfg['albums']]
    body = ''.join(
        f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{today}</lastmod>\n"
        f"    <changefreq>{c}</changefreq>\n    <priority>{p}</priority>\n  </url>\n"
        for u, p, c in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}</urlset>\n'


# ---------------------------------------------------------------- main

def main():
    cfg, base = load()
    global CSS, CONTACT_SECTION
    CSS = re.search(r'<style>(.*?)</style>', base, re.DOTALL).group(1)
    m = re.search(r'<section id="contact".*?</section>', base, re.DOTALL)
    CONTACT_SECTION = m.group(0)

    total_photos = sum(len(a['photos']) for a in cfg['albums'])
    print(f"Config : {len(cfg['albums'])} albums, {total_photos} photos, "
          f"{len(cfg['accueil']['selection'])} en accueil, {len(cfg['evenements'])} evenements")

    # verifie que toutes les images existent
    manquantes = []
    for a in cfg['albums']:
        for p in a['photos']:
            for f in (p['src'], thumb(p['src'])):
                if not os.path.exists(os.path.join(ROOT, f)):
                    manquantes.append(f)
    for p in cfg['evenements']:
        for f in (p['src'], thumb(p['src'])):
            if not os.path.exists(os.path.join(ROOT, f)):
                manquantes.append(f)
    if manquantes:
        print(f"\n! {len(manquantes)} fichier(s) manquant(s) :")
        for f in manquantes[:15]:
            print("   ", f)

    write(os.path.join(ROOT, 'index.html'), page_accueil(cfg))
    os.makedirs(os.path.join(ROOT, 'albums'), exist_ok=True)
    write(os.path.join(ROOT, 'albums', 'index.html'), page_albums_index(cfg))
    for a in cfg['albums']:
        d = os.path.join(ROOT, 'albums', a['slug'])
        os.makedirs(d, exist_ok=True)
        write(os.path.join(d, 'index.html'), page_album(cfg, a))
    write(os.path.join(ROOT, 'sitemap.xml'), sitemap(cfg))
    print("\nTermine.")


def write(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    rel = os.path.relpath(path, ROOT)
    print(f"  ecrit  {rel:<34} {len(content.encode()):>7} octets")


if __name__ == '__main__':
    main()
