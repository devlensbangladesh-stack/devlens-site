// Devlens: keeps dates and job listings current in the visitor's browser, using Dhaka time.
(function () {
  var fmt = function (opts) { return new Intl.DateTimeFormat('en-GB', Object.assign({ timeZone: 'Asia/Dhaka' }, opts)); };
  var now = new Date();
  var today = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Dhaka' }).format(now); // YYYY-MM-DD
  var days = function (a, b) { return Math.round((Date.parse(b) - Date.parse(a)) / 86400000); };
  var longDate = function (iso) { return fmt({ day: 'numeric', month: 'long', year: 'numeric' }).format(new Date(iso + 'T12:00:00+06:00')); };
  var shortDate = function (iso) { return fmt({ day: 'numeric', month: 'short', year: 'numeric' }).format(new Date(iso + 'T12:00:00+06:00')); };
  var label = function (d) {
    if (!d) return ['OPEN', '#6b6f76', false];
    var n = days(today, d);
    if (n <= 0) return ['CLOSES TODAY', '#c2410c', true];
    if (n === 1) return ['CLOSES TOMORROW', '#c2410c', true];
    if (n <= 7) return ['CLOSES THIS WEEK', '#b45309', true];
    return ['DEADLINE', '#0b8f68', false];
  };
  var setAll = function (sel, val) { document.querySelectorAll(sel).forEach(function (el) { el.textContent = val; }); };

  // Header date
  var td = document.getElementById('today-date');
  if (td) td.innerHTML = fmt({ weekday: 'long' }).format(now) + '<br>' + longDate(today);

  // Mobile menu
  var tg = document.querySelector('.menu-toggle'), nav = document.getElementById('site-nav');
  if (tg && nav) tg.addEventListener('click', function () { var o = nav.classList.toggle('open'); tg.setAttribute('aria-expanded', o); });

  // Jobs page
  var cards = Array.prototype.slice.call(document.querySelectorAll('article.job[data-deadline]'));
  if (cards.length) {
    cards.forEach(function (c) {
      var d = c.dataset.deadline;
      if (d && d < today) { c.remove(); return; }
      var l = label(d), el = c.querySelector('[data-label]');
      if (el) { el.textContent = l[0]; el.style.color = l[1]; }
      var nw = c.querySelector('[data-new]'); if (nw) nw.hidden = c.dataset.added !== today;
    });
    var live = Array.prototype.slice.call(document.querySelectorAll('article.job'));
    var bySector = {};
    live.forEach(function (c) { bySector[c.dataset.sector] = (bySector[c.dataset.sector] || 0) + 1; });
    document.querySelectorAll('section.sector[data-sector]').forEach(function (s) { if (!bySector[s.dataset.sector]) s.remove(); });
    document.querySelectorAll('[data-chip]').forEach(function (a) { if (!bySector[a.dataset.chip]) a.remove(); });
    Object.keys(bySector).forEach(function (k) { setAll('[data-sector-count="' + k + '"]', bySector[k]); });
    var soon = live.filter(function (c) { return c.dataset.deadline && days(today, c.dataset.deadline) <= 7; })
      .sort(function (a, b) { return a.dataset.deadline.localeCompare(b.dataset.deadline); });
    var orgs = {}; live.forEach(function (c) { orgs[c.dataset.badge] = 1; });
    setAll('[data-stat="open"]', live.length);
    setAll('[data-stat="soon"]', soon.length);
    setAll('[data-stat="nationals"]', live.filter(function (c) { return c.dataset.nationals; }).length);
    setAll('[data-stat="orgs"]', Object.keys(orgs).length);
    setAll('[data-today-long]', longDate(today));
    var wk = new Date(Date.parse(today) + 7 * 86400000).toISOString().slice(0, 10);
    setAll('[data-week-out]', fmt({ day: 'numeric', month: 'long' }).format(new Date(wk + 'T12:00:00+06:00')));
    var grid = document.getElementById('soon-grid');
    if (grid) {
      grid.innerHTML = '';
      soon.forEach(function (c) {
        var l = label(c.dataset.deadline), a = document.createElement('a');
        a.className = 'mini'; a.href = c.dataset.url; a.style.borderTopColor = l[1];
        var s1 = document.createElement('span'); s1.className = 'lab'; s1.style.color = l[1]; s1.textContent = l[0] + ' · ' + shortDate(c.dataset.deadline);
        var s2 = document.createElement('span'); s2.className = 't'; s2.textContent = c.dataset.title;
        var s3 = document.createElement('span'); s3.className = 'o'; s3.textContent = c.dataset.org + ' · ' + c.dataset.location;
        a.appendChild(s1); a.appendChild(s2); a.appendChild(s3); grid.appendChild(a);
      });
    }
  }

  // Homepage: hide anything whose deadline has passed and recount jobs
  document.querySelectorAll('[data-job-deadline]').forEach(function (el) {
    var d = el.dataset.jobDeadline; if (d && d < today) el.remove();
  });
  var jd = document.getElementById('jobs-data');
  if (jd) {
    try {
      var all = JSON.parse(jd.textContent), open = all.filter(function (j) { return !j.d || j.d >= today; });
      setAll('[data-open-jobs]', open.length);
      var bs = {}; open.forEach(function (j) { bs[j.s] = (bs[j.s] || 0) + 1; });
      document.querySelectorAll('[data-sector-count]').forEach(function (el) {
        var n = bs[el.dataset.sectorCount] || 0;
        if (!n && el.closest('a')) el.closest('a').remove(); else el.textContent = n;
      });
    } catch (e) {}
  }
})();
