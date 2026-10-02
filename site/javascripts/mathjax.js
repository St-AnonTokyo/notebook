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

// Re-typeset formulas after Material's instant navigation. MathJax is loaded
// asynchronously, so on the first emission window.MathJax.startup does not
// exist yet -- bail out there and let MathJax's own startup pass handle that
// page instead of throwing.
document$.subscribe(() => {
  if (!window.MathJax || !MathJax.startup) return;

  MathJax.startup.promise = MathJax.startup.promise
    .then(() => {
      MathJax.typesetClear()
      MathJax.texReset()
      return MathJax.typesetPromise()
    })
    .catch((err) => console.error("MathJax typeset failed:", err))
})
