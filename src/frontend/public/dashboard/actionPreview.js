export class ActionPreview {
  constructor({ previewEl }) {
    this.previewEl = previewEl;
  }

  clear(message = 'Select a pending action to preview impact.') {
    this.previewEl.textContent = message;
  }

  renderApproval(approval) {
    const lines = [
      `>>> PREVIEW: ${approval.action_type}`,
      `Intent ID: ${approval.intent_id || 'N/A'}`,
      `Actor: ${approval.actor || 'N/A'}`,
      `Tier: ${approval.tier}`,
      '',
      JSON.stringify(approval.preview_data || {}, null, 2)
    ];

    this.previewEl.innerHTML = `
      <div class="preview-header">${lines.slice(0, 4).join('<br>')}</div>
      <div class="preview-block">${JSON.stringify(approval.preview_data || {}, null, 2)}</div>
    `;
  }
}
