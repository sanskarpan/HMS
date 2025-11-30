// API utility for making HTTP requests to the backend

const API_BASE_URL = '/api';

const api = {
    getToken() {
        return localStorage.getItem('access_token');
    },

    getRefreshToken() {
        return localStorage.getItem('refresh_token');
    },

    setTokens(accessToken, refreshToken) {
        localStorage.setItem('access_token', accessToken);
        if (refreshToken) {
            localStorage.setItem('refresh_token', refreshToken);
        }
    },

    clearTokens() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
    },

    setUser(user) {
        localStorage.setItem('user', JSON.stringify(user));
    },

    getUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    },

    isAuthenticated() {
        return !!this.getToken();
    },

    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json'
        };

        if (includeAuth && this.getToken()) {
            headers['Authorization'] = `Bearer ${this.getToken()}`;
        }

        return headers;
    },

    async get(endpoint, includeAuth = true) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'GET',
                headers: this.getHeaders(includeAuth)
            });
            return await this.handleResponse(response);
        } catch (error) {
            return this.handleError(error);
        }
    },

    async post(endpoint, data, includeAuth = true) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: this.getHeaders(includeAuth),
                body: JSON.stringify(data)
            });
            return await this.handleResponse(response);
        } catch (error) {
            return this.handleError(error);
        }
    },

    async put(endpoint, data, includeAuth = true) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'PUT',
                headers: this.getHeaders(includeAuth),
                body: JSON.stringify(data)
            });
            return await this.handleResponse(response);
        } catch (error) {
            return this.handleError(error);
        }
    },

    async delete(endpoint, includeAuth = true) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'DELETE',
                headers: this.getHeaders(includeAuth)
            });
            return await this.handleResponse(response);
        } catch (error) {
            return this.handleError(error);
        }
    },

    async handleResponse(response) {
        const data = await response.json();

        if (!response.ok) {
            if (response.status === 401 && this.getRefreshToken()) {
                const refreshed = await this.refreshToken();
                if (refreshed) {
                    return null;
                }
            }

            return {
                success: false,
                status: response.status,
                message: data.message || 'An error occurred',
                error: data.error || 'unknown_error',
                errors: data.errors || []
            };
        }

        return data;
    },

    handleError(error) {
        console.error('API Error:', error);
        return {
            success: false,
            message: 'Network error. Please check your connection.',
            error: 'network_error'
        };
    },

    async refreshToken() {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getRefreshToken()}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('access_token', data.access_token);
                return true;
            }

            this.clearTokens();
            return false;
        } catch (error) {
            this.clearTokens();
            return false;
        }
    }
};

window.api = api;
