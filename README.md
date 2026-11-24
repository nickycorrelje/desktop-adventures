# Nicky's Desktop Adventures

A pixel-art portfolio you can walk through. Plain HTML, CSS and JS, no build step.

## What works now
- `index.html` Utrecht (start): walk with the arrow keys or W A S D, doors open the rooms, the bridge leads to work.
- `work.html` the work map with the arena, McLaren, adidas, Swifty and IKEA.
- `room-home.html` and `room-klimhal.html` are built: green dots and tiles (3 x 3 visible, the rest scrolls).
- `room-ikea.html`, `room-adidas.html` and `room-swifty.html` are case rooms: art from the design system (Nicky removed), a quest log in the side panel, one green dot per field. Their texts are the `CASES` list in `tools/build.py`.
- `room-case.html` (McLaren, no art yet) and `room-pledge.html` are still placeholders.
- `about-list.html` and `work-list.html` are the list views (the quick version): the map / list switch at the right of the menu flips between world and list. They use the same texts as the rooms. `room-ikea.html#case-2` opens IKEA on its second case.
- `about.html` and `project.html` are temporary redirects.
- `mobile.html` is the mobile prototype (http://localhost:8000/mobile.html). It loads the real pages and shows them in a phone layout: tap to walk, a bottom sheet for the side panel, rooms fit the width with their panel below. On a desktop screen it sits in a phone frame. The build does not touch it.

## Navigation without jumping
`js/router.js` swaps only the game window when you walk through a door or click a link, so the page keeps its scroll position. It needs the site to be served over http (see below); opened straight from disk it falls back to normal page loads.

## Try it locally
```
python3 -m http.server 8000
```
Then open http://localhost:8000

## Publish
Drag the folder onto Netlify Drop, or connect the GitHub repo to Netlify, Vercel or Cloudflare Pages. No build command, publish directory is the repo root.

## Where things live
- `css/site.css` all styles (colours and type match the design system).
- `js/game.js` walking, collisions, doors, speech bubble that follows the character.
- `assets/` pixel worlds (without the character), the walking sprite sheet and icons.
- Collision boxes and doors are the `WORLD` lists at the bottom of `index.html` and `work.html`, in the art's own 320-px-wide units.
- `tools/make-klimhal.py` draws the newer icons and an older Klimhal world; `tools/build.py` writes all the pages.
- `assets/world-klimhal.png` now comes from the design system (room-klimhal.png, with the baked-in Nicky removed). Running `make-klimhal.py` overwrites it with the old drawing.
- All page text (speech bubbles, cards, labels) lives in `tools/build.py`, not in the HTML: the HTML is overwritten on every build. Change the text there, then run `cd tools && python3 build.py`.
- `tools/teksten.xlsx` overrides texts: every filled-in "Jouw tekst" (column F) replaces the text with the same ID (column A) on the next build. No extra packages needed. Save the sheet, then run the build.
- The build also stamps every image, stylesheet and script with `?v=<content hash>` (in the HTML and in `css/site.css`), so a changed file always loads fresh. Run the build after changing an image, CSS or JS file.
- `tools/` the scripts that drew the art and wrote the pages (optional, needs Python and Pillow).
