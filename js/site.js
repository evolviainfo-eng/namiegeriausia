/* NAMIE geriausia — minimal runtime */
(function () {
  var de = document.documentElement;
  de.classList.add('js');

  /* hero reveal: once, on fonts ready (safety at 2500ms regardless) */
  function on() { de.classList.add('is-on'); }
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(function () { setTimeout(on, 60); });
  } else { setTimeout(on, 300); }
  setTimeout(on, 2500);

  /* nav surface appears once the page is scrolled */
  var nav = document.querySelector('.nav');
  function onScroll() { nav.classList.toggle('scrolled', window.scrollY > 8); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* contact form -> mailto compose + inline confirmation */
  var f = document.getElementById('cf');
  if (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var v = function (id) { return (document.getElementById(id) || {}).value || ''; };
      var body = 'Vardas: ' + v('cf-name') + '\nKontaktas: ' + v('cf-tel') + '\n\n' + v('cf-msg');
      var url = 'mailto:brigita@namiegeriausia.lt' +
        '?subject=' + encodeURIComponent('Užklausa dėl interjero projekto') +
        '&body=' + encodeURIComponent(body);
      var m = document.getElementById('cf-note');
      if (m) m.textContent = 'Atsidarys jūsų pašto programa. Jei neatsidarė — parašykite brigita@namiegeriausia.lt arba skambinkite +370 680 20901.';
      window.location.href = url;
    });
  }
})();
