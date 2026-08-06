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

  /* ---- section arrival: heading masked-line lift + lead fade, once ----
     One idiom, one curve. Headings only — body copy is never split.
     Hidden state lives under html.js, so no-JS renders everything visible. */
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var targets = [].slice.call(document.querySelectorAll('.sec h2, .mani blockquote, .phead h1'));

  targets.forEach(function (el) {
    if (el.tagName === 'H2' || el.tagName === 'H1') {
      // wrap each heading in a clipping mask so the line lifts from behind it
      var inner = document.createElement('span');
      inner.className = 'ml-i';
      while (el.firstChild) inner.appendChild(el.firstChild);
      el.appendChild(inner);
      el.classList.add('ml');
    }
    el.classList.add('rv');
  });

  function show(el) { el.classList.add('in'); }

  if (reduce || !('IntersectionObserver' in window)) {
    targets.forEach(show);
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        show(en.target);
        io.unobserve(en.target);          // once — never replays
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.01 });
    targets.forEach(function (el) { io.observe(el); });

    // failsafe: nothing inside (or just below) the viewport may stay invisible,
    // but leave far-below content to the observer so it still arrives on scroll
    function sweep() {
      targets.forEach(function (el) {
        if (el.getBoundingClientRect().top < window.innerHeight * 1.5) show(el);
      });
    }
    setTimeout(sweep, 2500);
    window.addEventListener('load', sweep);
    document.addEventListener('visibilitychange', function () {
      if (!document.hidden) sweep();
    });
    // absolute last resort — never leave the page with hidden text
    setTimeout(function () { targets.forEach(show); }, 10000);
  }

  /* nav surface appears once the page is scrolled */
  var nav = document.querySelector('.nav');
  function onScroll() { nav.classList.toggle('scrolled', window.scrollY > 8); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---- instagram strip ---- */
  var igs = document.querySelector('.igs');
  if (igs) {
    // pause off-screen via a CLASS, so :hover in the stylesheet still wins
    var igw = igs.querySelector('.igwrap');
    if (igw && 'IntersectionObserver' in window) {
      igs.classList.add('paused');
      new IntersectionObserver(function (es) {
        igs.classList.toggle('paused', !es[0].isIntersecting);
      }, { threshold: 0 }).observe(igw);
    }
    var tileImgs = [].slice.call(igs.querySelectorAll('.igt img'));

    // fade each tile in and drop its blur placeholder the moment it paints,
    // otherwise a slow tile sits there as a smear of 24px mush
    tileImgs.forEach(function (im) {
      function ok() { im.classList.add('ok'); im.parentNode.classList.add('ok'); }
      if (im.complete && im.naturalWidth > 0) ok();
      else {
        im.addEventListener('load', ok, { once: true });
        im.addEventListener('error', ok, { once: true });   // never leave mush on screen
      }
    });

    // The strip sits at the bottom of a very long page, so Chrome defers its
    // images even without loading="lazy" — tiles then drifted in as blur.
    // Warm all 12 URLs as soon as the strip is anywhere near the viewport.
    if ('IntersectionObserver' in window) {
      var warm = new IntersectionObserver(function (es) {
        if (!es[0].isIntersecting) return;
        warm.disconnect();
        var seen = {};
        tileImgs.forEach(function (im) {
          if (seen[im.src]) return;
          seen[im.src] = 1;
          if (im.fetchPriority !== undefined) im.fetchPriority = 'high';
          new Image().src = im.src;
        });
      }, { rootMargin: '900px 0px' });
      warm.observe(igs);
    }
  }

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
