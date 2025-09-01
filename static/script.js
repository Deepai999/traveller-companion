const API_URL = 'http://127.0.0.1:5001/api';

async function handleRequest(endpoint, options = {}, isTripPlan = false) {
    const resultsCard = document.getElementById('results-card');
    const resultsEl = document.getElementById('results');
    resultsCard.style.display = 'block';

    try {
        const response = await fetch(`${API_URL}${endpoint}`, options);
        const data = await response.json();
        resultsDiv.innerHTML = displayTripResults(data);
        if (isTripPlan) {
            getSavedTrips(); // Refresh saved trips list after planning a new one
        }
    } catch (error) {
        resultsDiv.textContent = `Error: ${error.message}`;
    }
}

function displayTripResults(data) {
    let html = '<h4>Trip Details</h4>';

    if (data.destination) {
        html += `<p><strong>Destination:</strong> ${data.destination}</p>`;
    }

    if (data.estimated_arrival) {
        html += `<p><strong>Estimated Arrival:</strong> ${new Date(data.estimated_arrival).toLocaleString()}</p>`;
    }

    if (data.duration_hours) {
        html += `<p><strong>Duration:</strong> ${data.duration_hours} hours</p>`;
    }

    if (data.weather && Object.keys(data.weather).length > 0) {
        html += '<h5>Weather Forecast</h5>';
        html += '<ul>';
        for (const [key, value] of Object.entries(data.weather)) {
            html += `<li><strong>${key.replace('_', ' ')}:</strong> ${value}</li>`;
        }
        html += '</ul>';
    }

    if (data.recommended_gear) {
        html += '<h5>Recommended Gear</h5>';
        html += `<ul>${data.recommended_gear.map(item => `<li>${item}</li>`).join('')}</ul>`;
    }

    if (data.suggested_activities) {
        html += '<h5>Suggested Activities</h5>';
        html += `<ul>${data.suggested_activities.map(item => `<li>${item}</li>`).join('')}</ul>`;
    }

    if (data.safety_notes) {
        html += '<h5>Safety Notes</h5>';
        html += `<ul>${data.safety_notes.map(item => `<li>${item}</li>`).join('')}</ul>`;
    }

    if (data.notes) {
        html += `<p><strong>Notes:</strong> ${data.notes}</p>`;
    }

    return html;
}

function planLateNightTrip() {
    const destination = document.getElementById('destination').value;
    if (!destination) {
        alert('Please enter a destination.');
        return;
    }
    handleRequest('/plan/late-night', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ destination })
    }, true);
}

function planSpontaneousTrip() {
    const duration_hours = document.getElementById('duration').value;
    handleRequest('/plan/spontaneous', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ duration_hours })
    }, true);
}

function getMechanicAssist() {
    const issue = document.getElementById('issue').value;
    if (!issue) {
        alert('Please describe the issue.');
        return;
    }
    handleRequest('/mechanic/assist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ issue })
    });
}

function getAnticipatedMaintenance() {
    const trip_type = document.getElementById('trip-type').value;
    const mileage = document.getElementById('mileage').value;
    handleRequest('/maintenance/anticipate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ trip_type, mileage })
    });
}

function getRandomTip() {
    handleRequest('/tips/random');
}

function getFullGuide() {
    handleRequest('/guide');
}

async function getSavedTrips() {
    const savedTripsList = document.getElementById('saved-trips-list');
    if (!savedTripsList) return; // Don't run if the element doesn't exist (user not logged in)

    try {
        const response = await fetch(`${API_URL}/trips`);
        if (!response.ok) {
            // If not logged in, the server will redirect, but fetch won't follow for CORS reasons.
            // Or it might return an error. Either way, we can't show trips.
            savedTripsList.innerHTML = '<li>Login to see your trips.</li>';
            return;
        }
        const trips = await response.json();
        savedTripsList.innerHTML = ''; // Clear existing list
        if (trips.length === 0) {
            savedTripsList.innerHTML = '<li>No saved trips yet.</li>';
        }
        trips.forEach(trip => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>${trip.trip_type}</strong> (${new Date(trip.timestamp).toLocaleString()})<br><pre>${JSON.stringify(trip.details, null, 2)}</pre>`;
            savedTripsList.appendChild(li);
        });
    } catch (error) {
        savedTripsList.innerHTML = '<li>Could not load saved trips.</li>';
    }
}

// Load saved trips when the page loads if the user is logged in.
document.addEventListener('DOMContentLoaded', getSavedTrips);
