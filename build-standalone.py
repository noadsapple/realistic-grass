"""Build realistic-grass-standalone.html: the whole site in one HTML file.

Every image is embedded once (base64) in an IMG table; the page fills the
<img>/<link> tags from it at load. Usage:  python3 build-standalone.py
Requires Pillow (pip install pillow).
"""
import base64
import io
import os

from PIL import Image

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def data_uri(path, fmt="WEBP", quality=82):
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
    "assets/logo.png": data_uri("assets/logo.png"),
    "assets/van-left.png": data_uri("assets/van-left.png"),
    "assets/van-right.png": data_uri("assets/van-right.png"),
    "assets/qr.png": data_uri("assets/qr.png", "PNG"),
    "assets/turf.jpg": data_uri("assets/turf.jpg", "JPEG", 78),
}

html = open("index.html").read()
css = open("styles.css").read()
js = open("script.js").read()

css = css.replace('url("assets/turf.jpg")', "var(--turf-img)")
for key in IMAGES:
    js = js.replace(f'"{key}"', f'IMG["{key}"]')

# Relative asset URLs are meaningless in a single file
html = html.replace('  <meta property="og:image" content="assets/logo.png">\n', "")
html = html.replace('    "image": "assets/logo.png",\n', "")
html = html.replace('<link rel="icon" href="assets/logo.png">', '<link rel="icon" data-img="assets/logo.png">')
for key in IMAGES:
    html = html.replace(f'src="{key}"', f'data-img="{key}"')

table = "const IMG = {\n" + ",\n".join(f'  "{k}": "{v}"' for k, v in IMAGES.items()) + "\n};\n"
fill = """document.querySelectorAll("[data-img]").forEach((el) => {
  el[el.tagName === "LINK" ? "href" : "src"] = IMG[el.dataset.img];
});
document.documentElement.style.setProperty("--turf-img", `url("${IMG["assets/turf.jpg"]}")`);
"""
html = html.replace('<link rel="stylesheet" href="styles.css">', "<style>\n" + css + "\n</style>")
html = html.replace('<script src="script.js"></script>', "<script>\n" + table + fill + js + "\n</script>")

assert 'src="assets/' not in html and "href=\"styles.css\"" not in html
open("realistic-grass-standalone.html", "w").write(html)
print(f"realistic-grass-standalone.html: {len(html) // 1024} KB")
