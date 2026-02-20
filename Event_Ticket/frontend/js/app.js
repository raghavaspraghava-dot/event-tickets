const API_BASE = '/api';

// 🔒 FORM VALIDATION FUNCTIONS
function validateEmail(email) {
    if (!email || email.trim() === '') return 'Please enter your email';
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email) ? '' : 'Please enter a valid email';
}

function validatePassword(password) {
    if (!password || password.trim() === '') return 'Please enter your password';
    return password.length >= 6 ? '' : 'Password must be at least 6 characters';
}

function validateTickets(tickets) {
    const num = parseInt(tickets);
    if (!tickets || isNaN(num) || num <= 0) return 'Please enter valid number of tickets';
    if (num > 10) return 'Maximum 10 tickets allowed';
    return '';
}

// COMMON UI FUNCTIONS
function showError(id, message) {
    const errorDiv = document.getElementById(id);
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }
}

function hideError(id) {
    const errorDiv = document.getElementById(id);
    if (errorDiv) errorDiv.style.display = 'none';
}

function setLoading(btnId, loading = true) {
    const btn = document.getElementById(btnId);
    if (!btn) return;
    if (loading) {
        btn.disabled = true;
        btn.innerHTML = '🔄 Loading...';
        btn.dataset.originalText = btn.innerHTML;
    } else {
        btn.disabled = false;
        btn.innerHTML = btn.dataset.originalText || 'Submit';
    }
}

// 🔄 REDIRECT FUNCTION (Fixed for Flask)
function redirectTo(page) {
    window.location.href = `/${page}`;
}

// 👨‍💼 ADMIN LOGIN (With Validation)
async function adminLogin() {
    const email = document.getElementById('admin-email')?.value?.trim();
    const password = document.getElementById('admin-password')?.value;
    
    // VALIDATION
    const emailError = validateEmail(email);
    if (emailError) {
        showError('admin-error', emailError);
        return;
    }
    const passError = validatePassword(password);
    if (passError) {
        showError('admin-error', passError);
        return;
    }
    
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
            redirectTo('dashboard.html');
        } else {
            throw new Error(data.error || 'Invalid admin credentials');
        }
    } catch (error) {
        showError('admin-error', `Login failed: ${error.message}`);
    }
    
    setLoading('admin-login-btn', false);
}

// 👤 USER LOGIN (With Validation)
async function userLogin() {
    const email = document.getElementById('user-email')?.value?.trim();
    const password = document.getElementById('user-password')?.value;
    
    // VALIDATION
    const emailError = validateEmail(email);
    if (emailError) {
        showError('user-error', emailError);
        return;
    }
    const passError = validatePassword(password);
    if (passError) {
        showError('user-error', passError);
        return;
    }
    
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
            redirectTo('register.html');
        } else {
            throw new Error(data.error || 'Login failed');
        }
    } catch (error) {
        showError('user-error', `Login failed: ${error.message}`);
    }
    
    setLoading('user-login-btn', false);
}

// 🎫 USER REGISTER TICKETS (With Validation)
async function userRegister() {
    const email = document.getElementById('register-email')?.value?.trim();
    const ticketsInput = document.getElementById('tickets');
    const tickets = ticketsInput?.value;
    
    // VALIDATION
    const emailError = validateEmail(email);
    if (emailError) {
        showError('register-error', emailError);
        return;
    }
    const ticketsError = validateTickets(tickets);
    if (ticketsError) {
        showError('register-error', ticketsError);
        return;
    }
    
    setLoading('register-btn', true);
    hideError('register-error');
    
    try {
        const eventsRes = await fetch(`${API_BASE}/events`);
        const events = await eventsRes.json();
        
        if (events.length === 0) {
            throw new Error('No events available. Contact admin.');
        }
        
        const event = events[0];
        const response = await fetch(`${API_BASE}/tickets/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email,
                event_id: event.id,
                tickets: parseInt(tickets)
            })
        });
        
        const data = await response.json();
        showSuccess('✅ Tickets registered successfully!');
        
    } catch (error) {
        showError('register-error', error.message);
    }
    
    setLoading('register-btn', false);
}

// 📊 DASHBOARD FUNCTIONS
async function loadEvents() {
    const eventsList = document.getElementById('events-list');
    if (!eventsList) return;
    
    eventsList.innerHTML = '<div style="text-align:center;padding:20px;">🔄 Loading events...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/events`);
        const events = await response.json();
        
        if (events.length === 0) {
            eventsList.innerHTML = '<div style="text-align:center;color:#666;padding:40px;">📭 No events yet</div>';
            document.getElementById('event-count').textContent = '0 events';
        } else {
            eventsList.innerHTML = events.map(event => `
                <div class="event">
                    <h3>${event.title || 'Untitled'}</h3>
                    <p>📅 ${event.date || 'TBD'}</p>
                    <p>🎫 ${event.total_tickets || 0} tickets available</p>
                    ${event.description ? `<p>${event.description}</p>` : ''}
                </div>
            `).join('');
            document.getElementById('event-count').textContent = `${events.length} event${events.length !== 1 ? 's' : ''}`;
        }
    } catch (error) {
        eventsList.innerHTML = '<div style="color:#e74c3c;text-align:center;padding:40px;">❌ Failed to load events</div>';
    }
}

function logout() {
    localStorage.removeItem('adminToken');
    localStorage.removeItem('userToken');
    redirectTo('index.html');
}

function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success';
    successDiv.textContent = message;
    document.querySelector('.container').insertBefore(successDiv, document.querySelector('.container').firstChild);
    setTimeout(() => successDiv.remove(), 3000);
}

// PAGE INIT
document.addEventListener('DOMContentLoaded', function() {
    // Add click listeners for all buttons
    document.querySelectorAll('[onclick]').forEach(btn => {
        if (!btn.onclick.name || !['adminLogin', 'userLogin', 'userRegister'].includes(btn.onclick.name)) {
            btn.addEventListener('click', btn.onclick);
        }
    });
    
    // Auto-load dashboard if admin
    if (window.location.pathname.includes('dashboard.html') && localStorage.getItem('adminToken')) {
        loadEvents();
    }
});
