// Fetch events from API
async function loadEvents() {
    try {
        const response = await fetch('/api/events');
        const events = await response.json();
        displayEvents(events);
    } catch(e) {
        console.log('Using fallback events');
    }
}

// Display events on page
function displayEvents(events) {
    const container = document.getElementById('events-container');
    container.innerHTML = events.map(event => `
        <div class="card">
            <h3>${event.name}</h3>
            <p>Date: ${event.date}</p>
            <p>Available: ${event.available}/${event.capacity}</p>
            <button onclick="bookTickets('${event.id}')" class="btn">
                Book Tickets (${event.available} left)
            </button>
        </div>
    `).join('');
}

// Book tickets form
function bookTickets(eventId) {
    const name = prompt('Full Name:');
    const email = prompt('Email:');
    const tickets = prompt('Tickets (1-10):');
    
    if(name && email && tickets) {
        fetch('/book', {
            method: 'POST',
            body: new FormData({
                name: name,
                email: email,
                eventId: eventId,
                tickets: tickets
            })
        }).then(() => alert('🎫 Booking confirmed!'));
    }
}

// Auto-load events
loadEvents();
