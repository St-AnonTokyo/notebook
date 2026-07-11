(function () {
  var prefetched = new Set();
  var timer = null;

  function prefetchImages(href) {
    if (prefetched.has(href)) return;
    prefetched.add(href);

    fetch(href)
      .then(function (res) { return res.text(); })
      .then(function (html) {
        var doc = new DOMParser().parseFromString(html, "text/html");
        var imgs = doc.querySelectorAll("img[src]");
        imgs.forEach(function (img) {
          var src = img.getAttribute("src");
          if (!src || src.startsWith("data:") || src.startsWith("blob:")) return;
          var url = new URL(src, href).href;
          if (url.startsWith(window.location.origin)) {
            var link = document.createElement("link");
            link.rel = "prefetch";
            link.as = "image";
            link.href = url;
            document.head.appendChild(link);
          }
        });
      })
      .catch(function () {});
  }

  function handleHover(e) {
    var link = e.target.closest("a[href]");
    if (!link) return;
    try {
      var url = new URL(link.href);
      if (url.origin !== window.location.origin) return;
      if (url.pathname === window.location.pathname) return;
    } catch (e) { return; }

    clearTimeout(timer);
    timer = setTimeout(function () { prefetchImages(link.href); }, 50);
  }

  function handleFocus(e) {
    var link = e.target.closest("a[href]");
    if (!link) return;
    try {
      var url = new URL(link.href);
      if (url.origin !== window.location.origin) return;
      if (url.pathname === window.location.pathname) return;
    } catch (e) { return; }

    clearTimeout(timer);
    prefetchImages(link.href);
  }

  document.addEventListener("mouseover", handleHover);
  document.addEventListener("mouseout", function () { clearTimeout(timer); });
  document.addEventListener("focusin", handleFocus);
})();
