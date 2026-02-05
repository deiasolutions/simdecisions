# TASK-011: Metrics Dashboard

## Status: PENDING
## Assignee: BEE-001
## Effort: 6-8 hours
## Priority: P1
## Depends: TASK-009, TASK-010

---

## Objective

Real-time HTML dashboard showing live metrics via WebSocket.

---

## Create `docs/mockups/metrics-dashboard.html`

```html
<!DOCTYPE html>
<html>
<head>
  <title>SimDecisions Metrics</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { 
      font-family: system-ui, -apple-system, sans-serif; 
      background: #0f0f1a; 
      color: #e0e0e0; 
      padding: 24px;
      min-height: 100vh;
    }
    
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
    }
    h1 { color: #00d9ff; font-size: 24px; }
    .status { 
      display: flex; 
      align-items: center; 
      gap: 8px;
      font-size: 14px;
    }
    .status-dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: #ff4444;
    }
    .status-dot.connected { background: #44ff44; }
    
    .cards { 
      display: grid; 
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
      gap: 16px; 
      margin-bottom: 24px; 
    }
    .card { 
      background: #1a1a2e; 
      padding: 20px; 
      border-radius: 12px;
      border: 1px solid #2a2a4a;
    }
    .card h3 { 
      font-size: 12px; 
      color: #888; 
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 8px; 
    }
    .card .value { 
      font-size: 36px; 
      font-weight: 700; 
      color: #00d9ff; 
    }
    .card .subtitle {
      font-size: 12px;
      color: #666;
      margin-top: 4px;
    }
    
    .panels { 
      display: grid; 
      grid-template-columns: 1fr 1fr; 
      gap: 16px; 
    }
    @media (max-width: 900px) {
      .panels { grid-template-columns: 1fr; }
    }
    
    .panel { 
      background: #1a1a2e; 
      padding: 20px; 
      border-radius: 12px;
      border: 1px solid #2a2a4a;
      max-height: 500px;
      display: flex;
      flex-direction: column;
    }
    .panel h2 { 
      font-size: 14px; 
      margin-bottom: 16px; 
      color: #00d9ff;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .panel-content {
      flex: 1;
      overflow-y: auto;
    }
    
    .event { 
      padding: 10px 12px; 
      border-bottom: 1px solid #2a2a4a; 
      font-size: 13px; 
      font-family: 'SF Mono', Monaco, monospace;
      display: flex;
      gap: 12px;
      align-items: flex-start;
    }
    .event:last-child { border-bottom: none; }
    .event .time { color: #666; min-width: 80px; }
    .event .type { 
      color: #00d9ff; 
      font-weight: 600;
      min-width: 120px;
    }
    .event .detail { color: #999; }
    
    .provider-row { 
      display: flex; 
      justify-content: space-between; 
      padding: 12px 0; 
      border-bottom: 1px solid #2a2a4a; 
    }
    .provider-row:last-child { border-bottom: none; }
    .provider-row .name { color: #e0e0e0; }
    .provider-row .tokens { color: #888; font-size: 13px; }
    .provider-row .cost { color: #00d9ff; font-weight: 600; }
    
    .empty { color: #666; font-style: italic; padding: 20px; text-align: center; }
  </style>
</head>
<body>
  <header>
    <h1>SimDecisions Metrics</h1>
    <div class="status">
      <div class="status-dot" id="ws-status"></div>
      <span id="ws-text">Disconnected</span>
    </div>
  </header>
  
  <div class="cards">
    <div class="card">
      <h3>Events Today</h3>
      <div class="value" id="events-count">-</div>
      <div class="subtitle" id="events-date"></div>
    </div>
    <div class="card">
      <h3>Total Tokens</h3>
      <div class="value" id="total-tokens">-</div>
      <div class="subtitle">across all providers</div>
    </div>
    <div class="card">
      <h3>Estimated Cost</h3>
      <div class="value" id="total-cost">-</div>
      <div class="subtitle">USD</div>
    </div>
    <div class="card">
      <h3>Active Flights</h3>
      <div class="value" id="active-flights">-</div>
      <div class="subtitle">in progress</div>
    </div>
  </div>
  
  <div class="panels">
    <div class="panel">
      <h2>Cost by Provider</h2>
      <div class="panel-content" id="providers">
        <div class="empty">Loading...</div>
      </div>
    </div>
    <div class="panel">
      <h2>Recent Events</h2>
      <div class="panel-content" id="events">
        <div class="empty">Waiting for events...</div>
      </div>
    </div>
  </div>

  <script>
    const API = 'http://localhost:8010';
    const WS_URL = 'ws://localhost:8010/api/ws';
    let ws = null;
    let reconnectAttempts = 0;
    const MAX_EVENTS = 50;
    let eventsBuffer = [];
    
    // Format helpers
    function formatNumber(n) {
      if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
      if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
      return n.toString();
    }
    
    function formatCost(n) {
      if (n >= 1) return '$' + n.toFixed(2);
      if (n >= 0.01) return '$' + n.toFixed(3);
      return '$' + n.toFixed(4);
    }
    
    function formatTime(ts) {
      if (!ts) return '';
      const d = new Date(ts);
      return d.toTimeString().split(' ')[0];
    }
    
    // Fetch summary data
    async function fetchSummary() {
      try {
        const res = await fetch(`${API}/api/summary`);
        const data = await res.json();
        
        const cost = data.cost || {};
        document.getElementById('total-tokens').textContent = formatNumber(cost.total_tokens || 0);
        document.getElementById('total-cost').textContent = formatCost(cost.estimated_cost_usd || 0);
        
        // Providers
        const providers = cost.by_provider || {};
        const entries = Object.entries(providers);
        if (entries.length === 0) {
          document.getElementById('providers').innerHTML = '<div class="empty">No data yet</div>';
        } else {
          document.getElementById('providers').innerHTML = entries
            .sort((a, b) => b[1].cost - a[1].cost)
            .map(([name, info]) => `
              <div class="provider-row">
                <div>
                  <div class="name">${name}</div>
                  <div class="tokens">${formatNumber(info.tokens)} tokens</div>
                </div>
                <div class="cost">${formatCost(info.cost)}</div>
              </div>
            `).join('');
        }
      } catch (e) {
        console.error('Failed to fetch summary:', e);
      }
    }
    
    // Fetch events
    async function fetchEvents() {
      try {
        const res = await fetch(`${API}/api/events?limit=20`);
        const data = await res.json();
        
        document.getElementById('events-count').textContent = data.count || 0;
        document.getElementById('events-date').textContent = data.date || '';
        
        eventsBuffer = data.events || [];
        renderEvents();
      } catch (e) {
        console.error('Failed to fetch events:', e);
      }
    }
    
    // Fetch flights
    async function fetchFlights() {
      try {
        const res = await fetch(`${API}/api/flights`);
        const data = await res.json();
        const active = (data.flights || []).filter(f => !f.ended_at).length;
        document.getElementById('active-flights').textContent = active;
      } catch (e) {
        document.getElementById('active-flights').textContent = '0';
      }
    }
    
    // Render events
    function renderEvents() {
      if (eventsBuffer.length === 0) {
        document.getElementById('events').innerHTML = '<div class="empty">No events yet</div>';
        return;
      }
      
      document.getElementById('events').innerHTML = eventsBuffer
        .slice(-MAX_EVENTS)
        .reverse()
        .map(e => `
          <div class="event">
            <span class="time">${formatTime(e.timestamp)}</span>
            <span class="type">${e.event}</span>
            <span class="detail">${e.task_id || ''} ${e.bot_id || ''}</span>
          </div>
        `).join('');
      
      document.getElementById('events-count').textContent = eventsBuffer.length;
    }
    
    // WebSocket connection with auto-reconnect
    function connectWS() {
      ws = new WebSocket(WS_URL);
      
      ws.onopen = () => {
        reconnectAttempts = 0;
        document.getElementById('ws-status').classList.add('connected');
        document.getElementById('ws-text').textContent = 'Connected';
      };
      
      ws.onmessage = (e) => {
        try {
          const event = JSON.parse(e.data);
          // Add to buffer
          eventsBuffer.push(event);
          if (eventsBuffer.length > MAX_EVENTS * 2) {
            eventsBuffer = eventsBuffer.slice(-MAX_EVENTS);
          }
          renderEvents();
          // Refresh summary on certain events
          if (['task_completed', 'response_received'].includes(event.event)) {
            fetchSummary();
          }
        } catch (err) {
          console.error('WS message error:', err);
        }
      };
      
      ws.onclose = () => {
        document.getElementById('ws-status').classList.remove('connected');
        document.getElementById('ws-text').textContent = 'Reconnecting...';
        
        // Exponential backoff reconnect
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
        reconnectAttempts++;
        setTimeout(connectWS, delay);
      };
      
      ws.onerror = (err) => {
        console.error('WS error:', err);
        ws.close();
      };
    }
    
    // Initialize
    fetchSummary();
    fetchEvents();
    fetchFlights();
    connectWS();
    
    // Refresh periodically
    setInterval(fetchSummary, 30000);
    setInterval(fetchFlights, 30000);
  </script>
</body>
</html>
```

---

## Done When

- [ ] Dashboard HTML created at `docs/mockups/metrics-dashboard.html`
- [ ] Cards show events count, tokens, cost, flights
- [ ] Provider breakdown panel works
- [ ] Events panel shows recent events
- [ ] WebSocket connects and receives live events
- [ ] Auto-reconnect with exponential backoff
- [ ] Status indicator shows connection state
