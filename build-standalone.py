"""Build the whole site as single HTML files (one per language):
realistic-grass-standalone.html (EN) and realistic-grass-standalone-es.html (ES).

Every image is embedded once (base64) in an IMG table; the page fills the
<img>/<link> tags from it at load. Usage:  python3 build-standalone.py
Requires Pillow (pip install pillow).
"""
import base64
import io
import os
import re

from PIL import Image

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def data_uri(path, fmt="WEBP", quality=82):
    if fmt == "RAW":
        return "data:image/webp;base64," + base64.b64encode(open(path, "rb").read()).decode()
    im = Image.open(path)
    buf = io.BytesIO()
    if fmt == "JPEG":
        im.convert("RGB").save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
        mime = "image/jpeg"
    elif fmt == "PNG":
        im.save(buf, "PNG", optimize=True)
        mime = "image/png"
    else:
        im.save(buf, "WEBP", quality=quality, method=6)
        mime = "image/webp"
    return f"data:{mime};base64," + base64.b64encode(buf.getvalue()).decode()


IMAGES = {
    "assets/logo.webp": data_uri("assets/logo.webp", "RAW"),
    "assets/logo-sm.webp": data_uri("assets/logo-sm.webp", "RAW"),
    "assets/van-left.webp": data_uri("assets/van-left.webp", "RAW"),
    "assets/van-right.webp": data_uri("assets/van-right.webp", "RAW"),
    "assets/qr.png": data_uri("assets/qr.png", "PNG"),
    "assets/turf.jpg": data_uri("assets/turf.jpg", "JPEG", 78),
    "assets/favicon-32.png": data_uri("assets/favicon-32.png", "PNG"),
}
FONTS = {
    "assets/fonts/anton-latin.woff2": "data:font/woff2;base64," + base64.b64encode(open("assets/fonts/anton-latin.woff2", "rb").read()).decode(),
    "assets/fonts/inter-latin-var.woff2": "data:font/woff2;base64," + base64.b64encode(open("assets/fonts/inter-latin-var.woff2", "rb").read()).decode(),
}

CSS = open("styles.css").read().replace('url("assets/turf.jpg")', "var(--turf-img)")
for key, uri in FONTS.items():
    CSS = CSS.replace(f'url("{key}")', f'url("{uri}")')
JS = open("script.js").read()
for key in IMAGES:
    JS = JS.replace(f'"{key}"', f'IMG["{key}"]')
TABLE = "const IMG = {\n" + ",\n".join(f'  "{k}": "{v}"' for k, v in IMAGES.items()) + "\n};\n"
FILL = """document.querySelectorAll("[data-img]").forEach((el) => {
  el[el.tagName === "LINK" ? "href" : "src"] = IMG[el.dataset.img];
});
document.documentElement.style.setProperty("--turf-img", `url("${IMG["assets/turf.jpg"]}")`);
"""

EN_OUT = "realistic-grass-standalone.html"
ES_OUT = "realistic-grass-standalone-es.html"


def build(page, out, lang_links):
    html = open(page).read()
    # The Spanish page lives in es/ and points one level up
    html = html.replace('"../assets/', '"assets/').replace('"../styles.css"', '"styles.css"')
    html = html.replace('"../script.js"', '"script.js"')
    # The SEO block (canonical, social cards, analytics, JSON-LD) belongs to the published site only
    html = re.sub(r"\s*<!-- SEO:START.*?<!-- SEO:END -->", '\n  <link rel="icon" data-img="assets/favicon-32.png">', html, flags=re.S)
    for key in IMAGES:
        html = html.replace(f'src="{key}"', f'data-img="{key}"')
    # Legal pages are not bundled: link to the published ones
    live = "https://noadsapple.github.io/realistic-grass/"
    sub = "es/" if page.startswith("es/") else ""
    for doc in ("privacy.html", "warranty.html", "privacidad.html", "garantia.html"):
        html = html.replace(f'href="{doc}', f'href="{live}{sub}{doc}')
    # EN | ES switcher points at the other standalone file
    for old, new in lang_links.items():
        html = html.replace(old, new)
    html = html.replace('<link rel="stylesheet" href="styles.css">', "<style>\n" + CSS + "\n</style>")
    html = html.replace('<script src="script.js"></script>', "<script>\n" + TABLE + FILL + JS + "\n</script>")
    assert 'src="assets/' not in html and 'href="styles.css"' not in html
    open(out, "w").write(html)
    print(f"{out}: {len(html) // 1024} KB")


build("index.html", EN_OUT, {'<a href="./" aria-current': f'<a href="{EN_OUT}" aria-current',
                              '<a href="es/" hreflang="es"': f'<a href="{ES_OUT}" hreflang="es"'})
build("es/index.html", ES_OUT, {'<a href="../" hreflang="en"': f'<a href="{EN_OUT}" hreflang="en"',
                                 '<a href="./" aria-current': f'<a href="{ES_OUT}" aria-current'})
