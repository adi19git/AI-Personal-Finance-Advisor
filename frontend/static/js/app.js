// Shared JavaScript for AI Finance Advisor

// Config
const API_BASE = "/api";

// Formatters
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

// ============================================================
// Theme Toggle
// ============================================================
function getTheme() {
    return document.documentElement.getAttribute('data-theme') || 'light';
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    updateThemeIcon(theme);
}

function toggleTheme() {
    const current = getTheme();
    setTheme(current === 'light' ? 'dark' : 'light');
}

function updateThemeIcon(theme) {
    const icon = document.getElementById('themeIcon');
    if (!icon) return;
    if (theme === 'dark') {
        icon.className = 'bi bi-sun-fill';
    } else {
        icon.className = 'bi bi-moon-fill';
    }
}

// Initialize icon on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    updateThemeIcon(getTheme());
});

// Auth Helpers
function isAuthenticated() {
    return !!localStorage.getItem("token");
}

function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = "/login";
    } else {
        const nav = document.getElementById('mainNav');
        if (nav) nav.classList.remove('d-none');
    }
}

function requireGuest() {
    if (isAuthenticated()) {
        window.location.href = "/";
    }
}

function logout() {
    localStorage.removeItem("token");
    window.location.href = "/login";
}

// API Wrappers
async function apiCall(endpoint, options = {}) {
    const token = localStorage.getItem("token");
    
    const headers = {
        "Content-Type": "application/json",
        ...options.headers
    };
    
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }
    
    const config = {
        ...options,
        headers
    };
    
    const response = await fetch(`${API_BASE}${endpoint}`, config);
    
    if (response.status === 401) {
        logout(); // Token expired
    }
    
    if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || "API Request Failed");
    }
    
    return response.json();
}

async function apiGet(endpoint) {
    return apiCall(endpoint, { method: "GET" });
}

async function apiPost(endpoint, data) {
    return apiCall(endpoint, {
        method: "POST",
        body: JSON.stringify(data)
    });
}

// Form Handlers
async function handleLogin(e) {
    e.preventDefault();
    const alertBox = document.getElementById('loginAlert');
    alertBox.classList.add('d-none');
    
    const formData = new FormData();
    formData.append('username', document.getElementById('username').value);
    formData.append('password', document.getElementById('password').value);
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            body: formData // OAuth2 uses form-urlencoded/multipart
        });
        
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail);
        
        localStorage.setItem("token", data.access_token);
        window.location.href = "/";
    } catch (err) {
        alertBox.textContent = err.message;
        alertBox.classList.remove('d-none');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const alertBox = document.getElementById('registerAlert');
    alertBox.classList.add('d-none');
    
    const payload = {
        full_name: document.getElementById('regFullName').value,
        email: document.getElementById('regEmail').value,
        username: document.getElementById('regUsername').value,
        password: document.getElementById('regPassword').value,
    };
    
    try {
        await apiPost('/auth/register', payload);
        
        // Auto-login after registration
        const formData = new FormData();
        formData.append('username', payload.username);
        formData.append('password', payload.password);
        
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        
        localStorage.setItem("token", data.access_token);
        window.location.href = "/";
    } catch (err) {
        alertBox.textContent = err.message;
        alertBox.classList.remove('d-none');
    }
}
