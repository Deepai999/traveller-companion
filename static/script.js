document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const chatWindow = document.getElementById('chat-window');
    const loginPrompt = document.getElementById('login-prompt');

    // Show login prompt if user is not authenticated
    const isLoggedIn = document.querySelector('nav a[href*="logout"]');
    if (!isLoggedIn) {
        loginPrompt.style.display = 'block';
    }

    chatForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        const messageText = messageInput.value.trim();
        if (!messageText) return;

        appendMessage(messageText, 'user');
        messageInput.value = '';
        showTypingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: messageText }),
            });

            removeTypingIndicator();

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'An unknown error occurred.');
            }

            const data = await response.json();
            appendMessage(data, 'assistant');

        } catch (error) {
            removeTypingIndicator();
            appendMessage({ error: error.message }, 'assistant');
        }
    });

    function appendMessage(content, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `message-${sender}`);
        
        const paragraph = document.createElement('p');
        paragraph.innerHTML = formatResponse(content);
        messageElement.appendChild(paragraph);
        
        chatWindow.appendChild(messageElement);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function showTypingIndicator() {
        if (document.getElementById('typing-indicator')) return;
        const typingIndicator = document.createElement('div');
        typingIndicator.id = 'typing-indicator';
        typingIndicator.classList.add('message', 'message-assistant');
        typingIndicator.innerHTML = '<p><i>Typing...</i></p>';
        chatWindow.appendChild(typingIndicator);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    function formatResponse(data) {
        if (typeof data === 'string') {
            return data; // User message
        }

        if (data.error) {
            return `<span class="error-message">${data.error}</span>`;
        }

        let html = '';
        
        // Title
        if (data.title) {
            html += `<strong>${data.title}</strong><br>`;
        }
        
        // Handle different response structures
        if (data.destination) { // Late-night trip
            html += `<strong>Destination:</strong> ${data.destination}<br>`;
            if (data.weather && Object.keys(data.weather).length > 0) {
                html += '<strong>Weather:</strong><br><ul>';
                for (const [key, value] of Object.entries(data.weather)) {
                    html += `<li>${key.replace(/_/g, ' ')}: ${value}</li>`;
                }
                html += '</ul>';
            }
            if (data.recommended_gear) html += '<strong>Recommended Gear:</strong><ul>' + data.recommended_gear.map(g => `<li>${g}</li>`).join('') + '</ul>';
            if (data.safety_notes) html += '<strong>Safety Notes:</strong><ul>' + data.safety_notes.map(n => `<li>${n}</li>`).join('') + '</ul>';
        } else if (data.suggested_activities) { // Spontaneous trip
            html += `<strong>Duration:</strong> ${data.duration_hours} hours<br>`;
            html += '<strong>Suggested Activities:</strong><ul>' + data.suggested_activities.map(a => `<li>${a}</li>`).join('') + '</ul>';
        } else if (data.pre_trip) { // Vehicle checklist
            html += '<strong>Pre-Trip:</strong><ul>' + data.pre_trip.map(c => `<li>${c}</li>`).join('') + '</ul>';
            html += '<strong>Post-Trip:</strong><ul>' + data.post_trip.map(c => `<li>${c}</li>`).join('') + '</ul>';
        } else if (data.solution) { // Mechanic assist
            html += `<strong>Issue:</strong> ${data.issue}<br>`;
            if(data.solution.tools) html += '<strong>Tools:</strong><ul>' + data.solution.tools.map(t => `<li>${t}</li>`).join('') + '</ul>';
            if(data.solution.steps) html += '<strong>Steps:</strong><ol>' + data.solution.steps.map(s => `<li>${s}</li>`).join('') + '</ol>';
            if(data.solution.follow_up) html += `<strong>Follow-up:</strong> ${data.solution.follow_up}`;
        } else if (data.tip) { // Random tip
             html += `<strong>${data.category}:</strong> ${data.tip}`;
        } else if (data.tips) { // Trail tips
             html += '<ul>' + data.tips.map(t => `<li>${t}</li>`).join('') + '</ul>';
        } else if (Array.isArray(data) && data.length > 0 && data[0].trip_type) { // Saved Trips
            if (data.length === 0) {
                html = 'You have no saved trips yet.';
            } else {
                html += '<strong>Your Saved Trips:</strong><br><ul>';
                data.forEach(trip => {
                    html += `<li><strong>${trip.trip_type.replace(/_/g, ' ')}</strong> (${new Date(trip.timestamp).toLocaleDateString()})<br>`;
                    html += `<pre>${JSON.stringify(trip.details, null, 2)}</pre></li>`;
                });
                html += '</ul>';
            }
        } else if (typeof data === 'object' && data['Driving Techniques']) { // Full Guide
            html += '<strong>Offroad Guide:</strong><br>';
            for (const [category, tips] of Object.entries(data)) {
                 html += `<strong>${category}:</strong><ul>${tips.map(t => `<li>${t}</li>`).join('')}</ul>`;
            }
        } else if (typeof data === 'object' && Object.keys(data).length === 0) {
            return 'Sorry, I received an empty response.';
        } else {
            // Generic fallback for other JSON objects
            html += '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
        }

        return html;
    }
});
