const API_BASE = '/api';

document.addEventListener('DOMContentLoaded', initApp);

async function initApp() {
    try {
        // Test API connection
        const response = await fetch('/api/health');
        const data = await response.json();
        document.getElementById('status').innerHTML = 
            `✅ <strong>${data.message}</strong><br>🗄️ Supabase: <span style="color: ${data.supabase_status === 'ready' ? '#27ae60' : '#f39c12'}">${data.supabase_status}</span>`;
    } catch (error) {
        document.getElementById('status').innerHTML = '❌ API connection failed';
        console.error('API health check failed:', error);
    }

    // Event listeners
    document.getElementById('login-btn').addEventListener('click', adminLogin);
    document.getElementById('refresh-btn').addEventListener('click', loadEvents);
    document.getElementById('logout-btn').addEventListener('click', logout);

    // Auto-login if token exists
    if (localStorage.getItem('adminToken')) {
        showDashboard();
        loadEvents();
    }
}

async function adminLogin() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const btn = document.getElementById('login-btn');
    const errorDiv = document.getElementById('login-error');

    // Reset UI
    errorDiv.style.display = 'none';
    btn.disabled = true;
    btn.innerHTML = '🔄 Logging in...';

    try {
        console.log('Login attempt:', { email });
        const response = await fetch(`${API_BASE}/auth/admin-login`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        console.log('Login response status:', response.status);
        const data = await response.json();
        console.log('Login data:', data);

        if (data.token && data.token.startsWith('admin-')) {
            localStorage.setItem('adminToken', data.token);
            showDashboard();
            document.getElementById('status').innerHTML = '✅ Login successful! Dashboard loaded.';
        } else {
            throw new Error(data.error || 'Invalid login response');
        }
    } catch (error) {
        console.error('Login error:', error);
        errorDiv.textContent = `❌ ${error.message}`;
        errorDiv.style.display = 'block';
    }

    btn.disabled = false;
    btn.innerHTML = '🚀 Login to Dashboard';
}

async function loadEvents() {
    const token = localStorage.getItem('adminToken');
    if (!token) return logout();

    const eventsList = document.getElementById('events-list');
    eventsList.innerHTML = '<div class="loading">🔄 Loading events...</div>';

    try {
        const response = await fetch(`${API_BASE}/events`);
        const events = await response.json();

        if (events.length === 0) {
            eventsList.innerHTML = 
                '<div class="event" style="text-align:center; color:#7f8c8d;">📭 No events yet<br><small>Supabase database is empty. Add events via API.</small></div>';
            document.getElementById('event-count').textContent = '0 events';
        } else {
            eventsList.innerHTML = events.map(event => createEventHTML(event)).join('');
            document.getElementById('event-count').textContent = `${events.length} event${events.length !== 1 ? 's' : ''}`;
        }
    } catch (error) {
        console.error('Load events error:', error);
        eventsList.innerHTML = 
            '<div class="event" style="text-align:center; color:#e74c3c;">❌ Failed to load events: ' + error.message + '</div>';
    }
}

function createEventHTML(event) {
    return `
        <div class="event">
            <h3>${event.title || 'Untitled'}</h3>
            <p>📅 <strong>Date:</strong> ${event.date || 'TBD'}</p>
            <p>🎫 <strong>Tickets:</strong> ${event.total_tickets || 0} available</p>
            ${event.description ? `<p><strong>Description:</strong> ${event.description}</p>` : ''}
        </div>
    `;
}

function showDashboard() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('dashboard').style.display = 'block';
}

function logout() {
    localStorage.removeItem('adminToken');
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('dashboard').style.display = 'none';
    document.getElementById('status').innerHTML = 'Checking API status...';
    document.getElementById('email').focus();
}
