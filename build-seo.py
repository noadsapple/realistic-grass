"""Inject SEO metadata into every page and write sitemap.xml, robots.txt and
site.webmanifest. Settings come from site.json (base URL, Google Search Console
verification token, GA4 measurement ID).

Each page gets one block between <!-- SEO:START --> and <!-- SEO:END --> in its
<head>: canonical + hreflang, Open Graph / Twitter cards, icons, font preloads,
optional Search Console tag and Google Analytics, and schema.org JSON-LD
(local business, website, web page, FAQ, breadcrumbs). Re-running replaces it.
Usage:  python3 build-seo.py
"""
import html as H
import json
import os
import re

os.chdir(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open("site.json"))
BASE = CFG["base_url"].rstrip("/") + "/"
GSV = CFG.get("google_site_verification", "").strip()
GA = CFG.get("ga4_measurement_id", "").strip()
UPDATED = CFG.get("updated", "")

PHONE = "+1-786-329-9117"
AREAS = ["Miami", "Miami Beach", "Brickell", "Coral Gables", "Doral", "Hialeah", "Kendall", "Homestead",
         "Aventura", "Pinecrest", "Key Biscayne", "Miami Lakes", "Palmetto Bay", "Cutler Bay", "North Miami",
         "South Miami", "Sunny Isles Beach", "Miami Gardens"]

HOME = {
    "en": {
        "title": "Artificial Grass Miami | Turf Installation – Realistic Grass",
        "description": "Artificial turf installed in Miami-Dade at wholesale prices: lawns, pet turf, putting greens, "
                       "pools. Free estimate · 5-year limited warranty.",
        "keywords": "artificial grass Miami, artificial turf Miami, synthetic turf installation, pet turf Miami, "
                    "putting green Miami, artificial grass wholesale, Miami-Dade turf installer",
        "og_title": "Realistic Grass – Artificial Grass Miami",
        "slogan": "Artificial Grass Expert in Miami",
        "services": [
            ("Artificial grass installation", "Lawns for front yards, backyards and HOA communities in Miami-Dade."),
            ("Pet turf", "Permeable, easy-to-rinse turf for dogs and pet areas."),
            ("Putting greens", "Custom backyard putting greens."),
            ("Playground turf", "Cushioned, mud-free play areas."),
            ("Pool surrounds, rooftops and balconies", "Turf for pool decks, terraces and balconies."),
            ("Commercial landscaping", "Artificial turf for businesses, schools and events."),
            ("Wholesale turf", "Turf rolls at wholesale prices for homeowners, landscapers and contractors."),
        ],
        "catalog": "Artificial turf services",
    },
    "es": {
        "title": "Grama Artificial Miami | Instalación – Realistic Grass",
        "description": "Grama artificial instalada en Miami-Dade a precios al por mayor: jardines, mascotas, "
                       "putting greens, piscinas. Estimado gratis y garantía limitada de 5 años.",
        "keywords": "grama artificial Miami, césped artificial Miami, césped sintético, instalación de grama artificial, "
                    "grama para perros Miami, putting green Miami, grama artificial al por mayor",
        "og_title": "Realistic Grass – Grama Artificial Miami",
        "slogan": "Expertos en Grama Artificial en Miami",
        "services": [
            ("Instalación de grama artificial", "Jardines delanteros, patios y comunidades con HOA en Miami-Dade."),
            ("Grama para mascotas", "Grama permeable y fácil de enjuagar para perros y áreas de mascotas."),
            ("Putting greens", "Putting greens a medida en su patio."),
            ("Grama para parques infantiles", "Áreas de juego acolchadas y sin lodo."),
            ("Piscinas, azoteas y balcones", "Grama para áreas de piscina, terrazas y balcones."),
            ("Paisajismo comercial", "Grama artificial para empresas, escuelas y eventos."),
            ("Grama al por mayor", "Rollos de grama a precios al por mayor para propietarios, jardineros y contratistas."),
        ],
        "catalog": "Servicios de grama artificial",
    },
}

# file on disk, URL path, language, key shared by translations, page kind
PAGES = [
    ("index.html", "", "en", "home", "home"),
    ("es/index.html", "es/", "es", "home", "home"),
    ("privacy.html", "privacy.html", "en", "privacy", "doc"),
    ("es/privacidad.html", "es/privacidad.html", "es", "privacy", "doc"),
    ("warranty.html", "warranty.html", "en", "warranty", "doc"),
    ("es/garantia.html", "es/garantia.html", "es", "warranty", "doc"),
]
HOME_NAME = {"en": "Home", "es": "Inicio"}
LOCALE = {"en": "en_US", "es": "es_US"}


def alternates(key):
    return {lang: BASE + path for _, path, lang, k, _ in PAGES if k == key}


