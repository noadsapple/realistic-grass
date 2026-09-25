"""Generate the legal pages (privacy policy + limited warranty, EN and ES).

Content lives here so the four pages share one header/footer.
Usage:  python3 build-legal.py
"""
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

UPDATED = {"en": "September 25, 2026", "es": "25 de septiembre de 2026"}
COMPANY = "Realistic Grass LLC"
ADDRESS = "407 Lincoln Road, Suite 6J, Miami Beach, FL 33139"
PHONE_HTML = '<a href="tel:+17863299117">(786) 329-9117</a>'

UI = {
    "en": {
        "home": "index.html", "back": "← Back to the site", "print": "🖨 Print / Save as PDF",
        "privacy": "privacy.html", "warranty": "warranty.html",
        "privacy_t": "Privacy Policy", "warranty_t": "Limited Warranty", "access_t": "Accessibility",
        "footer_co": "a Florida limited liability company", "rights": "All rights reserved.",
        "updated": "Last updated", "lang_label": "Language", "tag": "Artificial Turf · Miami",
    },
    "es": {
        "home": "index.html", "back": "← Volver al sitio", "print": "🖨 Imprimir / Guardar en PDF",
        "privacy": "privacidad.html", "warranty": "garantia.html",
        "privacy_t": "Política de Privacidad", "warranty_t": "Garantía Limitada", "access_t": "Accesibilidad",
        "footer_co": "sociedad de responsabilidad limitada de Florida", "rights": "Todos los derechos reservados.",
        "updated": "Última actualización", "lang_label": "Idioma", "tag": "Grama Artificial · Miami",
    },
}

# Counterpart page in the other language, per page key
PATHS = {
    ("en", "privacy"): "privacy.html", ("es", "privacy"): "es/privacidad.html",
    ("en", "warranty"): "warranty.html", ("es", "warranty"): "es/garantia.html",
}


def page(lang, key, title, description, body):
    u = UI[lang]
    up = "" if lang == "en" else "../"
    other = "es" if lang == "en" else "en"
    other_href = ("es/" if lang == "en" else "../") + os.path.basename(PATHS[(other, key)])
    en_link = f'<a href="{other_href}" hreflang="en" lang="en">EN</a>' if lang == "es" else '<a href="#" aria-current="page" lang="en">EN</a>'
    es_link = f'<a href="{other_href}" hreflang="es" lang="es">ES</a>' if lang == "en" else '<a href="#" aria-current="page" lang="es">ES</a>'
    base = "https://noadsapple.github.io/realistic-grass/"
    return f"""<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} | {COMPANY}</title>
  <meta name="description" content="{description}">
  <meta name="theme-color" content="#0f4d2c">
  <link rel="icon" href="{up}assets/logo.png">
  <link rel="alternate" hreflang="en" href="{base}{PATHS[('en', key)]}">
  <link rel="alternate" hreflang="es" href="{base}{PATHS[('es', key)]}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{up}styles.css">
</head>
<body class="doc">
  <a class="skip-link" href="#main">{'Skip to content' if lang == 'en' else 'Saltar al contenido'}</a>
  <div class="turf-fallback" aria-hidden="true"></div>
  <div class="turf-shade" aria-hidden="true"></div>

  <header class="nav" id="top">
    <a href="{u['home']}" class="brand">
      <img src="{up}assets/logo.png" alt="Realistic Grass" width="72" height="67">
      <span class="brand-text"><b>Realistic</b> Grass<small>{u['tag']}</small></span>
    </a>
    <div class="lang" aria-label="{u['lang_label']}" style="margin-left:auto">
      {en_link}
      {es_link}
    </div>
    <a href="{u['home']}" class="btn btn-ghost nav-cta">{u['back']}</a>
  </header>

  <main id="main">
    <article class="section legal">
{body}
      <div class="doc-actions">
        <a href="{u['home']}" class="btn btn-ghost">{u['back']}</a>
        <button type="button" class="btn btn-yellow" onclick="window.print()">{u['print']}</button>
      </div>
    </article>
  </main>

  <footer class="footer">
    <p><b>{COMPANY}</b> · {ADDRESS}</p>
    <p>{PHONE_HTML} · <a href="https://www.realisticgrass.com">www.realisticgrass.com</a></p>
    <p class="footer-links"><a href="{u['privacy']}">{u['privacy_t']}</a> · <a href="{u['warranty']}">{u['warranty_t']}</a> · <a href="{u['privacy']}#{'accessibility' if lang == 'en' else 'accesibilidad'}">{u['access_t']}</a></p>
    <p class="small">© 2026 {COMPANY}, {u['footer_co']} (Doc. No. L25000417235). {u['rights']}</p>
  </footer>
</body>
</html>
"""


