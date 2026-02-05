# SPRINT-E: Wire Up High-Priority Backend Features

**Priority**: MEDIUM-HIGH
**Estimated Time**: 1.5 hours
**Depends On**: Sprints A-D complete
**Test After**: KB injection preview works, flight lifecycle controls work, worker status visible

---

## Context

The backend has many features with no UI. This sprint wires up the highest-priority ones.

Reference: `2026-01-23-SPRINT-021-ANALYSIS.md` TASK-099, TASK-100, TASK-103

---

## Tasks

### E1: KB Preview Injection

**Backend**: POST /api/kb/preview, GET /api/kb/entities
**Priority**: High - core RAQCOON feature

Add a KB panel that lets users preview what will be injected into a task.

**CSS to add**:
```css
/* KB Panel */
.kb-panel {
  position: fixed;
  right: 0;
  top: 44px;
  bottom: 0;
  width: 320px;
  background: var(--ink-800);
  border-left: 1px solid var(--panel-border);
  transform: translateX(100%);
  transition: transform 0.2s ease;
  z-index: 100;
  display: flex;
  flex-direction: column;
}

.kb-panel.open {
  transform: translateX(0);
}

.kb-panel-header {
  padding: 12px 16px;
  border-bottom: 1px solid var(--panel-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.kb-panel-header h3 {
  font-size: 14px;
  font-weight: 600;
}

.kb-panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.kb-entity {
  padding: 10px 12px;
  background: var(--ink-900);
  border: 1px solid var(--panel-border);
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
}

.kb-entity:hover {
  border-color: var(--brand-400);
}

.kb-entity.selected {
  border-color: var(--mint-500);
  background: rgba(31, 199, 177, 0.1);
}

.kb-entity-title {
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 4px;
}

.kb-entity-type {
  font-size: 10px;
  text-transform: uppercase;
  color: var(--ink-400);
  margin-bottom: 4px;
}

.kb-entity-summary {
  font-size: 11px;
  color: var(--ink-400);
  line-height: 1.4;
}

.kb-preview-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--panel-border);
}

.kb-preview-section h4 {
  font-size: 12px;
  color: var(--ink-400);
  margin-bottom: 8px;
}

.kb-preview-content {
  background: var(--ink-900);
  border: 1px solid var(--panel-border);
  border-radius: 8px;
  padding: 12px;
  font-family: var(--font-mono, monospace);
  font-size: 11px;
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
}
```

**HTML to add**:
```html
<!-- KB Panel -->
<div class="kb-panel" id="kbPanel">
  <div class="kb-panel-header">
    <h3>📚 Knowledge Base</h3>
    <button class="gate-modal-close" onclick="toggleKBPanel()">&times;</button>
  </div>
  <div class="kb-panel-body">
    <div class="kb-entities" id="kbEntities">
      <div style="color:var(--ink-400);font-size:12px;">Loading entities...</div>
    </div>
    <div class="kb-preview-section">
      <h4>Preview Injection</h4>
      <div class="kb-preview-content" id="kbPreview">Select entities above to preview injection...</div>
    </div>
  </div>
</div>
```

**JS to add**:
```javascript
// ═══════════════════════════════════════════════════════════════
// KB PANEL
// ═══════════════════════════════════════════════════════════════

let kbEntities = [];
let selectedKBEntities = new Set();

function toggleKBPanel() {
  const panel = document.getElementById('kbPanel');
  panel.classList.toggle('open');
  if (panel.classList.contains('open')) {
    loadKBEntities();
  }
}

async function loadKBEntities() {
  try {
    const resp = await fetch(`${API}/api/kb/entities`);
    const data = await resp.json();
    kbEntities = data.entities || [];
    renderKBEntities();
  } catch (err) {
    document.getElementById('kbEntities').innerHTML = 
      `<div style="color:var(--rose-500);font-size:12px;">Failed to load: ${err.message}</div>`;
  }
}

function renderKBEntities() {
  const container = document.getElementById('kbEntities');
  
  if (kbEntities.length === 0) {
    container.innerHTML = '<div style="color:var(--ink-400);font-size:12px;">No KB entities found</div>';
    return;
  }
  
  container.innerHTML = kbEntities.map(entity => `
    <div class="kb-entity ${selectedKBEntities.has(entity.id) ? 'selected' : ''}" 
         onclick="toggleKBEntity('${escapeHtml(entity.id)}')">
      <div class="kb-entity-type">${escapeHtml(entity.type)}</div>
      <div class="kb-entity-title">${escapeHtml(entity.title)}</div>
      <div class="kb-entity-summary">${escapeHtml(entity.summary || '')}</div>
    </div>
  `).join('');
}

function toggleKBEntity(entityId) {
  if (selectedKBEntities.has(entityId)) {
    selectedKBEntities.delete(entityId);
  } else {
    selectedKBEntities.add(entityId);
  }
  renderKBEntities();
  updateKBPreview();
}

async function updateKBPreview() {
  const previewEl = document.getElementById('kbPreview');
  
  if (selectedKBEntities.size === 0) {
    previewEl.textContent = 'Select entities above to preview injection...';
    return;
  }
  
  previewEl.textContent = 'Loading preview...';
  
  try {
    const resp = await fetch(`${API}/api/kb/preview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ entity_ids: Array.from(selectedKBEntities) })
    });
    
    const data = await resp.json();
    previewEl.textContent = data.preview || data.content || 'No preview available';
  } catch (err) {
    previewEl.textContent = 'Preview error: ' + err.message;
  }
}