def business(lang):
    h = HOME[lang]
    return {
        "@type": "HomeAndConstructionBusiness",
        "@id": BASE + "#business",
        "name": "Realistic Grass",
        "legalName": "Realistic Grass LLC",
        "slogan": h["slogan"],
        "description": h["description"],
        "url": BASE,
        "logo": BASE + "assets/icon-512.png",
        "image": [BASE + "assets/og-image-en.jpg", BASE + "assets/logo.webp"],
        "telephone": PHONE,
        "priceRange": "$$",
        "currenciesAccepted": "USD",
        "address": {
            "@type": "PostalAddress", "streetAddress": "407 Lincoln Road, Suite 6J",
            "addressLocality": "Miami Beach", "addressRegion": "FL", "postalCode": "33139", "addressCountry": "US",
        },
        "areaServed": [{"@type": "AdministrativeArea", "name": "Miami-Dade County, FL"}]
                      + [{"@type": "City", "name": f"{a}, FL"} for a in AREAS],
        "knowsLanguage": ["en", "es"],
        "contactPoint": {
            "@type": "ContactPoint", "telephone": PHONE, "contactType": "sales",
            "areaServed": "US-FL", "availableLanguage": ["English", "Spanish"],
        },
        "hasOfferCatalog": {
            "@type": "OfferCatalog", "name": h["catalog"],
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": n, "description": d,
                                                   "areaServed": {"@type": "AdministrativeArea", "name": "Miami-Dade County, FL"}}}
                for n, d in h["services"]
            ],
        },
    }


def faq_from_page(src):
    """FAQ structured data built from the visible <details> questions (kept in sync automatically)."""
    items = []
    for q, a in re.findall(r"<details><summary>(.*?)</summary><p>(.*?)</p></details>", src, re.S):
        clean = lambda s: H.unescape(re.sub(r"<[^>]+>", "", s)).strip()
        items.append({"@type": "Question", "name": clean(q),
                      "acceptedAnswer": {"@type": "Answer", "text": clean(a)}})
    return items


def text_of(tag, src):
    m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", src, re.S)
    return H.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else ""


def meta_description(src):
    m = re.search(r'<meta name="description" content="([^"]*)">', src)
    return H.unescape(m.group(1)) if m else ""


def seo_block(file, path, lang, key, kind, src):
    url = BASE + path
    alts = alternates(key)
    up = "../" if file.startswith("es/") else ""
    title = HOME[lang]["title"] if kind == "home" else text_of("title", src)
    desc = HOME[lang]["description"] if kind == "home" else meta_description(src)
    og_title = HOME[lang]["og_title"] if kind == "home" else title
    og_img = BASE + f"assets/og-image-{lang}.jpg"
    e = lambda s: H.escape(s, quote=True)

    graph = [
        business(lang),
        {"@type": "WebSite", "@id": BASE + "#website", "url": BASE, "name": "Realistic Grass",
         "inLanguage": ["en-US", "es-US"], "publisher": {"@id": BASE + "#business"}},
        {"@type": "WebPage", "@id": url + "#webpage", "url": url, "name": title, "description": desc,
         "inLanguage": f"{lang}-US", "isPartOf": {"@id": BASE + "#website"}, "about": {"@id": BASE + "#business"},
         "primaryImageOfPage": {"@type": "ImageObject", "url": og_img, "width": 1200, "height": 630},
         **({"dateModified": UPDATED} if UPDATED else {})},
    ]
    if kind == "home":
        faq = faq_from_page(src)
        if faq:
            graph.append({"@type": "FAQPage", "@id": url + "#faq", "inLanguage": f"{lang}-US", "mainEntity": faq})
    else:
        home = BASE + ("es/" if lang == "es" else "")
        graph[2]["breadcrumb"] = {"@id": url + "#breadcrumb"}
        graph.append({"@type": "BreadcrumbList", "@id": url + "#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": HOME_NAME[lang], "item": home},
            {"@type": "ListItem", "position": 2, "name": text_of("h1", src) or title, "item": url},
        ]})
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)

    lines = [
        "<!-- SEO:START (generated by build-seo.py – edit site.json / build-seo.py, not this block) -->",
        f'<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">',
        *( [f'<meta name="keywords" content="{e(HOME[lang]["keywords"])}">'] if kind == "home" else [] ),
        f'<link rel="canonical" href="{url}">',
        *[f'<link rel="alternate" hreflang="{l}" href="{u}">' for l, u in sorted(alts.items())],
        f'<link rel="alternate" hreflang="x-default" href="{alts["en"]}">',
        '<meta name="geo.region" content="US-FL">',
        '<meta name="geo.placename" content="Miami">',
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="Realistic Grass">',
        f'<meta property="og:locale" content="{LOCALE[lang]}">',
        f'<meta property="og:locale:alternate" content="{LOCALE["es" if lang == "en" else "en"]}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:title" content="{e(og_title)}">',
        f'<meta property="og:description" content="{e(desc)}">',
        f'<meta property="og:image" content="{og_img}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{e(og_title)}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{e(og_title)}">',
        f'<meta name="twitter:description" content="{e(desc)}">',
        f'<meta name="twitter:image" content="{og_img}">',
        '<meta name="theme-color" content="#0f4d2c">',
        '<meta name="format-detection" content="telephone=yes">',
        f'<link rel="icon" type="image/png" sizes="32x32" href="{up}assets/favicon-32.png">',
        f'<link rel="apple-touch-icon" href="{up}assets/apple-touch-icon.png">',
        f'<link rel="manifest" href="{up}site.webmanifest">',
        f'<link rel="preload" href="{up}assets/fonts/anton-latin.woff2" as="font" type="font/woff2" crossorigin>',
        f'<link rel="preload" href="{up}assets/fonts/inter-latin-var.woff2" as="font" type="font/woff2" crossorigin>',
    ]
    if GSV:
        lines.append(f'<meta name="google-site-verification" content="{e(GSV)}">')
    if GA:
        # Loaded only on the published site, and not for visitors who send Global Privacy Control / Do Not Track
        lines.append(f"""<script>
(function () {{
  var id = "{e(GA)}";
  if (location.protocol === "file:" || navigator.globalPrivacyControl || navigator.doNotTrack === "1") return;
  var s = document.createElement("script"); s.async = true;
  s.src = "https://www.googletagmanager.com/gtag/js?id=" + id; document.head.appendChild(s);
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () {{ dataLayer.push(arguments); }};
  gtag("js", new Date());
  gtag("config", id);
}})();
</script>""")
    lines.append(f'<script type="application/ld+json">\n{ld}\n</script>')
    lines.append("<!-- SEO:END -->")
    return title, desc, "\n  ".join(lines)


