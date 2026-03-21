const severityLabel = (tier) => {
  if (tier >= 3) return 'Critical';
  if (tier >= 2) return 'Warning';
  return 'Info';
};

const buildSummary = (app) => {
  const actor = app.actor || 'unknown actor';
  const intent = app.intent_id || 'no-intent-id';
  return `Governance review is required before ${actor} can continue ${app.action_type}. Intent ${intent} remains blocked until an explicit approval decision is recorded.`;
};

const previewKeys = (preview) => Object.keys(preview || {}).slice(0, 3);

export class ApprovalInbox {
  constructor({ inboxEl, countEl, onDecide, onView }) {
    this.inboxEl = inboxEl;
    this.countEl = countEl;
    this.onDecide = onDecide;
    this.onView = onView;
  }

  render(approvals) {
    this.countEl.textContent = String(approvals.length);
    if (approvals.length === 0) {
      this.inboxEl.innerHTML = '<div class="empty-state">No pending approvals.</div>';
      return;
    }

    this.inboxEl.innerHTML = approvals.map((app) => {
      const timestamp = app.created_at || 'Awaiting timestamp';
      const details = previewKeys(app.preview_data);
      return `
        <article class="approval-item" data-tier="${app.tier}">
          <div class="approval-top">
            <div>
              <div class="tier-tag">${severityLabel(app.tier)} · Tier ${app.tier}</div>
              <h3 class="approval-title">${app.action_type}</h3>
              <div class="approval-kicker">Governance approval required for actor ${app.actor || 'unknown'}.</div>
            </div>
            <div class="timeline-stamp">${timestamp}</div>
          </div>
          <p class="approval-summary">${buildSummary(app)}</p>
          <div class="approval-detail-grid">
            <div class="detail-card">
              <div class="detail-line">Intent ID</div>
              <div class="detail-value">${app.intent_id || 'N/A'}</div>
            </div>
            <div class="detail-card">
              <div class="detail-line">Actor</div>
              <div class="detail-value">${app.actor || 'N/A'}</div>
            </div>
            <div class="detail-card">
              <div class="detail-line">Preview fields</div>
              <div class="detail-value">${details.length ? details.join(', ') : 'No preview fields'}</div>
            </div>
          </div>
          <div class="approval-actions">
            <button class="btn-approve" data-action="approve" data-id="${app.request_id}">Approve</button>
            <button class="btn-reject" data-action="reject" data-id="${app.request_id}">Reject</button>
            <button class="btn-view" data-action="view" data-id="${app.request_id}">View preview</button>
            <button class="btn-dismiss" data-action="view" data-id="${app.request_id}">Inspect</button>
          </div>
        </article>`;
    }).join('');

    this.inboxEl.querySelectorAll('button[data-action]').forEach((btn) => {
      const id = btn.dataset.id;
      const action = btn.dataset.action;
      if (action === 'approve') btn.onclick = () => this.onDecide(id, 'APPROVED');
      if (action === 'reject') btn.onclick = () => this.onDecide(id, 'REJECTED');
      if (action === 'view') btn.onclick = () => this.onView(id);
    });
  }
}
