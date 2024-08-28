import React, { useEffect, useState } from 'react';

function MechanicNotification({ mechanicId }) {
    const [message, setMessage] = useState('');

    useEffect(() => {
        // Create WebSocket connection.
        const ws = new WebSocket(`ws://localhost:8000/ws/mechanic/${mechanicId}/`);

        // Connection opened
        ws.onopen = () => {
            console.log('WebSocket connected');
        };

        // Listen for messages
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setMessage(data.message);
            alert(data.message); // Display notification alert
        };

        // Connection closed
        ws.onclose = () => {
            console.log('WebSocket disconnected');
        };

        // Cleanup function
        return () => ws.close();
    }, [mechanicId]);

    return (
        <div>
            <p>{message}</p>
        </div>
    );
}

export default MechanicNotification;
