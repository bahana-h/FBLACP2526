Lazy Dog font for "Chrysalis Connect" heading
==============================================
Font by Paul Neave - 100% Free (https://www.dafont.com/lazy-dog.font)

The site tries these options in order until one works:

1. Direct WOFF from CDN Fonts (in styles.css) - no action needed if CDN allows GitHub Pages.

2. CDN stylesheet - index.html links to fonts.cdnfonts.com (Lazydog). May be blocked on some hosts.

3. Self-host in this folder:
   - Download lazy_dog.ttf from https://www.dafont.com/lazy-dog.font
   - Save it here as: lazy_dog.ttf
   - Push to your repo. The CSS will load it from assets/fonts/lazy_dog.ttf.

4. After pushing the file, jsDelivr can also serve it from your repo:
   - URL: https://cdn.jsdelivr.net/gh/USER/REPO@main/docs/assets/fonts/lazy_dog.ttf
   - Replace USER/REPO with your GitHub username and repo name (e.g. bahana-h/FBLACP2526).
   - The CSS already has a "Lazy Dog Fallback" @font-face for this (edit styles.css if your repo path differs).

If none load, the browser falls back to a cursive system font.
