# Realistic Grass — site vitrine (Artificial Grass Miami)

**En ligne : https://noadsapple.github.io/realistic-grass/** (anglais) · **https://noadsapple.github.io/realistic-grass/es/** (espagnol) (branche `gh-pages`, mise à jour automatiquement à chaque push sur `main`).

Site statique (HTML/CSS/JS, aucune dépendance) — ouvrir `index.html` ou servir le dossier :

```bash
cd realistic-grass && python3 -m http.server 8000   # http://localhost:8000
```

| Fichier | Rôle |
|---|---|
| `es/index.html` | Version espagnole (mêmes sections, mêmes styles/scripts via `../`) ; sélecteur EN / ES dans le menu, balises `hreflang` pour Google |
| `privacy.html`, `warranty.html`, `es/privacidad.html`, `es/garantia.html` | Politique de confidentialité (+ déclaration d'accessibilité) et garantie limitée 5 ans, EN/ES — générées par `build-legal.py` (modifier le texte là, puis relancer le script) |
| `docs/` | Garantie limitée en PDF (EN/ES) avec encadré à remplir, à joindre aux devis |
| `index.html` | Contenu marketing : hero, produits, applications, pourquoi nous, bénéfices, process 4 étapes, avis, zones desservies, FAQ, contact (reprend la pancarte : téléphone, site, QR, 5 arguments) |
| `styles.css` | Charte : vert foncé / vert lime / jaune (camion), typo Anton + Inter, responsive |
| `script.js` | 1) pelouse de fond animée par le vent (shader WebGL sur la photo) · 2) camion qui fait le tour de la fenêtre (avant orienté dans le sens de la marche) en posant une bordure de dalles de gazon qui tombent de l'arrière · 3) menu mobile + formulaire (ouvre un SMS vers le 786-329-9117) |
| `build-standalone.py` | Regénère `realistic-grass-standalone.html` (EN) et `realistic-grass-standalone-es.html` (ES) : site complet en un seul fichier, images incluses |
| `assets/` | `logo.png`, `van-left.png` / `van-right.png` (détourés), `turf.jpg` (photo rendue raccordable), `qr.png` (→ magicrealisticgrass.com) |

Animations désactivées automatiquement si l'utilisateur a activé « réduire les animations ».
Sans WebGL, la photo de pelouse s'affiche en fond fixe.

À compléter avant mise en ligne : vrais avis clients (les avis actuels sont des exemples),
adresse / e-mail éventuels, et un vrai back-end de formulaire (ex. Formspree) si besoin.

## Informations légales utilisées

Realistic Grass LLC — Florida LLC, Document No. L25000417235 (déposée le 09/09/2025) —
407 Lincoln Road, Suite 6J, Miami Beach, FL 33139 — domaine realisticgrass.com.
