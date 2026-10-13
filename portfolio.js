/* Progressive enhancement for architecture switching. */
(() => {
  const tabs = Array.from(document.querySelectorAll("[data-architecture]"));
  const panels = Array.from(document.querySelectorAll("[data-architecture-panel]"));
  if (!tabs.length || !panels.length) return;
  const activate = name => {
    tabs.forEach(tab => tab.setAttribute("aria-pressed", String(tab.dataset.architecture === name)));
    panels.forEach(panel => { panel.hidden = panel.dataset.architecturePanel !== name; });
  };
  tabs.forEach(tab => tab.addEventListener("click", () => activate(tab.dataset.architecture)));
  activate("vision");
})();
