/* ═══════════════════════════════════════════════════════════
   Cyberpunk Edge-Runner Simulator — Frontend JavaScript
   ═══════════════════════════════════════════════════════════ */

// ── State ──────────────────────────────────────────────────────
const State = {
  data: null,

  set(d) {
    this.data = d;
    this.renderAll();
  },

  get() { return this.data; },

  renderAll() {
    const s = this.data;
    if (!s) return;
    renderHUD(s);
    renderDashboard(s);
    renderGigs(s);
    renderShop(s);
    renderTrauma(s);
    if (s.game_over) {
      showGameOver(s);
    } else {
      hideGameOver();
    }
  }
};

// ── API ────────────────────────────────────────────────────────
const API = {
  async get(path) {
    const r = await fetch(path);
    if (!r.ok) throw new Error(`API ${r.status}: ${r.statusText}`);
    return r.json();
  },

  async post(path, body = {}) {
    const r = await fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!r.ok) throw new Error(`API ${r.status}: ${r.statusText}`);
    return r.json();
  },

  async status()       { return this.get('/api/status'); },
  async executeJob(id) { return this.post('/api/gig', { id }); },
  async buy(id)        { return this.post('/api/buy', { id }); },
  async uninstall(id)  { return this.post('/api/uninstall', { id }); },
  async heal()         { return this.post('/api/heal', {}); },
  async rest()         { return this.post('/api/rest', {}); },
  async restart()      { return this.post('/api/restart', {}); },
};

// ── Actions (button handlers) ──────────────────────────────────
const Actions = {
  async executeJob(jobId) {
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'RUNNING...';
    try {
      const result = await API.executeJob(jobId);
      showModal(result);
      State.set(result.state);
    } catch (e) {
      showNotification('Connection Error', e.message, 'error');
    }
    btn.disabled = false;
    btn.textContent = 'EXECUTE';
  },

  async buy(id) {
    const btn = event.target;
    btn.disabled = true;
    try {
      const result = await API.buy(id);
      showModal(result);
      State.set(result.state);
    } catch (e) {
      showNotification('Connection Error', e.message, 'error');
    }
    btn.disabled = false;
  },

  async uninstall(id) {
    const btn = event.target;
    btn.disabled = true;
    try {
      const result = await API.uninstall(id);
      showModal(result);
      State.set(result.state);
    } catch (e) {
      showNotification('Connection Error', e.message, 'error');
    }
    btn.disabled = false;
  },

  async heal() {
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'CALLING...';
    try {
      const result = await API.heal();
      showModal(result);
      State.set(result.state);
    } catch (e) {
      showNotification('Connection Error', e.message, 'error');
    }
    btn.disabled = false;
    btn.textContent = 'CALL TRAUMA TEAM';
  },

  async rest() {
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'RESTING...';
    try {
      const result = await API.rest();
      showModal(result);
      State.set(result.state);
    } catch (e) {
      showNotification('Connection Error', e.message, 'error');
    }
    btn.disabled = false;
    btn.textContent = 'REST';
  },
};

// ── HUD ────────────────────────────────────────────────────────
function renderHUD(s) {
  document.getElementById('hud-money').textContent = `$${s.money.toLocaleString()}`;
  const hpColor = s.hp > 50 ? '#00ff88' : (s.hp > 20 ? '#fbbf24' : '#ff0044');
  document.getElementById('hud-hp').innerHTML = `<span style="color:${hpColor}">HP: ${s.hp}/100</span>`;
  const hc = s.humanity_color || '#00ff88';
  const hl = s.humanity > 70 ? 'STABLE' : (s.humanity > 40 ? 'ERODING' : 'CRITICAL');
  document.getElementById('hud-humanity').innerHTML = `<span style="color:${hc}">HUM: ${s.humanity}% ${hl}</span>`;
  document.getElementById('hud-combat').textContent = `COMBAT +${s.combat_bonus}`;
  document.getElementById('hud-day').textContent = `DAY ${s.day}`;
}

