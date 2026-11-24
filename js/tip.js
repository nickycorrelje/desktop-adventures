
(function () {
  var t = document.querySelector('.tip'); if (!t) return;
  function m(e) { t.style.setProperty('--tx', e.clientX + 'px'); t.style.setProperty('--ty', e.clientY + 'px'); }
  t.addEventListener('mouseenter', m); t.addEventListener('mousemove', m);
})();
