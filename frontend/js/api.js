/**
 * Skills-to-Job Planner - Unified API Client & Session Manager
 */

const API_BASE_URL = (
    window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
        ? "http://127.0.0.1:8000"
        : ""
);

const API = {
    getToken() {
        return localStorage.getItem("token") || "";
    },

    setToken(token) {
        if (token) {
            localStorage.setItem("token", token);
        } else {
            localStorage.removeItem("token");
        }
    },

    getUser() {
        try {
            const raw = localStorage.getItem("user");
            return raw ? JSON.parse(raw) : null;
        } catch (e) {
            return null;
        }
    },

    setUser(user) {
        if (user) {
            localStorage.setItem("user", JSON.stringify(user));
        } else {
            localStorage.removeItem("user");
        }
    },

    clearSession() {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
    },

    getHeaders(isMultipart = false) {
        const headers = {};
        const token = this.getToken();
        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }
        if (!isMultipart) {
            headers["Content-Type"] = "application/json";
        }
        return headers;
    },

    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const isMultipart = options.body instanceof FormData;
        const headers = { ...this.getHeaders(isMultipart), ...(options.headers || {}) };

        try {
            const response = await fetch(url, { ...options, headers });

            if (response.status === 401) {
                // If token invalid, clear and notify
                const currentPath = window.location.pathname;
                if (!currentPath.endsWith("auth.html") && !currentPath.endsWith("index.html") && currentPath !== "/") {
                    console.warn("Session expired or unauthorized");
                }
            }

            const contentType = response.headers.get("content-type");
            let data = null;
            if (contentType && contentType.includes("application/json")) {
                data = await response.json();
            } else {
                data = await response.text();
            }

            if (!response.ok) {
                const detail = (data && data.detail) ? data.detail : `Request failed with status ${response.status}`;
                throw new Error(detail);
            }

            return data;
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    },

    get(endpoint) {
        return this.request(endpoint, { method: "GET" });
    },

    post(endpoint, body) {
        return this.request(endpoint, {
            method: "POST",
            body: body instanceof FormData ? body : JSON.stringify(body)
        });
    },

    put(endpoint, body) {
        return this.request(endpoint, {
            method: "PUT",
            body: JSON.stringify(body)
        });
    },

    upload(endpoint, formData) {
        return this.request(endpoint, {
            method: "POST",
            body: formData
        });
    }
};

/**
 * Toast Notification Utility
 */
function showToast(message, type = "info") {
    let container = document.getElementById("toast-container");
    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        container.className = "toast-container";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    
    const icons = {
        success: "✓",
        error: "✕",
        warning: "⚠",
        info: "ℹ"
    };

    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || "ℹ"}</span>
        <span class="toast-message">${escapeHtml(message)}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add("toast-fadeout");
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