// Add command palette entry
// { icon: '📚', title: 'Toggle KB Panel', desc: 'Show/hide knowledge base panel', action: () => toggleKBPanel(), category: 'System' },
```

**Add icon bar button** for KB:
```html
<!-- In icon bar, add button -->
<button class="icon-btn" onclick="toggleKBPanel()" title="Knowledge Base">
  <span class="icon">📚</span>
  <span class="label">KB</span>
</button>
```

---

### E2: Flight Lifecycle Controls

**Backend**: POST /api/flights/start, POST /api/flights/end, POST /api/flights/recap
**Priority**: High - needed for pipeline workflow

Add UI to start, end, and add recaps to flights.

**Add to pipeline/flights view**:
```html
<!-- Flight control buttons - add to flights section header -->
<div class="flight-controls">
  <button class="btn small primary" onclick="startNewFlight()">+ New Flight</button>
</div>
```

**JS to add**:
```javascript
// ═══════════════════════════════════════════════════════════════
// FLIGHT LIFECYCLE
// ═══════════════════════════════════════════════════════════════

async function startNewFlight() {
  const title = prompt('Flight title (optional):');
  const flightId = `flight-${Date.now()}`;
  
  try {
    const resp = await fetch(`${API}/api/flights/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        flight_id: flightId, 
        title: title || flightId 
      })
    });
    
    const data = await resp.json();
    showNotification(`Flight started: ${data.flight_id || flightId}`, 'success');
    loadFlights && loadFlights();
    
    // Connect WebSocket to new flight
    connectFlightWebSocket(flightId);
  } catch (err) {
    showNotification('Failed to start flight: ' + err.message, 'error');
  }
}

async function endFlight(flightId) {
  if (!confirm(`End flight ${flightId}?`)) return;
  
  try {
    await fetch(`${API}/api/flights/end`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ flight_id: flightId })
    });
    
    showNotification(`Flight ended: ${flightId}`, 'success');
    disconnectFlightWebSocket();
    loadFlights && loadFlights();
  } catch (err) {
    showNotification('Failed to end flight: ' + err.message, 'error');
  }
}

async function addFlightRecap(flightId) {
  const recap = prompt('Enter recap notes:');
  if (!recap) return;
  
  try {
    await fetch(`${API}/api/flights/recap`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        flight_id: flightId, 
        recap_text: recap 
      })
    });
    
    showNotification('Recap added', 'success');
  } catch (err) {
    showNotification('Failed to add recap: ' + err.message, 'error');
  }
}
```

**Update flight card rendering** to include controls:
```javascript
// In renderFlights, add action buttons to each flight card:
<div class="flight-card-actions">
  ${!flight.ended_at ? `
    <button class="btn small" onclick="event.stopPropagation(); addFlightRecap('${flight.id}')">📝 Recap</button>
    <button class="btn small warning" onclick="event.stopPropagation(); endFlight('${flight.id}')">⏹ End</button>
  ` : ''}
</div>
```

---

### E3: Worker Status Display

**Backend**: GET /api/worker/status, POST /api/worker/start, POST /api/worker/stop
**Priority**: High - shows if automated processing is running

**Add to dashboard or status bar**:
```javascript
// ═══════════════════════════════════════════════════════════════
// WORKER STATUS
// ═══════════════════════════════════════════════════════════════

let workerStatus = { running: false };

async function loadWorkerStatus() {
  try {
    const resp = await fetch(`${API}/api/worker/status`);
    workerStatus = await resp.json();
    updateWorkerDisplay();
  } catch (err) {
    console.error('Failed to load worker status:', err);
  }
}

function updateWorkerDisplay() {
  const indicator = document.getElementById('workerStatus');
  if (!indicator) return;
  
  if (workerStatus.running) {
    indicator.innerHTML = '<span style="color:var(--mint-500);">● Worker Running</span>';
    indicator.title = `Tasks processed: ${workerStatus.tasks_processed || 0}`;
  } else {
    indicator.innerHTML = '<span style="color:var(--ink-400);">○ Worker Stopped</span>';
  }
}

async function toggleWorker() {
  try {
    const endpoint = workerStatus.running ? '/api/worker/stop' : '/api/worker/start';
    await fetch(`${API}${endpoint}`, { method: 'POST' });
    
    showNotification(workerStatus.running ? 'Worker stopped' : 'Worker started', 'success');
    await loadWorkerStatus();
  } catch (err) {
    showNotification('Failed to toggle worker: ' + err.message, 'error');
  }
}
```

**Add to status bar or dashboard**:
```html
<!-- In status bar or top bar -->
<div class="top-bar-status" id="workerStatus" onclick="toggleWorker()" style="cursor:pointer;" title="Click to toggle worker">
  <span style="color:var(--ink-400);">○ Worker</span>
</div>
```

**Add to init**:
```javascript
// In DOMContentLoaded, add:
loadWorkerStatus();
setInterval(loadWorkerStatus, 30000); // Check every 30s
```

---

### E4: Hive State & Orphan Management

**Backend**: GET /api/hive/state, GET /api/hive/orphans, POST /api/hive/orphans/kill-all
**Priority**: Medium - useful for managing stuck bots

**Add orphan indicator to bot list header**:
```javascript
async function checkOrphans() {
  try {
    const resp = await fetch(`${API}/api/hive/orphans`);
    const data = await resp.json();
    const orphans = data.orphans || [];
    
    const indicator = document.getElementById('orphanCount');
    if (indicator) {
      if (orphans.length > 0) {
        indicator.textContent = `⚠️ ${orphans.length} orphaned`;
        indicator.style.display = 'inline';
        indicator.onclick = () => handleOrphans(orphans);
      } else {
        indicator.style.display = 'none';
      }
    }
  } catch (err) {
    console.error('Failed to check orphans:', err);
  }
}

async function handleOrphans(orphans) {
  const names = orphans.map(o => o.name || o.session_id).join(', ');
  if (confirm(`Kill ${orphans.length} orphaned processes?\n\n${names}`)) {
    try {
      await fetch(`${API}/api/hive/orphans/kill-all`, { method: 'POST' });
      showNotification('Orphans killed', 'success');
      loadBots && loadBots();
    } catch (err) {
      showNotification('Failed to kill orphans: ' + err.message, 'error');
    }
  }
}
```

**Add orphan indicator HTML**:
```html
<!-- In bots section header -->
<span id="orphanCount" style="display:none;color:var(--amber-500);font-size:11px;cursor:pointer;margin-left:8px;"></span>
```

**Add to polling**:
```javascript
// Add to periodic checks:
setInterval(checkOrphans, 60000); // Check every minute
```

---

## Testing Checklist

After completing Sprint E:

- [ ] Click KB icon - panel slides open
- [ ] KB entities load and display
- [ ] Click entity - toggles selection, preview updates
- [ ] Multiple entities selected - preview shows combined injection
- [ ] Click "+ New Flight" - prompts for title, creates flight
- [ ] Flight card shows "Recap" and "End" buttons when active
- [ ] Click "End" on flight - confirms, ends flight
- [ ] Worker status shows in status bar
- [ ] Click worker status - toggles worker on/off
- [ ] When orphaned processes exist - indicator shows count
- [ ] Click orphan indicator - confirms, kills orphans

---

## Files Modified

- `docs/mockups/chat-beta.html`

---

## Notes

- Some endpoints may not exist yet in the backend - if you get 404s, note which ones and skip
- The worker loop may need backend implementation to fully work
- Orphan detection depends on hive state tracking

---

*Sprint E complete when all tests pass (or noted as backend-blocked)*
