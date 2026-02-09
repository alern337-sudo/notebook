import axios from 'axios';

// Dynamically determine the backend URL
// If accessed via localhost, use localhost
// If accessed via IP (LAN), use that IP
const hostname = window.location.hostname;
const api = axios.create({
    baseURL: `http://${hostname}:8000`,
});

export default api;