PRIVACY_EN = f"""      <p class="eyebrow">Legal</p>
      <h1>Privacy Policy</h1>
      <p class="meta">{UI['en']['updated']}: {UPDATED['en']}</p>

      <p>This policy explains how {COMPANY} (“Realistic Grass”, “we”, “us”) handles personal information collected through this website and when you contact us about artificial-turf products and installation.</p>

      <h2>Who we are</h2>
      <p>{COMPANY}, a Florida limited liability company (Florida Document No. L25000417235)<br>{ADDRESS}<br>Phone: {PHONE_HTML}</p>

      <h2>Information we collect</h2>
      <ul>
        <li><b>Information you give us</b>: when you use the free-estimate form, your device opens its messaging app with a text addressed to us containing the details you entered (name, phone number, city or ZIP code, project type, approximate area and your message). This website does not store what you type; we receive it only if you send the text. We also receive the information you give us when you call or text us.</li>
        <li><b>Technical information</b>: this website is hosted on GitHub Pages, which may log IP addresses and basic request data for security and operations. Fonts are loaded from Google Fonts, so your browser connects to Google's servers. These providers process that data under their own privacy policies.</li>
        <li><b>No cookies or trackers</b>: we do not use cookies, analytics, advertising pixels or any tool that tracks you across websites. The only thing stored on your device is your choice to pause the animations, and it stays in your browser.</li>
      </ul>

      <h2>How we use your information</h2>
      <ul>
        <li>To answer your request, prepare your estimate, schedule and perform the work.</li>
        <li>To provide customer service and honor our <a href="warranty.html">limited warranty</a>.</li>
        <li>To keep business, accounting and tax records and to comply with the law.</li>
      </ul>

      <h2>Calls and text messages</h2>
      <p>When you send us a request, you agree that we may call or text you at the number you provided about that request. We do not send marketing or promotional messages without your separate permission. You can reply STOP to any text from us, or tell us at any time that you no longer wish to be contacted. Message and data rates may apply.</p>

      <h2>Sharing</h2>
      <p>We do not sell your personal information and we do not share it for advertising. We only share it with service providers who help us run our business (for example, phone and messaging carriers), when required by law, or as part of a sale or reorganization of our business.</p>

      <h2>How long we keep it</h2>
      <p>We keep your information as long as needed for the purposes above, including the length of any warranty and the time required for legal and tax records.</p>

      <h2>Your choices</h2>
      <p>You may ask us to access, correct or delete your personal information, subject to records we must keep by law. Contact us by phone at {PHONE_HTML} or by mail at the address above.</p>

      <h2>Children</h2>
      <p>This website is not directed to children under 13 and we do not knowingly collect their personal information.</p>

      <h2>“Do Not Track”</h2>
      <p>We do not track visitors across websites, so browser “Do Not Track” signals do not change how this site works.</p>

      <h2>Changes to this policy</h2>
      <p>We may update this policy. The date at the top shows when it last changed.</p>

      <h2 id="accessibility">Accessibility statement</h2>
      <p>We want everyone to be able to use this website. We aim to meet the Web Content Accessibility Guidelines (WCAG) 2.1 level AA: text alternatives for images, keyboard navigation with visible focus, a “Skip to content” link, sufficient color contrast, and a button to pause the background animations (they are also turned off automatically if your device is set to reduce motion).</p>
      <p>If you have trouble using any part of the site or need information in another format, please call us at {PHONE_HTML} and we will help you.</p>
"""

