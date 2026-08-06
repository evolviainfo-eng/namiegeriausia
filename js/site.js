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

  /* instagram strip: only animate while it is actually on screen */
  var igw = document.querySelector('.igwrap'), igt = document.querySelector('.igtrack');
  if (igw && igt && 'IntersectionObserver' in window) {
    igt.style.animationPlayState = 'paused';
    new IntersectionObserver(function (es) {
      igt.style.animationPlayState = es[0].isIntersecting ? 'running' : 'paused';
    }, { threshold: 0 }).observe(igw);
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
