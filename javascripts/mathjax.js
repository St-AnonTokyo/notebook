window.MathJax = {
  loader: {load: ['[tex]/boldsymbol']},
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

document$.subscribe(() => {
  MathJax.typesetClear()
  MathJax.texReset()
  MathJax.typesetPromise()
})