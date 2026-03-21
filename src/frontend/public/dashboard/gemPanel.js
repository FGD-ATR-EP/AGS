export class GemPanel {
  constructor({ gemEl }) {
    this.gemEl = gemEl;
  }

  render(gems = []) {
    if (!gems.length) {
      this.gemEl.innerHTML = '<div class="gem-card"><div class="gem-title">No gems yet</div><div class="gem-principle">Awaiting approvals and reflection.</div></div>';
      return;
    }
    this.gemEl.innerHTML = gems.map(g => `
      <div class="gem-card">
        <div class="gem-title">${g.title} (${g.status})</div>
        <div class="gem-principle">"${g.principle}"</div>
      </div>
    `).join('');
  }
}