PRIVACY_ES = f"""      <p class="eyebrow">Legal</p>
      <h1>Política de Privacidad</h1>
      <p class="meta">{UI['es']['updated']}: {UPDATED['es']}</p>

      <p>Esta política explica cómo {COMPANY} (“Realistic Grass”, “nosotros”) trata la información personal recopilada a través de este sitio web y cuando usted nos contacta sobre productos e instalación de grama artificial.</p>

      <h2>Quiénes somos</h2>
      <p>{COMPANY}, sociedad de responsabilidad limitada de Florida (Documento de Florida N.º L25000417235)<br>{ADDRESS}<br>Teléfono: {PHONE_HTML}</p>

      <h2>Información que recopilamos</h2>
      <ul>
        <li><b>Información que usted nos da</b>: cuando usa el formulario de estimado gratis, su dispositivo abre su aplicación de mensajes con un texto dirigido a nosotros que contiene los datos que escribió (nombre, teléfono, ciudad o código postal, tipo de proyecto, área aproximada y su mensaje). Este sitio no guarda lo que usted escribe; solo lo recibimos si usted envía el mensaje. También recibimos la información que nos da cuando nos llama o nos escribe.</li>
        <li><b>Información técnica</b>: este sitio está alojado en GitHub Pages, que puede registrar direcciones IP y datos básicos de las solicitudes por motivos de seguridad y funcionamiento. Las fuentes tipográficas se cargan desde Google Fonts, por lo que su navegador se conecta a los servidores de Google. Estos proveedores tratan esos datos según sus propias políticas de privacidad.</li>
        <li><b>Sin cookies ni rastreadores</b>: no usamos cookies, herramientas de análisis, píxeles publicitarios ni nada que le rastree entre sitios web. Lo único que se guarda en su dispositivo es su elección de pausar las animaciones, y se queda en su navegador.</li>
      </ul>

      <h2>Cómo usamos su información</h2>
      <ul>
        <li>Para responder a su solicitud, preparar su estimado, programar y realizar el trabajo.</li>
        <li>Para dar servicio al cliente y cumplir nuestra <a href="garantia.html">garantía limitada</a>.</li>
        <li>Para llevar registros comerciales, contables y fiscales, y cumplir la ley.</li>
      </ul>

      <h2>Llamadas y mensajes de texto</h2>
      <p>Al enviarnos una solicitud, usted acepta que le llamemos o le enviemos mensajes de texto al número indicado sobre esa solicitud. No enviamos mensajes publicitarios o promocionales sin su permiso por separado. Puede responder STOP a cualquier mensaje nuestro o decirnos en cualquier momento que ya no desea ser contactado. Pueden aplicarse tarifas de mensajes y datos.</p>

      <h2>Con quién compartimos</h2>
      <p>No vendemos su información personal ni la compartimos con fines publicitarios. Solo la compartimos con proveedores que nos ayudan a operar (por ejemplo, operadores de telefonía y mensajería), cuando la ley lo exige, o en caso de venta o reorganización de la empresa.</p>

      <h2>Cuánto tiempo la conservamos</h2>
      <p>Conservamos su información el tiempo necesario para los fines anteriores, incluida la duración de cualquier garantía y el plazo exigido para los registros legales y fiscales.</p>

      <h2>Sus opciones</h2>
      <p>Puede pedirnos acceder, corregir o eliminar su información personal, salvo los registros que debemos conservar por ley. Contáctenos por teléfono al {PHONE_HTML} o por correo postal a la dirección indicada arriba.</p>

      <h2>Menores</h2>
      <p>Este sitio no está dirigido a menores de 13 años y no recopilamos a sabiendas su información personal.</p>

      <h2>“No rastrear” (Do Not Track)</h2>
      <p>No rastreamos a los visitantes entre sitios web, por lo que las señales “Do Not Track” del navegador no cambian el funcionamiento de este sitio.</p>

      <h2>Cambios en esta política</h2>
      <p>Podemos actualizar esta política. La fecha indicada arriba muestra la última modificación.</p>

      <h2 id="accesibilidad">Declaración de accesibilidad</h2>
      <p>Queremos que todas las personas puedan usar este sitio. Buscamos cumplir las Pautas de Accesibilidad para el Contenido Web (WCAG) 2.1 nivel AA: textos alternativos en las imágenes, navegación con teclado con foco visible, un enlace “Saltar al contenido”, contraste de colores suficiente y un botón para pausar las animaciones de fondo (que también se desactivan automáticamente si su dispositivo está configurado para reducir el movimiento).</p>
      <p>Si tiene dificultades para usar alguna parte del sitio o necesita la información en otro formato, llámenos al {PHONE_HTML} y le ayudaremos.</p>
"""

