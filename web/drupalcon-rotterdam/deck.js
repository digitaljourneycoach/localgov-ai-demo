// Keyboard controls for the deck.
// → / PageDown / Space : next slide      ← / PageUp : previous slide
// Home / End : first / last slide        N : speaker notes      F : full screen
// R : reveal (on the "spot the mistakes" slide)
(function () {
  var body = document.body;
  var prev = body.getAttribute('data-prev');
  var next = body.getAttribute('data-next');
  var first = body.getAttribute('data-first');
  var last = body.getAttribute('data-last');

  function go(url) { if (url) { window.location.href = url; } }

  function toggleNotes() {
    body.classList.toggle('show-notes');
    try { sessionStorage.setItem('deck-notes', body.classList.contains('show-notes') ? '1' : '0'); } catch (e) {}
  }
  try { if (sessionStorage.getItem('deck-notes') === '1') { body.classList.add('show-notes'); } } catch (e) {}

  function toggleReveal() {
    var target = document.querySelector('[data-reveal-target]');
    if (!target) { return; }
    target.classList.toggle('revealed');
    var btn = document.querySelector('[data-reveal]');
    if (btn) { btn.textContent = target.classList.contains('revealed') ? 'Hide the answers' : 'Reveal the mistakes'; }
  }
  var revealBtn = document.querySelector('[data-reveal]');
  if (revealBtn) { revealBtn.addEventListener('click', toggleReveal); }


  // Presenter checklist: remember ticks in this browser (best effort) and copy commands on click.
  var checks = document.querySelectorAll('[data-check]');
  Array.prototype.forEach.call(checks, function (box) {
    var key = 'deck-check-' + box.getAttribute('data-check');
    try { box.checked = localStorage.getItem(key) === '1'; } catch (e) {}
    box.addEventListener('change', function () {
      try { localStorage.setItem(key, box.checked ? '1' : '0'); } catch (e) {}
    });
  });
  var reset = document.querySelector('[data-reset]');
  if (reset) {
    reset.addEventListener('click', function () {
      Array.prototype.forEach.call(checks, function (box) {
        box.checked = false;
        try { localStorage.removeItem('deck-check-' + box.getAttribute('data-check')); } catch (e) {}
      });
    });
  }
  Array.prototype.forEach.call(document.querySelectorAll('[data-copy]'), function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault(); e.stopPropagation();
      var text = btn.getAttribute('data-copy');
      var done = function () { btn.classList.add('done'); setTimeout(function () { btn.classList.remove('done'); }, 1200); };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () {});
      }
    });
  });

  document.addEventListener('keydown', function (e) {
    if (e.metaKey || e.ctrlKey || e.altKey) { return; }
    var tag = (e.target && e.target.tagName) || '';
    if (tag === 'INPUT' || tag === 'TEXTAREA' || (e.target && e.target.isContentEditable)) { return; }
    switch (e.key) {
      case 'ArrowRight': case 'PageDown': case ' ': e.preventDefault(); go(next); break;
      case 'ArrowLeft': case 'PageUp': e.preventDefault(); go(prev); break;
      case 'Home': go(first); break;
      case 'End': go(last); break;
      case 'n': case 'N': toggleNotes(); break;
      case 'r': case 'R': toggleReveal(); break;
      case 'f': case 'F':
        if (!document.fullscreenElement) { document.documentElement.requestFullscreen && document.documentElement.requestFullscreen(); }
        else { document.exitFullscreen && document.exitFullscreen(); }
        break;
    }
  });
})();
