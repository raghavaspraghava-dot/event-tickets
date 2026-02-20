const API_BASE = '/api';

// COMMON FUNCTIONS
function showError(id, message) {
    const errorDiv = document.getElementById(id);
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

function hideError(id) {
    document.getElementById(id)?.style.setProperty('display', 'none');
}

function setLoading(btnId, loading = true) {
    const btn = document.getElementById(btnId);
    if (loading) {
        btn.disabled = true;
        btn.innerHTML = '🔄 Loading...';
    } else {
        btn.disabled = false;
        btn.innerHTML = btn.dataset.originalText || btn.innerHTML;
    }
}

// ADMIN LOGIN
async function adminLogin() {
    const email = document.getElementById('admin-email').value;
    const password = document.getElementById('admin-password').value;
    
    setLoading('admin-login-btn', true);
    hideError('admin-error');
    
    try {
        const response = await fetch(`${API_BASE}/auth/admin-login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (data.token && data.token.startsWith('admin-')) {
            localStorage.setItem('adminToken', data.token);
            window.location.href = '/admin/dashboard.html';
        } else {
            throw new Error(data.error || 'Invalid credentials');
        }
    } catch (error) {
        showError('admin-error', `Login failed: ${error.message}`);
    }
    
    setLoading('admin-login-btn', false);
}

// USER LOGIN  
async function userLogin() {
    const email = document.getElementById('user-email').value;
    const password = document.getElementById('user-password').value;
    
    setLoading('user-login-btn', true);
    hideError('user-error');
    
    try {
        const response = await fetch(`${API_BASE}/auth/user-login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (data.token) {
            localStorage.setItem('userToken', data.token);
            window.location.href = '/register.html';
        } else {
            throw new Error(data.error || 'Login failed');
        }
    } catch (error) {
        showError('user-error', `Login failed: ${error.message}`);
    }
    
    setLoading('user-login-btn', false);
}

// USER REGISTER
async function userRegister() {
    const email = document.getElementById('register-email').value;
    const tickets = parseInt(document.getElementById('tickets').value);
    
    setLoading('register-btn', true);
    hideError('register-error');
    
    try {
        // Get first event for demo
        const eventsRes = await fetch(`${API_BASE}/events`);
        const events = await eventsRes.json();
        
        if (events.length === 0) {
            throw new Error('No events available');
        }
        
        const event = events[0];
        
        const response = await fetch(`${API_BASE}/tickets/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email,
                event_id: event.id,
                tickets
            })
        });
        
        const data = await response.json();
        showSuccess('✅ Tickets registered! Check your email.');
        document.getElementById('register-form').style.display = 'none';
        
    } catch (error) {
        showError('register-error', error.message);
    }
    
    setLoading('register-btn', false);
}

// DASHBOARD FUNCTIONS
async function loadEvents() {
    const eventsList = document.getElementById('events-list');
    eventsList.innerHTML = '<div class="loading">Loading...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/events`);
        const events = await response.json();
        
        if (events.length === 0) {
            eventsList.innerHTML = '<div class="event" style="text-align:center;">No events</div>';
        } else {
            eventsList.innerHTML = events.map(e => `
                <div class="event">
                    <h3>${e.title}</h3>
                    <p>📅 ${e.date} | 🎫 ${e.total_tickets} tickets</p>
                </div>
            `).join('');
        }
    } catch (error) {
        eventsList.innerHTML = '<div class="error">Failed to load events</div>';
    }
}

function logout() {
    localStorage.removeItem('adminToken');
    localStorage.removeItem('userToken');
    window.location.href = '/index.html';
}