WARRANTY_EN = f"""      <p class="eyebrow">Warranty</p>
      <h1>5-Year Limited Warranty</h1>
      <p class="meta">{UI['en']['updated']}: {UPDATED['en']} · Issued by {COMPANY}, {ADDRESS} · {PHONE_HTML}</p>

      <div class="box"><p><b>Summary</b> — For 5 years after we finish your installation, {COMPANY} will repair or replace, at no charge for materials and labor, turf we supplied and installed that fails because of a manufacturing defect or an installation defect. Details, exclusions and how to make a claim are below. Please ask us for a copy before you sign your quote.</p></div>

      <h2>1. Who is covered</h2>
      <p>The original customer who purchased an artificial-turf installation from {COMPANY}, at the property where the turf was installed. This warranty cannot be transferred.</p>

      <h2>2. What is covered</h2>
      <ul>
        <li><b>Materials</b>: turf supplied and installed by us, against manufacturing defects that appear under normal residential or commercial use (for example abnormal fading or loss of fibers).</li>
        <li><b>Workmanship</b>: defects caused by our installation, such as seams that separate, edges that lift, or base settling that creates visible depressions or standing water.</li>
      </ul>

      <h2>3. How long coverage lasts</h2>
      <p>5 years from the date the installation is completed, as shown on your invoice. Repairs or replacements do not extend this period. If the turf manufacturer also provides its own warranty, we will give you its terms; that manufacturer warranty is separate from this one.</p>

      <h2>4. What we will do</h2>
      <p>If a covered defect appears during the warranty period, we will, at our option, repair or replace the affected area at no charge for materials or labor. Replacement turf will be the same or a comparable product; because turf naturally weathers, an exact color match with the existing turf cannot be guaranteed.</p>

      <h2>5. What is not covered</h2>
      <ul>
        <li>Damage caused by misuse, abuse, vandalism, accidents, sharp objects, vehicles or heavy equipment.</li>
        <li>Heat damage from grills, fire pits, fireworks, cigarettes, or sunlight reflected from windows or other surfaces.</li>
        <li>Damage from chemicals, solvents, oils or other substances spilled on the turf.</li>
        <li>Damage by animals (digging, chewing) and odors caused by lack of regular rinsing and cleaning.</li>
        <li>Floods, hurricanes and storms, sinkholes, tree roots, ground movement not caused by our base work, and other natural events.</li>
        <li>Work, repairs or changes made by anyone other than {COMPANY}, and irrigation or drainage systems we did not install.</li>
        <li>Normal wear, including flattening (matting) of fibers in high-traffic areas.</li>
        <li>Turf sold without installation (turf-only / wholesale purchases): only the manufacturer's warranty, if any, applies.</li>
      </ul>

      <h2>6. How to get warranty service</h2>
      <p>Contact us at {PHONE_HTML} or by mail at {ADDRESS} within the warranty period and within 30 days of noticing the problem. Please have your invoice and photos of the issue. We will arrange an inspection and, if the defect is covered, schedule the repair.</p>

      <h2>7. Limitations</h2>
      <p class="caps">Any implied warranties, including the implied warranties of merchantability and fitness for a particular purpose, are limited to the 5-year duration of this written warranty. {COMPANY} is not responsible for incidental or consequential damages.</p>
      <p>Some states do not allow limitations on how long an implied warranty lasts, or the exclusion or limitation of incidental or consequential damages, so the above limitations or exclusions may not apply to you. This warranty gives you specific legal rights, and you may also have other rights which vary from state to state.</p>

      <div class="box print-only">
        <p><b>Warranty record</b></p>
        <p>Customer: ______________________________________________</p>
        <p>Installation address: ____________________________________</p>
        <p>Installation completed on: ______________ &nbsp; Invoice No.: ______________</p>
        <p>Turf product: ____________________________ &nbsp; Area: __________ sq ft</p>
        <p>For Realistic Grass LLC: __________________ &nbsp; Customer: __________________</p>
      </div>
"""

