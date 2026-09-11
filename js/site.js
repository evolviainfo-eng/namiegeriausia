/* NAMIE geriausia · minimal runtime */
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
     One idiom, one curve. Headings only; body copy is never split.
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
        io.unobserve(en.target);          // once, never replays
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
    // absolute last resort: never leave the page with hidden text
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
    var igw = igs.querySelector('.igwrap');
    var igtrack = igs.querySelector('.igtrack');
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
    // images even without loading="lazy", so tiles drifted in as blur.
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

    /* ---- the drift ----
       The animation itself is pure CSS on the compositor. JS only sets its
       duration from the measured width, so the strip travels at the same
       pixels-per-second on a phone as on a 27" display, and only lets it run
       while it is actually on screen. */
    if (igtrack && !reduce) {
      // Below roughly 1px per frame the eye reads shimmer, not glide: at 34px/s
      // the strip moved 0.57px a frame and the captions crawled. 78px/s puts it
      // at ~1.3px a frame, which reads as deliberate, continuous motion.
      var PPS = 78;                                        // pixels per second

      function setSpeed() {
        var half = igtrack.scrollWidth / 2;                // one full copy
        if (half > 0) igtrack.style.animationDuration = (half / PPS).toFixed(1) + 's';
      }
      setSpeed();
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(setSpeed);
      window.addEventListener('load', setSpeed);

      var rt;
      window.addEventListener('resize', function () {
        clearTimeout(rt); rt = setTimeout(setSpeed, 200);
      }, { passive: true });

      if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (es) {
          igs.classList.toggle('go', es[0].isIntersecting);  // no work off-screen
        }, { threshold: 0 }).observe(igs);
      } else {
        igs.classList.add('go');
      }
    }
  }


  /* ---- lightbox: project photography only ----
     Bound to .pgal, which is the project gallery and nothing else, so the
     Instagram tiles keep opening Instagram and are never pulled in here. */
  var lbGal = [].slice.call(document.querySelectorAll('.pgal figure img'));
  if (lbGal.length) {
    function lbIcon(d) {
      return '<lbIcon viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" ' +
             'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
             '<path d="' + d + '"/></lbIcon>';
    }

    var lb = document.createElement('div');
    lb.className = 'lb';
    lb.hidden = true;
    lb.setAttribute('role', 'dialog');
    lb.setAttribute('aria-modal', 'true');
    lb.setAttribute('aria-label', 'Projekto nuotrauka');
    lb.innerHTML =
      '<figure class="lb-fig"><img class="lb-img" alt="">' +
      '<figcaption class="lb-cap"></figcaption></figure>' +
      '<button class="lb-prev" type="button" aria-label="Ankstesnė nuotrauka">' +
        lbIcon('M15 5 8 12l7 7') + '</button>' +
      '<button class="lb-next" type="button" aria-label="Kita nuotrauka">' +
        lbIcon('M9 5l7 7-7 7') + '</button>' +
      '<button class="lb-x" type="button" aria-label="Uždaryti">' +
        lbIcon('M6 6l12 12M18 6L6 18') + '</button>';
    document.body.appendChild(lb);

    var lbImg = lb.querySelector('.lb-img'),
        lbCap = lb.querySelector('.lb-cap'),
        bPrev = lb.querySelector('.lb-prev'),
        bNext = lb.querySelector('.lb-next'),
        bX = lb.querySelector('.lb-x'),
        lbIdx = 0, opener = null;

    // the lbLargest file the srcset offers, so full screen is never an upscale of
    // whatever variant the grid happened to pick
    function lbLargest(img) {
      var best = img.currentSrc || img.src, w = 0;
      (img.getAttribute('srcset') || '').split(',').forEach(function (part) {
        var m = part.trim().match(/^(\S+)\s+(\d+)w$/);
        if (m && +m[2] > w) { w = +m[2]; best = m[1]; }
      });
      return best;
    }

    function lbWarm(i) {
      var n = lbGal[(i + lbGal.length) % lbGal.length];
      if (n) { new Image().src = lbLargest(n); }
    }

    function lbShow(i) {
      lbIdx = (i + lbGal.length) % lbGal.length;
      var from = lbGal[lbIdx];
      lbImg.src = lbLargest(from);
      lbImg.alt = from.alt || '';
      lbCap.textContent = from.alt || '';
      lbWarm(lbIdx + 1); lbWarm(lbIdx - 1);          // next swipe is already in cache
    }

    function lbOpen(i, trigger) {
      opener = trigger || null;
      lbShow(i);
      lb.hidden = false;
      void lb.offsetHeight;                  // give the fade a start value to run from
      lb.classList.add('on');
      de.classList.add('lb-lbOpen');
      bX.focus();
    }

    function lbClose() {
      lb.classList.remove('on');
      de.classList.remove('lb-lbOpen');
      var done = function () { lb.hidden = true; lbImg.removeAttribute('src'); };
      if (reduce) { done(); } else { setTimeout(done, 240); }
      if (opener) { opener.focus(); }
    }

    lbGal.forEach(function (img, i) {
      img.setAttribute('role', 'button');
      img.setAttribute('tabindex', '0');
      img.setAttribute('aria-label', (img.alt || 'Nuotrauka') + ', atidaryti per visą ekraną');
      img.addEventListener('click', function () { lbOpen(i, img); });
      img.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); lbOpen(i, img); }
      });
    });

    bPrev.addEventListener('click', function () { lbShow(lbIdx - 1); });
    bNext.addEventListener('click', function () { lbShow(lbIdx + 1); });
    bX.addEventListener('click', lbClose);

    // a click on the ground closes; the photo, its caption and the controls do not
    lb.addEventListener('click', function (e) {
      if (!e.target.closest('.lb-fig, button')) { lbClose(); }
    });

    document.addEventListener('keydown', function (e) {
      if (lb.hidden) return;
      if (e.key === 'Escape') { lbClose(); }
      else if (e.key === 'ArrowLeft') { lbShow(lbIdx - 1); }
      else if (e.key === 'ArrowRight') { lbShow(lbIdx + 1); }
      else if (e.key === 'Tab') {
        // hold focus inside the dialog while it is lbOpen
        var f = [bPrev, bNext, bX].filter(function (b) { return b.offsetParent !== null; });
        var at = f.indexOf(document.activeElement);
        e.preventDefault();
        f[(at + (e.shiftKey ? -1 : 1) + f.length) % f.length].focus();
      }
    });

    var sx = 0, sy = 0, swiping = false;
    lb.addEventListener('touchstart', function (e) {
      swiping = e.touches.length === 1;
      if (swiping) { sx = e.touches[0].clientX; sy = e.touches[0].clientY; }
    }, { passive: true });
    lb.addEventListener('touchend', function (e) {
      if (!swiping) return;
      swiping = false;
      var t = e.changedTouches[0], dx = t.clientX - sx, dy = t.clientY - sy;
      // horizontal intent only, so a vertical flick never flips the photo
      if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy) * 1.5) {
        lbShow(lbIdx + (dx < 0 ? 1 : -1));
      }
    }, { passive: true });
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
      if (m) m.textContent = 'Atsidarys jūsų pašto programa. Jei neatsidarė, parašykite brigita@namiegeriausia.lt arba skambinkite +370 680 20901.';
      window.location.href = url;
    });
  }
})();
