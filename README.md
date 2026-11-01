# Realistic Grass — site web (www.realisticgrass.com)

Site statique prêt à déployer : anglais (`/`) et espagnol (`/es/`), pages légales, vidéos, logo animé.
Les sources et outils de fabrication sont dans le dépôt `noadsapple/realistic-grass`.

## Déployer avec WinSCP

1. Sur GitHub : bouton vert **Code → Download ZIP**, puis extraire le ZIP sur le PC.
2. WinSCP, panneau de droite : ouvrir la **racine web** de l'hébergement (le dossier servi par le domaine,
   p. ex. `/html`, `public_html` ou `www`).
3. Panneau de gauche : ouvrir le dossier extrait, sélectionner **tout son contenu** (`Ctrl+A`,
   fichiers cachés affichés avec `Ctrl+Alt+H` pour inclure `.htaccess`) et le glisser à droite.
   Ne pas copier `README.md` est sans importance (il peut rester).
4. À la racine web on doit voir, au même niveau : `assets/  es/  social/  .htaccess  index.html
   privacy.html  warranty.html  robots.txt  script.js  site.webmanifest  sitemap.xml  styles.css`.
   **Pas de sous-dossier intermédiaire.**

## Vérifier (navigation privée)

- https://www.realisticgrass.com/robots.txt affiche `Sitemap: https://www.realisticgrass.com/sitemap.xml`
- https://www.realisticgrass.com/social/realistic-grass-promo-square-en.mp4 lit la vidéo
- La page d'accueil montre le camion entier, le logo animé, la vidéo ; ES → EN reste sur realisticgrass.com

## Après la mise en ligne

- HTTPS activé, `realisticgrass.com` redirigé vers `https://www.realisticgrass.com/`
- Google Search Console : soumettre `sitemap.xml`
