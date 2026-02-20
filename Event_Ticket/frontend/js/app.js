const API_BASE = '/api';

// 🔍 FIXED JSON ERROR HANDLING
async function safeFetch(url, options = {}) {
    try {
        const response = await fetch(url, options);
        
        // ✅ CHECK IF HTML ERROR PAGE (Common Flask 404/500 issue)
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error(`Server returned HTML (404/500). Check if ${url} exists.`);
        }
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        
        return await response.json();
    } catch (error) {
        if (error.message.includes('Unexpected token')) {
            throw new Error('Server error: API endpoint not found or crashed');
        }
        throw error;
    }
}

// 🔒 FORM VALIDATION (Unchanged)
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

function validateEvent(title, description, date, tickets) {
    if (!title || title.trim() === '') return 'Event title required';
    if (!description || description.trim() === '') return 'Description required';
    if (!date || date === '') return 'Event date required';
    const numTickets = parseInt(tickets);
    if (isNaN(numTickets) || numTickets <= 0) return 'Valid ticket count required';
    return '';
}

// UI FUNCTIONS
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

function redirectTo(page) {
    window.location.href = `/${page}`;
}

// 👨‍💼 ADMIN LOGIN (Fixed JSON handling)
async function adminLogin() {
    const email = document.getElementById('admin-email')?.value?.trim();
    const password = document.getElementById('admin-password')?.value;
    
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
        const data = await safeFetch(`${API_BASE}/auth/admin-login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
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

// 👤 USER LOGIN (Fixed JSON handling)
async function userLogin() {
    const email = document.getElementById('user-email')?.value?.trim();
    const password = document.getElementById('user-password')?.value;
    
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
        const data = await safeFetch(`${API_BASE}/auth/user-login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
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

// 🎫 REGISTER TICKETS
async function userRegister() {
    const email = document.getElementById('register-email')?.value?.trim();
    const tickets = document.getElementById('tickets')?.value;
    
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
        const events = await safeFetch(`${API_BASE}/events`);
        if (events.length === 0) {
            throw new Error('No events available. Contact admin.');
        }
        
        const event = events[0];
        const data = await safeFetch(`${API_BASE}/tickets/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email,
                event_id: event.id,
                tickets: parseInt(tickets)
            })
        });
        
        showSuccess('✅ Tickets registered successfully!');
        
    } catch (error) {
        showError('register-error', error.message);
    }
    
    setLoading('register-btn', false);
}

// 📊 DASHBOARD FUNCTIONS + NEW EVENT CREATION
async function loadEvents() {
    const eventsList = document.getElementById('events-list');
    const token = localStorage.getItem('adminToken');
    
    if (!token || !token.startsWith('admin-')) {
        redirectTo('index.html');
        return;
    }
    
    if (!eventsList) return;
    eventsList.innerHTML = '<div style="text-align:center;padding:20px;">🔄 Loading events...</div>';
    
    try {
        const events = await safeFetch(`${API_BASE}/events`);
        
        if (events.length === 0) {
            eventsList.innerHTML = '<div style="text-align:center;color:#666;padding:40px;">📭 No events yet<br><small>Create your first event below!</small></div>';
            document.getElementById('event-count').textContent = '0 events';
        } else {
            eventsList.innerHTML = events.map(event => `
                <div class="event">
                    <h3>${event.title || 'Untitled'}</h3>
                    <p>📅 ${new Date(event.date).toLocaleDateString()}</p>
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

// ✨ NEW: CREATE EVENT FUNCTION
async function createEvent() {
    const title = document.getElementById('event-title')?.value?.trim();
    const description = document.getElementById('event-description')?.value?.trim();
    const date = document.getElementById('event-date')?.value;
    const tickets = document.getElementById('event-tickets')?.value;
    
    const validationError = validateEvent(title, description, date, tickets);
    if (validationError) {
        showError('create-event-error', validationError);
        return;
    }
    
    setLoading('create-event-btn', true);
    hideError('create-event-error');
    
    try {
        const token = localStorage.getItem('adminToken');
        const data = await safeFetch(`${API_BASE}/events`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                title,
                description,
                date,
                total_tickets: parseInt(tickets)
            })
        });
        
        showSuccess('✅ Event created successfully!');
        document.getElementById('event-form').reset();
        loadEvents(); // Refresh list
        
    } catch (error) {
        showError('create-event-error', `Failed to create event: ${error.message}`);
    }
    
    setLoading('create-event-btn', false);
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
    if (window.location.pathname.includes('dashboard.html')) {
        loadEvents();
    }
});
