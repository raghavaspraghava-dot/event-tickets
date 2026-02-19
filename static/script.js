console.log("🔥 JavaScript LOADED!");

async function loadEvents() {
    console.log("🚀 Loading events...");
    
    try {
        const response = await fetch('/api/events');
        console.log("📡 API Response:", response);
        const events = await response.json();
        console.log("✅ Events data:", events);
        
        const eventsList = document.getElementById('events-list');
        const eventSelect = document.getElementById('event-select');
        
        console.log("📋 Found elements:", eventsList, eventSelect);
        
        eventsList.innerHTML = '';
        eventSelect.innerHTML = '<option value="">Choose an event...</option>';
        
        events.forEach(event => {
            console.log("➕ Adding event:", event);
            
            // Event cards
            const eventCard = document.createElement('div');
            eventCard.className = 'event-card';
            eventCard.innerHTML = `<h3>${event.name}</h3><div>${event.date}</div><div>${event.available} tickets</div>`;
            eventsList.appendChild(eventCard);
            
            // Dropdown
            const option = document.createElement('option');
            option.value = event.id;
            option.textContent = `${event.name} - ${event.date}`;
            eventSelect.appendChild(option);
        });
        
        console.log("🎉 Events loaded successfully!");
    } catch (error) {
        console.error("❌ Error loading events:", error);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log("🌐 Page loaded, starting app...");
    loadEvents();
});