WARRANTY_ES = f"""      <p class="eyebrow">Garantía</p>
      <h1>Garantía Limitada de 5 Años</h1>
      <p class="meta">{UI['es']['updated']}: {UPDATED['es']} · Emitida por {COMPANY}, {ADDRESS} · {PHONE_HTML}</p>

      <div class="box"><p><b>Resumen</b> — Durante 5 años después de terminar su instalación, {COMPANY} reparará o reemplazará, sin costo de materiales ni de mano de obra, la grama que suministramos e instalamos si falla por un defecto de fabricación o de instalación. Abajo encontrará los detalles, las exclusiones y cómo hacer un reclamo. Pídanos una copia antes de firmar su cotización.</p></div>
      <p class="meta">La versión en inglés (<a href="../warranty.html">Limited Warranty</a>) es la versión de referencia; esta traducción se ofrece para su comodidad.</p>

      <h2>1. Quién está cubierto</h2>
      <p>El cliente original que compró una instalación de grama artificial a {COMPANY}, en la propiedad donde se instaló la grama. Esta garantía no es transferible.</p>

      <h2>2. Qué cubre</h2>
      <ul>
        <li><b>Materiales</b>: la grama suministrada e instalada por nosotros, contra defectos de fabricación que aparezcan con un uso residencial o comercial normal (por ejemplo, decoloración anormal o pérdida de fibras).</li>
        <li><b>Mano de obra</b>: defectos causados por nuestra instalación, como uniones que se separan, bordes que se levantan o hundimientos de la base que causan depresiones visibles o agua estancada.</li>
      </ul>

      <h2>3. Duración</h2>
      <p>5 años a partir de la fecha en que se termina la instalación, según su factura. Las reparaciones o reemplazos no extienden este plazo. Si el fabricante de la grama ofrece su propia garantía, le entregaremos sus condiciones; esa garantía del fabricante es independiente de esta.</p>

      <h2>4. Qué haremos</h2>
      <p>Si aparece un defecto cubierto durante el período de garantía, a nuestra elección repararemos o reemplazaremos el área afectada sin costo de materiales ni de mano de obra. La grama de reemplazo será el mismo producto o uno comparable; como la grama se desgasta de forma natural con el tiempo, no se puede garantizar que el color coincida exactamente con la grama existente.</p>

      <h2>5. Qué no cubre</h2>
      <ul>
        <li>Daños por mal uso, abuso, vandalismo, accidentes, objetos punzantes, vehículos o equipos pesados.</li>
        <li>Daños por calor de parrillas, fogatas, fuegos artificiales, cigarrillos o luz solar reflejada por ventanas u otras superficies.</li>
        <li>Daños por productos químicos, solventes, aceites u otras sustancias derramadas sobre la grama.</li>
        <li>Daños causados por animales (escarbar, morder) y olores por falta de enjuague y limpieza regulares.</li>
        <li>Inundaciones, huracanes y tormentas, socavones, raíces de árboles, movimientos del terreno no causados por nuestra base y otros fenómenos naturales.</li>
        <li>Trabajos, reparaciones o cambios hechos por otras personas que no sean {COMPANY}, y sistemas de riego o drenaje que no instalamos.</li>
        <li>El desgaste normal, incluido el aplastamiento de las fibras en zonas de mucho tránsito.</li>
        <li>La grama vendida sin instalación (compras solo de grama / al por mayor): solo se aplica la garantía del fabricante, si existe.</li>
      </ul>

      <h2>6. Cómo obtener servicio de garantía</h2>
      <p>Contáctenos al {PHONE_HTML} o por correo postal a {ADDRESS} dentro del período de garantía y dentro de los 30 días siguientes a notar el problema. Tenga a mano su factura y fotos del problema. Organizaremos una inspección y, si el defecto está cubierto, programaremos la reparación.</p>

      <h2>7. Limitaciones</h2>
      <p class="caps">Toda garantía implícita, incluidas las garantías implícitas de comerciabilidad y de idoneidad para un fin determinado, se limita a la duración de 5 años de esta garantía escrita. {COMPANY} no es responsable de daños incidentales o consecuentes.</p>
      <p>Algunos estados no permiten limitar la duración de una garantía implícita ni excluir o limitar los daños incidentales o consecuentes, por lo que es posible que las limitaciones o exclusiones anteriores no se apliquen en su caso. Esta garantía le otorga derechos legales específicos, y usted también puede tener otros derechos que varían de un estado a otro.</p>

      <div class="box print-only">
        <p><b>Registro de garantía</b></p>
        <p>Cliente: _______________________________________________</p>
        <p>Dirección de la instalación: _______________________________</p>
        <p>Instalación terminada el: ______________ &nbsp; Factura N.º: ______________</p>
        <p>Producto: _______________________________ &nbsp; Área: __________ pies²</p>
        <p>Por Realistic Grass LLC: __________________ &nbsp; Cliente: __________________</p>
      </div>
"""

os.makedirs("es", exist_ok=True)
out = {
    "privacy.html": page("en", "privacy", "Privacy Policy",
                         "How Realistic Grass LLC handles personal information, plus our accessibility statement.", PRIVACY_EN),
    "warranty.html": page("en", "warranty", "5-Year Limited Warranty",
                          "Terms of the Realistic Grass LLC 5-year limited warranty on artificial turf installations.", WARRANTY_EN),
    "es/privacidad.html": page("es", "privacy", "Política de Privacidad",
                               "Cómo Realistic Grass LLC trata la información personal, y nuestra declaración de accesibilidad.", PRIVACY_ES),
    "es/garantia.html": page("es", "warranty", "Garantía Limitada de 5 Años",
                             "Condiciones de la garantía limitada de 5 años de Realistic Grass LLC sobre instalaciones de grama artificial.", WARRANTY_ES),
}
for path, html in out.items():
    open(path, "w").write(html)
    print("wrote", path)
