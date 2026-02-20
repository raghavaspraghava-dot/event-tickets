async function loadEvents() {
    const response = await fetch('/api/events');
    const events = await response.json();

    const list = document.getElementById('events-list');
    const select = document.getElementById('event-select');

    list.innerHTML='';
    select.innerHTML='<option value="">Select Event</option>';

    events.forEach(e=>{
        list.innerHTML+=`<div>${e.name} - ${e.date} (${e.available} tickets)</div>`;
        select.innerHTML+=`<option value="${e.id}">${e.name}</option>`;
    });
}

document.addEventListener('DOMContentLoaded', loadEvents);

document.getElementById('ticket-form')?.addEventListener('submit', async function(e){
    e.preventDefault();
    const formData=new FormData(this);
    await fetch('/book',{method:'POST',body:formData});
    alert("Booking successful!");
});