LEGACY = [  # tags now produced by the SEO block
    r'\s*<meta name="theme-color"[^>]*>', r'\s*<link rel="icon"[^>]*>', r'\s*<link rel="canonical"[^>]*>',
    r'\s*<link rel="alternate" hreflang[^>]*>', r'\s*<meta property="og:[^>]*>',
    r'\s*<script type="application/ld\+json">.*?</script>',
    r'\s*<link rel="preconnect" href="https://fonts\.[^>]*>', r'\s*<link href="https://fonts\.googleapis\.com[^>]*>',
]

for file, path, lang, key, kind in PAGES:
    src = open(file).read()
    src = re.sub(r"\s*<!-- SEO:START.*?<!-- SEO:END -->", "", src, flags=re.S)
    for pat in LEGACY:
        src = re.sub(pat, "", src, flags=re.S)
    title, desc, block = seo_block(file, path, lang, key, kind, src)
    src = re.sub(r"<title>.*?</title>", f"<title>{H.escape(title, quote=False)}</title>", src, count=1, flags=re.S)
    src = re.sub(r'<meta name="description" content="[^"]*">',
                 lambda m: f'<meta name="description" content="{H.escape(desc, quote=True)}">\n  {block}', src, count=1)
    open(file, "w").write(src)
    print(f"SEO  {file:22} {len(title):3} chars title, {len(desc):3} chars description")

# sitemap.xml with hreflang alternates
urls = []
for file, path, lang, key, kind in PAGES:
    alts = alternates(key)
    links = "".join(f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{u}"/>' for l, u in sorted(alts.items()))
    links += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{alts["en"]}"/>'
    prio = "1.0" if kind == "home" else "0.3"
    urls.append(f"""  <url>
    <loc>{BASE + path}</loc>{links}
    <lastmod>{UPDATED}</lastmod>
    <changefreq>{"monthly" if kind == "home" else "yearly"}</changefreq>
    <priority>{prio}</priority>
  </url>""")
open("sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    + "\n".join(urls) + "\n</urlset>\n")

open("robots.txt", "w").write(f"""# Crawlers only read robots.txt at the root of a domain; this file takes effect
# once the site is served from www.realisticgrass.com.
User-agent: *
Allow: /
Disallow: /realistic-grass-standalone.html
Disallow: /realistic-grass-standalone-es.html

Sitemap: {BASE}sitemap.xml
""")

json.dump({
    "name": "Realistic Grass – Artificial Grass Miami", "short_name": "Realistic Grass",
    "description": HOME["en"]["description"], "lang": "en-US", "start_url": "./", "scope": "./",
    "display": "browser", "background_color": "#0f4d2c", "theme_color": "#0f4d2c",
    "icons": [{"src": "assets/icon-192.png", "sizes": "192x192", "type": "image/png"},
              {"src": "assets/icon-512.png", "sizes": "512x512", "type": "image/png"}],
}, open("site.webmanifest", "w"), ensure_ascii=False, indent=2)
print("wrote sitemap.xml, robots.txt, site.webmanifest")
