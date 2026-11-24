/* Rooms with collectables (Home, Klimhal): click a green dot or a tile to read about that object.
   Home.init() runs after every room swap, Home.stop() before it. */
window.Home = (function () {
  var timer = 0;

  function init() {
    stop();
    var tiles = document.querySelectorAll('.tile'), dots = document.querySelectorAll('.hot'), details = document.querySelectorAll('.detail');
    // Case rooms with one case: every green dot lights up its field in the quest log.
    // A room with more than one case (IKEA) has tabs above the quest log and one green dot per case:
    // a dot opens its case's tab, and the dot of the open case is the green one.
    var fields = document.querySelectorAll('.qf');
    if (!tiles.length && fields.length) {
      var lit = null, tabs = document.querySelectorAll('.qtab');
      function light() {
        fields.forEach(function (f) { f.classList.toggle('on', f.dataset.item === lit && !f.parentNode.hidden); });
        dots.forEach(function (o) { if (!o.dataset.case) o.classList.toggle('on', o.dataset.item === lit); });
        var f = document.querySelector('.quest:not([hidden]) .qf.on'); if (f && f.scrollIntoView) f.scrollIntoView({ block: 'nearest' });
      }
      // A colleague's quote card sits under its case (data-for = the quest's id) and shows with it.
      // The colleague who stands on her own (IKEA, by the plant) has her own dot: it shows her quote instead of a case.
      var lone = document.querySelector('.quote[data-lone]');
      function showCase(id) {
        document.querySelectorAll('.quest').forEach(function (q) { q.hidden = q.id !== id; });
        document.querySelectorAll('.quote[data-for]').forEach(function (q) { q.hidden = q.dataset.for !== id; });
        if (lone) lone.hidden = id !== null;
      }
      dots.forEach(function (d) {
        d.addEventListener('click', function () {
          if (d.dataset.case) { if (tabs[d.dataset.case - 1]) tabs[d.dataset.case - 1].click(); return; }
          if (d.dataset.quote) {
            tabs.forEach(function (o) { o.setAttribute('aria-selected', false); });
            showCase(null);
            dots.forEach(function (o) { o.classList.toggle('on', o === d); });
            return;
          }
          lit = d.dataset.item; light();
        });
      });
      tabs.forEach(function (t, i, all) {
        t.addEventListener('click', function () {
          all.forEach(function (o) { o.setAttribute('aria-selected', o === t); });
          showCase(t.getAttribute('aria-controls'));
          dots.forEach(function (o) { if (o.dataset.case || o.dataset.quote) o.classList.toggle('on', +o.dataset.case === i + 1); });
          light();
        });
      });
      // Coming from the work list (room-ikea.html#case-2): open that case's tab.
      var m = /^#case-(\d+)$/.exec(location.hash);
      if (m && tabs[m[1] - 1]) tabs[m[1] - 1].click();
      return;
    }
    if (!tiles.length) return;
    function select(key) {
      tiles.forEach(function (t) { var on = t.dataset.item === key; t.classList.toggle('on', on); t.setAttribute('aria-pressed', on); });
      dots.forEach(function (d) { d.classList.toggle('on', d.dataset.item === key); });
      details.forEach(function (d) { d.hidden = d.dataset.item !== key; });
      var sel = document.querySelector('.tile.on'); if (sel && sel.scrollIntoView) sel.scrollIntoView({ block: 'nearest' });  // a dot click can pick a tile that is scrolled out of view
    }
    tiles.forEach(function (t) { t.addEventListener('click', function () { select(t.dataset.item); }); });
    dots.forEach(function (d) { d.addEventListener('click', function () { select(d.dataset.item); }); });
    nowSpinning();
  }

  /* Now spinning: last.fm "currently playing", shown inside the Records card and only while something plays.
     Settings live in js/config.js. */
  function nowSpinning() {
    var box = document.getElementById('spin'); if (!box) return;
    var label = document.getElementById('spin-label'), text = document.getElementById('spin-text');
    var vinyl = document.getElementById('vinyl'), stage = document.getElementById('stage');
    var cfg = (window.SITE && window.SITE.lastfm) || {};
    function show(state, l, t) {
      label.textContent = l; text.textContent = t;
      var on = state === 'playing';
      box.hidden = state === 'idle';                    // nothing playing: no block at all
      box.classList.toggle('on', on);
      if (stage) stage.classList.toggle('playing', on);
      if (vinyl) vinyl.classList.toggle('paused', state === 'idle');   // the record only stands still when we know nothing plays
    }
    if (!cfg.user || !cfg.key) { show('unset', 'Now spinning', '[ADD: last.fm username and API key in js/config.js]'); return; }
    var dead = false;
    function load() {
      var url = 'https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&limit=1&format=json&user=' +
        encodeURIComponent(cfg.user) + '&api_key=' + encodeURIComponent(cfg.key);
      fetch(url).then(function (r) { return r.json(); }).then(function (j) {
        if (dead) return;
        var tr = j && j.recenttracks && j.recenttracks.track; if (tr && tr.length) tr = tr[0];
        if (tr && tr.name && tr['@attr'] && tr['@attr'].nowplaying === 'true') {
          show('playing', 'Now spinning', (tr.artist && (tr.artist['#text'] || tr.artist.name) || '') + ' – ' + tr.name);
        } else show('idle');
      }).catch(function () { if (!dead) show('idle'); });
    }
    load();
    timer = setInterval(function () { if (!document.hidden) load(); }, 30000);
    stopFns.push(function () { dead = true; });
  }
  var stopFns = [];

  function stop() {
    clearInterval(timer); timer = 0;
    stopFns.forEach(function (f) { f(); }); stopFns = [];
  }
  return { init: init, stop: stop };
})();
