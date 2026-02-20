// Base API URL - Update this with your deployed backend URL
const API_BASE = 'http://localhost:5000/api'; // Change to your Render URL after deployment

// Global variables
let currentUser = null;
let isAdmin = false;

// Utility functions
function showMessage(elementId, message, isError = false) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
        element.className = isError ? 'error-message' : 'success-message';
        element.style.display = 'block';
        setTimeout(() => {
            element.style.display = 'none';
        }, 5000);
    }
}

function showAlert(message) {
    alert(message);
}

// Events functions
async function loadEvents() {
    try {
        const response = await fetch(`${API_BASE}/events`);
        const events = await response.json();
        
        const grid = document.getElementById('eventsGrid');
        if (grid) {
            grid.innerHTML = events.map(event => `
                <div class="event-card">
                    <h3>${event.title}</h3>
                    <p>${event.description}</p>
                    <div class="event-meta">
                        <span class="event-date">${new Date(event.date).toLocaleDateString()}</span>
                        <span>${event.total_tickets} tickets available</span>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading events:', error);
        document.getElementById('eventsGrid').innerHTML = '<div class="error-message" style="grid-column: 1/-1; padding: 2rem;">Failed to load events. Please try again.</div>';
    }
}

async function loadEventsForRegistration() {
    try {
        const response = await fetch(`${API_BASE}/events`);
        const events = await response.json();
        
        const select = document.getElementById('eventSelect');
        if (select) {
            select.innerHTML = '<option value="">Select an event</option>' + 
                events.map(event => 
                    `<option value="${event.id}" data-tickets="${event.total_tickets}">${event.title} - ${new Date(event.date).toLocaleDateString()}</option>`
                ).join('');
        }
    } catch (error) {
        console.error('Error loading events for registration:', error);
    }
}

async function loadEventsForDashboard() {
    await loadEventsForRegistration();
    
    const dashSelect = document.getElementById('dashEventSelect');
    if (dashSelect) {
        dashSelect.innerHTML = dashSelect.innerHTML; // Refresh options
    }
}

async function loadEventsForDashboardRegistration() {
    await loadEventsForRegistration();
}

// Registration functions
async function handleRegistration(e) {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        event_id: document.getElementById('eventSelect').value,
        tickets: parseInt(document.getElementById('tickets').value)
    };

    try {
        const response = await fetch(`${API_BASE}/tickets/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();
        
        if (response.ok) {
            showMessage('successMessage', `Success! ${result.message}`);
            document.getElementById('registerForm').reset();
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 2000);
        } else {
            showMessage('successMessage', result.error, true);
        }
    } catch (error) {
        showMessage('successMessage', 'Network error. Please try again.', true);
    }
}

async function handleDashboardRegistration(e) {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('dashName').value,
        email: document.getElementById('dashEmail').value,
        event_id: document.getElementById('dashEventSelect').value,
        tickets: parseInt(document.getElementById('dashTickets').value)
    };

    try {
        const response = await fetch(`${API_BASE}/tickets/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();
        
        if (response.ok) {
            showMessage('dashboardSuccess', `Success! ${result.message}`);
            document.getElementById('dashboardRegisterForm').reset();
        } else {
            showMessage('dashboardSuccess', result.error, true);
        }
    } catch (error) {
        showMessage('dashboardSuccess', 'Network error. Please try again.', true);
    }
}

// Auth functions
async function handleUserLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await fetch(`${API_BASE}/auth/user-login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });

        const result = await response.json();
        
        if (response.ok) {
            localStorage.setItem('userToken', result.token);
            currentUser = { email };
            showMessage('loginMessage', 'Login successful! Redirecting...');
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1000);
        } else {
            showMessage('loginMessage', result.error, true);
        }
    } catch (error) {
        showMessage('loginMessage', 'Network error. Please try again.', true);
    }
}

async function handleAdminLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('adminEmail').value;
    const password = document.getElementById('adminPassword').value;

    try {
        const response = await fetch(`${API_BASE}/auth/admin-login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });

        const result = await response.json();
        
        if (response.ok) {
            localStorage.setItem('adminToken', result.token);
            isAdmin = true;
            showMessage('adminLoginMessage', 'Admin login successful!');
            setTimeout(() => {
                window.location.href = 'admin.html';
            }, 1000);
        } else {
            showMessage('adminLoginMessage', result.error, true);
        }
    } catch (error) {
        showMessage('adminLoginMessage', 'Network error. Please try again.', true);
    }
}

// Admin functions
async function loadAdminStats() {
    try {
        const response = await fetch(`${API_BASE}/admin/stats`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
            }
        });
        
        if (response.ok) {
            const stats = await response.json();
            document.getElementById('totalEvents').textContent = stats.total_events;
            document.getElementById('totalTickets').textContent = stats.total_tickets;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadAdminEvents() {
    try {
        const response = await fetch(`${API_BASE}/events`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
            }
        });
        
        const events = await response.json();
        const grid = document.getElementById('adminEventsGrid');
        if (grid) {
            grid.innerHTML = events.map(event => `
                <div class="event-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h3>${event.title}</h3>
                            <p>${event.description}</p>
                        </div>
                        <div>
                            <div class="event-meta">
                                <span>${new Date(event.date).toLocaleDateString()}</span>
                                <span>${event.total_tickets} tickets</span>
                            </div>
                            <button class="btn-danger" onclick="deleteEvent('${event.id}')">Delete</button>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading admin events:', error);
    }
}

function showEventsManagement() {
    const section = document.getElementById('eventsManagement');
    const btn = document.getElementById('eventsBtn');
    if (section.style.display === 'none') {
        section.style.display = 'block';
        btn.textContent = 'Hide Events Management';
        loadAdminEvents();
    } else {
        section.style.display = 'none';
        btn.textContent = 'Events Management';
    }
}

async function handleAddEvent(e) {
    e.preventDefault();
    
    const formData = {
        title: document.getElementById('eventTitle').value,
        description: document.getElementById('eventDesc').value,
        date: document.getElementById('eventDate').value,
        total_tickets: parseInt(document.getElementById('eventTickets').value)
    };

    try {
        const response = await fetch(`${API_BASE}/events`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            showMessage('adminEventsGrid', 'Event added successfully!');
            document.getElementById('addEventForm').reset();
            loadAdminEvents();
            loadAdminStats();
        } else {
            const error = await response.json();
            alert('Error: ' + error.error);
        }
    } catch (error) {
        alert('Network error. Please try again.');
    }
}

async function deleteEvent(eventId) {
    if (!confirm('Are you sure you want to delete this event?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/events/${eventId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
            }
        });

        if (response.ok) {
            loadAdminEvents();
            loadAdminStats();
            showMessage('adminEventsGrid', 'Event deleted successfully!');
        } else {
            alert('Error deleting event');
        }
    } catch (error) {
        alert('Network error. Please try again.');
    }
}

// Expose functions globally for inline onclick handlers
window.deleteEvent = deleteEvent;
window.loadEvents = loadEvents;
window.handleUserLogin = handleUserLogin;
window.handleAdminLogin = handleAdminLogin;
window.handleRegistration = handleRegistration;
window.handleDashboardRegistration = handleDashboardRegistration;
window.showEventsManagement = showEventsManagement;
