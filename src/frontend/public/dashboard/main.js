import { ApprovalInbox } from './approvalInbox.js';
import { ActionPreview } from './actionPreview.js';
import { GemPanel } from './gemPanel.js';

class GovernanceManager {
  constructor() {
    this.inbox = new ApprovalInbox({
      inboxEl: document.getElementById('approval-inbox'),
      countEl: document.getElementById('pending-count'),
      onDecide: (id, d) => this.decide(id, d),
      onView: (id) => this.view(id)
    });
    this.preview = new ActionPreview({ previewEl: document.getElementById('action-preview') });
    this.gems = new GemPanel({ gemEl: document.getElementById('gem-list') });
    this.preview.clear();
    document.getElementById('refresh-approvals')?.addEventListener('click', () => this.fetchApprovals());
    document.getElementById('clear-preview')?.addEventListener('click', () => this.preview.clear());
    this.poll();
    this.fetchGems();
  }

  async poll() {
    setInterval(() => this.fetchApprovals(), 5000);
    this.fetchApprovals();
  }

  updateTelemetry(approvals) {
    const total = approvals.length;
    const critical = approvals.filter((item) => Number(item.tier) >= 3).length;
    const tiers = approvals.map((item) => Number(item.tier)).sort((a, b) => a - b);
    const median = tiers.length ? tiers[Math.floor(tiers.length / 2)] : 0;
    const resonance = Math.max(35, 100 - total * 6 - critical * 10);
    const posture = critical > 0 ? 'Escalated' : total > 0 ? 'Observed' : 'Nominal';
    const pressure = total === 0 ? 'None' : total < 3 ? 'Focused' : total < 6 ? 'Elevated' : 'Saturated';
    const threatIndex = ((critical * 0.021) + (total * 0.004)).toFixed(3);
    const freshness = new Date().toISOString().replace('T', ' ').slice(0, 19) + ' UTC';

    document.getElementById('metric-pending').textContent = String(total);
    document.getElementById('metric-critical').textContent = String(critical);
    document.getElementById('metric-median-tier').textContent = `T${median}`;
    document.getElementById('metric-posture').textContent = posture;
    document.getElementById('diag-pressure').textContent = pressure;
    document.getElementById('diag-threat-index').textContent = threatIndex;
    document.getElementById('diag-freshness').textContent = freshness;
    document.getElementById('resonance-score').textContent = `${resonance.toFixed(1)}%`;
    document.getElementById('resonance-status').textContent = posture === 'Nominal' ? 'Stable' : posture === 'Observed' ? 'Monitored' : 'Escalated';
    document.getElementById('resonance-bar-fill').style.width = `${resonance}%`;

    const counts = [0, 0, 0, 0];
    approvals.forEach((item) => {
      const tier = Math.max(0, Math.min(3, Number(item.tier) || 0));
      counts[tier] += 1;
    });
    const max = Math.max(...counts, 1);
    document.querySelectorAll('#tier-chart .chart-bar').forEach((bar, index) => {
      const height = counts[index] ? 16 + (counts[index] / max) * 84 : 16;
      bar.style.height = `${height}%`;
      bar.style.borderTopColor = index >= 3 ? 'var(--error)' : index >= 2 ? 'var(--secondary)' : index >= 1 ? 'var(--primary)' : 'var(--tertiary-strong)';
      bar.style.background = index >= 3 ? 'rgba(255, 113, 108, 0.25)' : index >= 2 ? 'rgba(255, 116, 51, 0.22)' : index >= 1 ? 'rgba(153, 247, 255, 0.22)' : 'rgba(0, 252, 155, 0.18)';
    });
  }

  async fetchApprovals() {
    try {
      const res = await fetch('/governance/approvals');
      const data = await res.json();
      this.inbox.render(data);
      this.updateTelemetry(data);
    } catch (e) {
      console.error('Gov Link Failed', e);
    }
  }

  async fetchGems() {
    try {
      const res = await fetch('/governance/gems');
      const data = await res.json();
      this.gems.render(data.gems || []);
    } catch (e) {
      console.error('Gem Link Failed', e);
    }
  }

  async decide(id, decision) {
    await fetch('/governance/decide', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ request_id: id, decision })
    });
    this.fetchApprovals();
    this.preview.clear('Action processed.');
  }

  async view(id) {
    const res = await fetch('/governance/approvals');
    const approvals = await res.json();
    const app = approvals.find((a) => a.request_id === id);
    if (app) this.preview.renderApproval(app);
  }
}

window.governanceManager = new GovernanceManager();
