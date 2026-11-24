/* Single-page navigation. Walking through a door or clicking a link swaps only the game window,
   so the header, the headline and the scroll position stay where they are (no jump back to the top).
   If anything goes wrong (for example when the files are opened straight from disk) it falls back to
   a normal page load. */
window.Router = (function () {
  function worldOf(doc) {
    var el = doc.getElementById('world-data');
    try { return el ? JSON.parse(el.textContent) : null; } catch (e) { return null; }
  }

  function boot(doc) {
    Game.stop(); Home.stop();
    Home.init();
    Game.start(worldOf(doc), new URLSearchParams(location.search).get('from'));
  }

  // Waits for the new picture, so the page never gets shorter for a moment (which would move the scroll position).
  function preload(win) {
    var imgs = Array.prototype.slice.call(win.querySelectorAll('img.world'));
    return Promise.all(imgs.map(function (im) {
      var p = new Image(); p.src = im.getAttribute('src');
      return p.decode ? p.decode().catch(function () {}) : Promise.resolve();
    }));
  }

  function go(url, push) {
    var u = new URL(url, location.href);
    if (u.origin !== location.origin) { location.href = u.href; return; }
    // 'no-cache': always ask the server whether the page changed, so a swap never shows an old copy from the browser cache.
    fetch(u.href, { cache: 'no-cache' }).then(function (r) { if (!r.ok) throw new Error(r.status); return r.text(); }).then(function (t) {
      var doc = new DOMParser().parseFromString(t, 'text/html');
      var next = doc.querySelector('.window'), cur = document.querySelector('.window');
      if (!next || !cur) throw new Error('no window');
      next = document.importNode(next, true);
      return preload(next).then(function () {
        var y = window.scrollY;
        var oldWorld = cur.querySelector('#stage img.world');
        var from = oldWorld && oldWorld.getAttribute('src');
        Game.stop(); Home.stop();
        cur.replaceWith(next);
        document.title = doc.title;
        if (push !== false) history.pushState(null, '', u.href);
        window.scrollTo(0, y);
        boot(doc);
        // World to world (through a door): the new room opens as a stepped circle from where you come in.
        // Anything else (a list view, a page without a world) just fades in.
        if (!(from && doorWipe(next, from))) next.classList.add('enter');
      });
    }).catch(function () { location.href = u.href; });
  }

  // Stepped circle, as in the design system: 8 steps in about 0.4 s, centred on the hero (who stands at the door
  // she came in through). The old world lies on top and a growing hole shows the new one.
  function doorWipe(win, from) {
    if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return false;
    var stage = win.querySelector('#stage'), hero = win.querySelector('#hero');
    if (!stage || !hero) return false;
    var s = stage.getBoundingClientRect(), h = hero.getBoundingClientRect();
    if (!s.width) return false;
    var x = h.left + h.width / 2 - s.left, y = h.top + h.height * 0.75 - s.top;   // her feet: the door tile
    var far = Math.max(Math.hypot(x, y), Math.hypot(s.width - x, y), Math.hypot(x, s.height - y), Math.hypot(s.width - x, s.height - y));
    var cover = document.createElement('div');
    cover.className = 'door-wipe'; cover.setAttribute('aria-hidden', 'true');
    cover.style.backgroundImage = 'url("' + from + '")';
    stage.appendChild(cover);
    var step = 0, STEPS = 8;
    function frame() {
      var r = far * step / STEPS;
      var m = 'radial-gradient(circle at ' + x + 'px ' + y + 'px, transparent ' + r + 'px, #000 ' + (r + 0.5) + 'px)';
      cover.style.webkitMaskImage = m; cover.style.maskImage = m;
      if (step++ < STEPS) setTimeout(frame, 50); else cover.remove();
    }
    frame();
    return true;
  }

  document.addEventListener('click', function (e) {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a || a.target || a.hasAttribute('download')) return;
    var u = new URL(a.href, location.href);
    if (u.origin !== location.origin || !/\.html$|\/$/.test(u.pathname)) return;
    e.preventDefault();
    go(u.href);
  });
  window.addEventListener('popstate', function () { go(location.href, false); });
  if ('scrollRestoration' in history) history.scrollRestoration = 'manual';

  boot(document);
  return { go: go };
})();