// ── Dashboard ──────────────────────────────────────────────────
function renderDashboard(s) {
  // HP bar
  const hpPct = Math.max(0, Math.min(100, s.hp));
  const hpColor = hpPct > 50 ? '#00ff88' : (hpPct > 20 ? '#fbbf24' : '#ff0044');
  document.getElementById('dash-hp-bar').style.width = hpPct + '%';
  document.getElementById('dash-hp-bar').style.background = hpColor;
  document.getElementById('dash-hp-val').textContent = s.hp + '/100';
  document.getElementById('dash-hp-val').style.color = hpColor;

  // Humanity bar
  const humPct = Math.max(0, Math.min(100, s.humanity));
  document.getElementById('dash-humanity-bar').style.width = humPct + '%';
  document.getElementById('dash-humanity-bar').style.background = s.humanity_color || '#00ff88';
  document.getElementById('dash-humanity-val').textContent = s.humanity + '%';
  document.getElementById('dash-humanity-val').style.color = s.humanity_color || '#00ff88';

  // Money & Combat
  document.getElementById('dash-money').textContent = '$' + s.money.toLocaleString();
  document.getElementById('dash-combat').textContent = '+' + s.combat_bonus;

  // Cyberware list
  const cwDiv = document.getElementById('dash-cyberware');
  if (s.owned.length === 0) {
    cwDiv.innerHTML = '<span style="color:#444;font-size:0.8rem;">No cyberware installed.</span>';
  } else {
    cwDiv.innerHTML = s.owned.map(c =>
      `<div style="padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04);display:flex;align-items:center;gap:8px;">
        <span style="color:var(--blue);">▸</span>
        <span style="color:var(--blue);font-size:0.85rem;">${esc(c.name)}</span>
      </div>`
    ).join('');
  }
}

// ── Fixer Market (Gigs) ────────────────────────────────────────
function renderGigs(s) {
  const container = document.getElementById('gig-list');
  if (!window.GAME_JOBS) return;
  container.innerHTML = window.GAME_JOBS.map(j => {
    const riskClass = 'risk-' + j.risk_level;
    const effectiveDiff = Math.max(5, j.base_difficulty - s.combat_bonus);
    const successChance = clamp(15, 90, 50 + s.combat_bonus * 2 - j.base_difficulty / 2);
    return `<div class="gig-card ${riskClass}">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
        <div>
          <div style="font-size:0.9rem;font-weight:700;color:#fff;margin-bottom:4px;">${esc(j.name)}</div>
          <div style="font-size:0.72rem;color:#666;line-height:1.4;margin-bottom:6px;">${esc(j.description)}</div>
          <div style="display:flex;gap:12px;flex-wrap:wrap;">
            <span class="text-xs" style="color:#555;font-size:0.7rem;">Risk: <span class="${riskClass}" style="font-weight:600;">${j.risk_level}</span></span>
            <span style="color:#555;font-size:0.7rem;">Diff: ${effectiveDiff}</span>
            <span style="color:var(--green);font-size:0.7rem;">Chance: ${successChance}%</span>
          </div>
        </div>
        <div style="text-align:right;">
          <div style="font-size:0.75rem;color:#888;margin-bottom:4px;">$${j.reward_range[0].toLocaleString()}-$${j.reward_range[1].toLocaleString()}</div>
          <button class="btn btn-pink" onclick="Actions.executeJob('${j.id}')" ${s.game_over ? 'disabled' : ''}>EXECUTE</button>
        </div>
      </div>
    </div>`;
  }).join('');
}

// ── Ripperdoc Clinic (Shop) ────────────────────────────────────
function renderShop(s) {
  const container = document.getElementById('shop-list');
  if (!window.GAME_CYBERWARE) return;
  const ownedIds = s.owned.map(c => c.id);
  container.innerHTML = Object.entries(window.GAME_CYBERWARE).map(([uid, item]) => {
    const owned = ownedIds.includes(uid);
    const canBuy = s.money >= item.price;
    const classes = owned ? 'shop-card owned' : 'shop-card';
    let statusHTML;
    if (owned) {
      statusHTML = `<span style="color:var(--green);font-size:0.75rem;font-weight:600;">[INSTALLED]</span>`;
    } else if (canBuy) {
      statusHTML = `<span style="color:#fbbf24;font-size:0.75rem;">CAN AFFORD</span>`;
    } else {
      statusHTML = `<span style="color:#f87171;font-size:0.75rem;">NEED $${item.price.toLocaleString()}</span>`;
    }
    let btns = '';
    if (owned) {
      btns = `<button class="btn btn-blue" onclick="Actions.uninstall('${uid}')" ${s.game_over ? 'disabled' : ''}>UNINSTALL</button>`;
    } else {
      btns = `<button class="btn btn-green" onclick="Actions.buy('${uid}')" ${s.game_over || !canBuy ? 'disabled' : ''}>BUY $${item.price.toLocaleString()}</button>`;
    }
    return `<div class="${classes}">
      <div>
        <div style="font-size:0.85rem;font-weight:700;color:#fff;margin-bottom:2px;">${esc(item.name)}</div>
        <div style="font-size:0.72rem;color:#555;">${esc(item.description)}</div>
        <div style="font-size:0.7rem;color:var(--green);margin-top:2px;">+${item.combat_bonus} combat</div>
      </div>
      <div style="text-align:right;display:flex;flex-direction:column;align-items:flex-end;gap:6px;">
        ${statusHTML}
        ${btns}
      </div>
    </div>`;
  }).join('');
}

