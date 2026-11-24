/* Walking engine. Coordinates are in the world's native pixels (the art is drawn at 320 wide).
   Game.start(cfg, from) builds a game on the current #stage, Game.stop() tears it down again,
   so the router can swap rooms without reloading the page. */
window.Game = (function () {
  var SW = 24, SH = 32;                              // sprite size
  var FEET = { x: 6, y: 22, w: 12, h: 8 };           // collision box inside the sprite
  var SPEED = 80;                                    // native px per second
  var ROW = { down: 0, up: 1, left: 2, right: 3 };
  var MAP = { ArrowUp: 'up', ArrowDown: 'down', ArrowLeft: 'left', ArrowRight: 'right', w: 'up', s: 'down', a: 'left', d: 'right', W: 'up', S: 'down', A: 'left', D: 'right' };
  var g = null;                                      // state of the running game

  function hits(a, b) { return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y; }

  function start(cfg, from) {
    stop();
    var stage = document.getElementById('stage'), heroEl = document.getElementById('hero');
    if (!cfg || !stage || !heroEl) return;
    var bubble = document.getElementById('bubble');
    // Every bubble gets a close button, so it can be clicked away. A closed bubble stays closed
    // for the rest of the visit, also after walking out of the room and back in (one key per page).
    var closedKey = 'bubble-closed:' + location.pathname;
    function wasClosed() { try { return sessionStorage.getItem(closedKey) === '1'; } catch (e) { return false; } }
    if (bubble && wasClosed()) bubble.classList.add('gone', 'closed');
    if (bubble && !bubble.querySelector('.bubble-close')) {
      var x = document.createElement('button');
      x.type = 'button'; x.className = 'bubble-close'; x.setAttribute('aria-label', 'Close'); x.textContent = '×';
      x.addEventListener('click', function () {
        bubble.classList.add('gone', 'closed');
        try { sessionStorage.setItem(closedKey, '1'); } catch (e) {}
      });
      bubble.appendChild(x);
    }
    var W = cfg.w, H = cfg.h;
    var spawn = cfg.spawns[from] || cfg.spawns['default'];
    var s = g = { cfg: cfg, x: spawn[0], y: spawn[1], dir: spawn[2] || 'down', keys: {}, frame: 0, frameT: 0, last: 0, moving: false, raf: 0, off: [] };
    var startX = s.x, startY = s.y;
    heroEl.style.width = (SW / W * 100) + '%';

    function feet(px, py) { return { x: px + FEET.x, y: py + FEET.y, w: FEET.w, h: FEET.h }; }
    function blocked(px, py) {
      if (px < 0 || py < -FEET.y + 2 || px > W - SW || py > H - SH) return true;
      var f = feet(px, py);
      for (var i = 0; i < cfg.solid.length; i++) {
        var o = cfg.solid[i];
        if (hits(f, { x: o[0], y: o[1], w: o[2], h: o[3] })) return true;
      }
      return false;
    }

    // The bubble always belongs to the hero: its tail points at the head.
    // Beside the hero (cfg.bubble 'right'): to the right, or to the left when there is no room, tail pointing sideways.
    // Above the hero: tail down, or below with the tail up when there is no room above.
    function clamp(v, lo, hi) { return Math.max(lo, Math.min(v, hi)); }
    function tail(dir) {
      bubble.classList.remove('t-down', 't-up', 't-left', 't-right');
      bubble.classList.add('t-' + dir);
    }
    function placeBubble() {
      var sw = stage.clientWidth, sh = stage.clientHeight;
      var bw = bubble.offsetWidth, bh = bubble.offsetHeight;
      var heroL = s.x / W * sw, heroR = (s.x + SW) / W * sw;
      var headX = (s.x + SW / 2) / W * sw, headTop = s.y / H * sh, headMid = (s.y + 7) / H * sh, feetY = (s.y + SH) / H * sh;
      var GAP = 18, left, top;
      var fitsRight = heroR + GAP + bw <= sw - 6, fitsLeft = heroL - GAP - bw >= 6;
      if (cfg.bubble === 'right' && (fitsRight || fitsLeft)) {
        left = fitsRight ? heroR + GAP : heroL - GAP - bw;
        top = clamp(headMid - 22, 6, sh - bh - 6);
        tail(fitsRight ? 'left' : 'right');
        bubble.style.setProperty('--tail', clamp(headMid - top, 16, bh - 16) + 'px');
      } else {
        // Above the hero, or beside it when the map is too narrow (phones): then above or below instead.
        left = clamp(headX - bw / 2, 6, sw - bw - 6);
        var above = headTop - bh - GAP >= 6;
        top = above ? headTop - bh - GAP : Math.min(feetY + GAP, sh - bh - 6);
        tail(above ? 'down' : 'up');
        bubble.style.setProperty('--tail', clamp(headX - left, 16, bw - 16) + 'px');
        if (cfg.bubble !== 'right' && Math.abs(s.x - startX) + Math.abs(s.y - startY) > 50) bubble.classList.add('gone');
      }
      bubble.style.left = left + 'px'; bubble.style.top = top + 'px'; bubble.style.bottom = 'auto';
    }

    function draw() {
      heroEl.style.left = (s.x / W * 100) + '%';
      heroEl.style.top = (s.y / H * 100) + '%';
      var col = s.moving ? s.frame % 4 : 0;
      heroEl.style.backgroundPosition = (col * 33.3333) + '% ' + (ROW[s.dir] * 33.3333) + '%';
      if (bubble) placeBubble();
    }

    function onStage() { var r = stage.getBoundingClientRect(); return r.bottom > 0 && r.top < innerHeight; }
    // Arrow keys belong to the game, never to the page: otherwise the page scrolls the map out of view.
    // (Scroll with the mouse or trackpad.) W A S D only play while the map is on screen.
    function onKey(e) {
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      var t = e.target; if (t && /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName)) return;
      var d = MAP[e.key]; if (!d) return;
      var arrow = e.key.indexOf('Arrow') === 0;
      if (t && t.classList && t.classList.contains('tiles') && arrow) return;   // let the collectables list scroll with the keyboard
      if (!arrow && !onStage()) return;
      s.keys[d] = true; e.preventDefault();
    }
    function onUp(e) { var d = MAP[e.key]; if (d) { s.keys[d] = false; if (e.key.indexOf('Arrow') === 0) e.preventDefault(); } }
    function onBlur() { s.keys = {}; }
    function on(t, ev, fn, opt) { t.addEventListener(ev, fn, opt); s.off.push(function () { t.removeEventListener(ev, fn, opt); }); }
    on(window, 'keydown', onKey, { capture: true, passive: false });
    on(window, 'keyup', onUp, { capture: true, passive: false });
    on(window, 'blur', onBlur);
    on(window, 'resize', draw);
    window.GAME_PRESS = function (d, v) { s.keys[d] = v; };   // d-pad / tap helper for touch controls later

    function leave(url) {
      stop();
      if (window.Router) window.Router.go(url); else location.href = url;
    }

    function tick(t) {
      if (g !== s) return;
      var dt = Math.min((t - s.last) / 1000, 0.05); s.last = t;
      var dx = (s.keys.right ? 1 : 0) - (s.keys.left ? 1 : 0);
      var dy = (s.keys.down ? 1 : 0) - (s.keys.up ? 1 : 0);
      s.moving = dx !== 0 || dy !== 0;
      if (s.moving) {
        if (dx && !dy) s.dir = dx > 0 ? 'right' : 'left';
        else if (dy && !dx) s.dir = dy > 0 ? 'down' : 'up';
        var len = Math.sqrt(dx * dx + dy * dy), step = SPEED * dt / len;
        if (!blocked(s.x + dx * step, s.y)) s.x += dx * step;
        if (!blocked(s.x, s.y + dy * step)) s.y += dy * step;
        s.frameT += dt;
        if (s.frameT > 0.13) { s.frameT = 0; s.frame++; }
        var f = feet(s.x, s.y);
        for (var i = 0; i < cfg.doors.length; i++) {
          var dd = cfg.doors[i];
          if (hits(f, { x: dd[0], y: dd[1], w: dd[2], h: dd[3] })) { draw(); leave(dd[4]); return; }
        }
      } else { s.frame = 0; s.frameT = 0; }
      draw();
      s.raf = requestAnimationFrame(tick);
    }
    draw();
    s.raf = requestAnimationFrame(function (t) { s.last = t; tick(t); });
  }

  function stop() {
    if (!g) return;
    cancelAnimationFrame(g.raf);
    g.off.forEach(function (f) { f(); });
    g = null;
  }

  return { start: start, stop: stop };
})();
