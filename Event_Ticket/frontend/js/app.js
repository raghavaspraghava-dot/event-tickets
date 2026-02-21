const API_BASE = '/api';

// 🔍 FIXED JSON ERROR HANDLING
async function safeFetch(url, options = {}) {
    try {
        const response = await fetch(url, options);
        
        // ✅ CHECK IF HTML ERROR PAGE
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            throw new Error(`Server error (HTML response). Check Network tab (F12). URL: ${url}`);
        }
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        if (error.message.includes('Unexpected token')) {
            throw new Error('API endpoint missing. Check Flask routes.');
        }
        throw error;
    }
}

// 🔒 FORM VALIDATION
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
    if (isNaN(numTickets) || numTickets <= 0) return 'Valid ticket count required (1+)';
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

function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success';
    successDiv.textContent = message;
    document.querySelector('.container').insertBefore(successDiv, document.querySelector('.container').firstChild);
    setTimeout(() => successDiv.remove(), 3000);
}

function logout() {
    localStorage.removeItem('adminToken');
    localStorage.removeItem('userToken');
    redirectTo('index.html');
}

// 👨‍💼 ADMIN LOGIN
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
            showSuccess('✅ Admin login successful!');
            setTimeout(() => redirectTo('dashboard.html'), 1000);
        } else {
            throw new Error(data.error || 'Invalid admin credentials');
        }
    } catch (error) {
        showError('admin-error', `Login failed: ${error.message}`);
        console.error('Admin login error:', error);
    }
    
    setLoading('admin-login-btn', false);
}

// 👤 USER LOGIN
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
            showSuccess('✅ Login successful!');
            setTimeout(() => redirectTo('register.html'), 1000);
        } else {
            throw new Error(data.error || 'Login failed');
        }
    } catch (error) {
        showError('user-error', `Login failed: ${error.message}`);
        console.error('User login error:', error);
    }
    
    setLoading('user-login-btn', false);
}

// 🎫 REGISTER TICKETS
async function userRegister() {
    const name = document.getElementById('user-name')?.value?.trim();
    const email = document.getElementById('register-email')?.value?.trim();
    const eventSelect = document.getElementById('event-select');
    const eventId = eventSelect?.value;
    const tickets = document.getElementById('tickets')?.value;
    
    if (!name) {
        showError('register-error', 'Please enter your full name');
        return;
    }
    const emailError = validateEmail(email);
    if (emailError) {
        showError('register-error', emailError);
        return;
    }
    if (!eventId) {
        showError('register-error', 'Please select an event');
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
        const data = await safeFetch(`${API_BASE}/tickets/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name,
                email,
                event_id: eventId,
                tickets: parseInt(tickets)
            })
        });
        
        showSuccess('✅ Tickets registered successfully!');
        document.getElementById('user-name').value = '';
        document.getElementById('register-email').value = '';
        document.getElementById('tickets').value = '1';
        if (eventSelect) eventSelect.selectedIndex = 0;
        
    } catch (error) {
        showError('register-error', error.message);
        console.error('Registration error:', error);
    }
    
    setLoading('register-btn', false);
}

// 📊 LOAD EVENTS FOR DASHBOARD
async function loadEvents() {
    const eventsList = document.getElementById('events-list');
    if (!eventsList) return;
    
    const adminToken = localStorage.getItem('adminToken');
    if (!adminToken || !adminToken.startsWith('admin-')) {
        redirectTo('admin_login.html');
        return;
    }
    
    eventsList.innerHTML = '<div style="text-align:center;padding:20px;">🔄 Loading events...</div>';
    
    try {
        const events = await safeFetch(`${API_BASE}/events`);
        
        if (events.length === 0) {
            eventsList.innerHTML = '<div style="text-align:center;color:#666;padding:40px;">📭 No events yet<br><small>Create your first event below!</small></div>';
            if (document.getElementById('event-count')) {
                document.getElementById('event-count').textContent = '0 events';
            }
        } else {
            eventsList.innerHTML = events.map(event => `
                <div class="event">
                    <h3>${event.title || 'Untitled'}</h3>
                    <p>📅 ${new Date(event.date).toLocaleDateString()}</p>
                    <p>🎫 ${event.total_tickets || 0} tickets available</p>
                    ${event.description ? `<p>${event.description}</p>` : ''}
                </div>
            `).join('');
            if (document.getElementById('event-count')) {
                document.getElementById('event-count').textContent = `${events.length} event${events.length !== 1 ? 's' : ''}`;
            }
        }
    } catch (error) {
        eventsList.innerHTML = '<div style="color:#e74c3c;text-align:center;padding:40px;">❌ Failed to load events: ' + error.message + '</div>';
        console.error('Load events error:', error);
    }
}

// ✨ CREATE EVENT - FIXED (Single fetch call)
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
    
    const adminToken = localStorage.getItem('adminToken');
    if (!adminToken || !adminToken.startsWith('admin-')) {
        showError('create-event-error', '⚠️ Admin login required');
        redirectTo('admin_login.html');
        return;
    }
    
    setLoading('create-event-btn', true);
    hideError('create-event-error');
    
    try {
        const data = await safeFetch(`${API_BASE}/events`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${adminToken}`
            },
            body: JSON.stringify({
                title,
                description,
                date,
                total_tickets: parseInt(tickets)
            })
        });
        
        showSuccess('✅ Event created successfully!');
        document.getElementById('event-title').value = '';
        document.getElementById('event-description').value = '';
        document.getElementById('event-date').value = '';
        document.getElementById('event-tickets').value = '100';
        loadEvents(); // Refresh list
        
    } catch (error) {
        showError('create-event-error', `Failed: ${error.message}`);
        console.error('Create event error:', error);
    }
    
    setLoading('create-event-btn', false);
}

// ✨ LOAD EVENTS FOR REGISTER DROPDOWN
async function loadEventsForRegister() {
    const eventSelect = document.getElementById('event-select');
    if (!eventSelect) return;
    
    eventSelect.innerHTML = '<option>Loading events...</option>';
    
    try {
        const events = await safeFetch(`${API_BASE}/events`);
        eventSelect.innerHTML = '<option value="">Select an event...</option>';
        
        if (events.length === 0) {
            eventSelect.innerHTML = '<option value="">No events available - Contact admin</option>';
            return;
        }
        
        events.forEach(event => {
            const option = document.createElement('option');
            option.value = event.id;
            option.textContent = `${event.title} (${new Date(event.date).toLocaleDateString()}) - ${event.total_tickets} tickets`;
            eventSelect.appendChild(option);
        });
    } catch (error) {
        eventSelect.innerHTML = '<option value="">Failed to load events</option>';
        console.error('Load events error:', error);
    }
}

// 🚀 PAGE INITIALIZATION
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎉 App loaded - Page:', window.location.pathname);
    
    // Dashboard: Check admin login + load events
    if (window.location.pathname.includes('dashboard.html')) {
        const adminToken = localStorage.getItem('adminToken');
        const statusDiv = document.getElementById('admin-status');
        if (statusDiv) {
            if (adminToken && adminToken.startsWith('admin-')) {
                statusDiv.textContent = '✅ Admin authenticated';
                loadEvents();
            } else {
                statusDiv.textContent = '⚠️ Please login as admin';
                setTimeout(() => redirectTo('admin_login.html'), 2000);
            }
        }
    }
    
    // Register: Load events dropdown
    if (window.location.pathname.includes('register.html')) {
        loadEventsForRegister();
    }
});
