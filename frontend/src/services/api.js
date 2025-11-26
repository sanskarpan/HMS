/**
 * API utility for making HTTP requests to the backend.
 * Handles authentication tokens and error responses.
 */

const API_BASE_URL = '/api';

const api = {
    /**
     * Get the stored authentication token.
     */
    getToken() {
        return localStorage.getItem('access_token');
    },

    /**
     * Get the refresh token.
     */
    getRefreshToken() {
        return localStorage.getItem('refresh_token');
    },

    /**
     * Store authentication tokens.
     */
    setTokens(accessToken, refreshToken) {
        localStorage.setItem('access_token', accessToken);
        if (refreshToken) {
            localStorage.setItem('refresh_token', refreshToken);
        }
    },

    /**
     * Clear stored tokens (logout).
     */
    clearTokens() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
    },

    /**
     * Store user data.
     */
    setUser(user) {
        localStorage.setItem('user', JSON.stringify(user));
    },

    /**
     * Get stored user data.
     */
    getUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    },

    /**
     * Check if user is authenticated.
     */
    isAuthenticated() {
        return !!this.getToken();
    },

    /**
     * Get headers for API requests.
     */
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json'
        };

        if (includeAuth && this.getToken()) {
            headers['Authorization'] = `Bearer ${this.getToken()}`;
        }

        return headers;
    },

    /**
     * Make a GET request.
     */
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

    /**
     * Make a POST request.
     */
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

    /**
     * Make a PUT request.
     */
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

    /**
     * Make a DELETE request.
     */
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

    /**
     * Handle API response.
     */
    async handleResponse(response) {
        const data = await response.json();

        if (!response.ok) {
            // Handle 401 - try to refresh token
            if (response.status === 401 && this.getRefreshToken()) {
                const refreshed = await this.refreshToken();
                if (refreshed) {
                    // Signal to retry
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

    /**
     * Handle network or other errors.
     */
    handleError(error) {
        console.error('API Error:', error);
        return {
            success: false,
            message: 'Network error. Please check your connection.',
            error: 'network_error'
        };
    },

    /**
     * Refresh the access token.
     */
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

            // Refresh failed - clear tokens and redirect to login
            this.clearTokens();
            return false;
        } catch (error) {
            this.clearTokens();
            return false;
        }
    }
};

// Make api available globally
window.api = api;
