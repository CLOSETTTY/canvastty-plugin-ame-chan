(() => {
  const cards = () => document.querySelectorAll('.plugin-canvas-card');
  const pluginFrame = (card) => card.querySelector('iframe[src*="//ame-chan-claude/"]');

  window.addEventListener('message', (event) => {
    if (event.data?.type !== 'ame-chan-picker' || typeof event.data.open !== 'boolean') return;
    for (const card of cards()) {
      const frame = pluginFrame(card);
      if (frame?.contentWindow === event.source) {
        card.classList.toggle('ame-chan-menu-open', event.data.open);
        return;
      }
    }
  });

  document.addEventListener('pointerdown', (event) => {
    for (const card of cards()) {
      if (!card.classList.contains('ame-chan-menu-open') || card.contains(event.target)) continue;
      card.classList.remove('ame-chan-menu-open');
      pluginFrame(card)?.contentWindow?.postMessage({ type: 'ame-chan-picker', open: false }, '*');
    }
  });
})();