// ── Trauma Team ────────────────────────────────────────────────
function renderTrauma(s) {
  // Buttons are disabled inline in the render templates
}

// ── Tab Switching ──────────────────────────────────────────────
function initTabs() {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const tabId = btn.dataset.tab;
      document.querySelectorAll('.tab-panel').forEach(p => {
        p.classList.toggle('hidden', p.id !== 'panel-' + tabId);
      });
    });
  });
}

// ── Game Over Overlay ──────────────────────────────────────────
function showGameOver(s) {
  const overlay = document.getElementById('gameover-overlay');
  overlay.classList.remove('hidden');
  document.getElementById('gameover-reason').textContent = s.game_over_reason || 'Your humanity has evaporated.';
  const cyberNames = s.owned.map(c => esc(c.name)).join(', ') || 'None';
  document.getElementById('gameover-stats').innerHTML = `
    <div>Money: <span style="color:var(--pink);">${s.money.toLocaleString()}ed</span></div>
    <div>Humanity: <span style="color:${s.humanity_color};">${s.humanity}%</span></div>
    <div>Combat Bonus: <span style="color:var(--green);">+${s.combat_bonus}</span></div>
    <div>Cyberware: ${cyberNames}</div>
  `;
}

function hideGameOver() {
  document.getElementById('gameover-overlay').classList.add('hidden');
}

// ── Notification Modal ─────────────────────────────────────────
function showNotification(title, body, type) {
  const modal = document.getElementById('notification-modal');
  const boxClass = type === 'success' ? 'success' : type === 'error' ? 'error' : 'info';
  const titleColor = type === 'success' ? 'var(--green)' : type === 'error' ? '#f87171' : 'var(--blue)';
  modal.innerHTML = `
    <div class="modal-backdrop" onclick="this.remove()">
      <div class="modal-box ${boxClass}" onclick="event.stopPropagation()">
        <h3 style="color:${titleColor};margin:0 0 12px;font-size:1rem;letter-spacing:1px;text-transform:uppercase;">${esc(title)}</h3>
        <p style="color:#bbb;margin:0 0 20px;font-size:0.85rem;line-height:1.6;">${esc(body)}</p>
        <button class="btn ${boxClass === 'success' ? 'btn-green' : boxClass === 'error' ? 'btn-pink' : 'btn-blue'}" onclick="this.closest('.modal-backdrop').remove()" style="width:100%;">ACK</button>
      </div>
    </div>
  `;
}

// ── Action Modal (for game results) ────────────────────────────
function showModal(result) {
  if (!result) return;
  const job = result.job_result;
  if (job) {
    const isOk = job.success;
    const type = isOk ? 'success' : 'error';
    let body = `<p style="margin:0 0 8px;">${isOk ? 'MISSION COMPLETE' : 'MISSION FAILED'}: <strong>${esc(job.job_name)}</strong></p>`;
    if (isOk) {
      body += `<p style="margin:0;">Reward: <span style="color:var(--pink);">+$${job.reward.toLocaleString()}</span> | Humanity: <span style="color:#f87171;">-${job.humanity_cost}%</span></p>`;
      body += `<p style="color:#555;margin-top:4px;">Roll: ${job.roll} | Chance: ${job.success_chance}% | Risk: ${job.risk_level}</p>`;
    } else {
      body += `<p style="margin:0 0 4px;">Lost <span style="color:#f87171;">$${job.loss.toLocaleString()}</span> | Humanity: <span style="color:#f87171;">-${job.humanity_cost}%</span> | HP: <span style="color:#f87171;">-${job.hp_cost}</span></p>`;
      body += `<p style="color:#555;">Roll: ${job.roll} | Chance: ${job.success_chance}% | Risk: ${job.risk_level}</p>`;
    }
    showNotification(result.message, body, type);
    return;
  }
  // Non-job actions (buy, sell, heal, rest)
  const type = result.success ? 'success' : 'error';
  showNotification(result.success ? 'Action Complete' : 'Action Failed', result.message, type);
}

// ── Utils ──────────────────────────────────────────────────────
function clamp(lo, hi, val) {
  return Math.max(lo, Math.min(hi, val));
}

function esc(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// ── Init ───────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  initTabs();

  // Cinematic overlay auto-dismiss
  setTimeout(() => {
    const overlay = document.getElementById('cinematic-overlay');
    if (overlay) {
      overlay.style.transition = 'opacity 0.8s';
      overlay.style.opacity = '0';
      setTimeout(() => overlay.remove(), 800);
    }
  }, 4000);

  // Load initial state
  try {
    const s = await API.status();
    State.set(s);
  } catch (e) {
    showNotification('Connection Error', 'Could not connect to server. Is the backend running?', 'error');
  }
});
