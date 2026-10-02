window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]],
    processEscapes: true,
    processEnvironments: true
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex"
  }
};

// The first document$ emission is the initial page load, which MathJax's own
// startup pass already typesets; re-running it there is redundant and races
// that pass. Later emissions are Material's instant navigation: the swapped-in
// <head> detaches MathJax's cached stylesheet node, so its cache must be
// cleared or new glyph rules are inserted into a detached sheet (sheet === null)
// and the formulas render blank.
let initialLoad = true
document$.subscribe(() => {
  if (initialLoad) { initialLoad = false; return }
  if (!window.MathJax || !MathJax.startup || !MathJax.startup.promise) return

  MathJax.startup.promise = MathJax.startup.promise
    .then(() => {
      MathJax.startup.output.clearCache()
      MathJax.typesetClear()
      MathJax.texReset()
      return MathJax.typesetPromise()
    })
    .catch((err) => console.error("MathJax typeset failed:", err))
})
