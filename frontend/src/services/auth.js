/**
 * Authentication service for login, registration, and session management.
 */

// Simple event emitter for auth state changes
const authEventTarget = new EventTarget();

const authService = {
    // Notify listeners of auth state changes
    _notifyAuthChange() {
        authEventTarget.dispatchEvent(new CustomEvent('authChange'));
    },

    // Subscribe to auth changes
    onAuthChange(callback) {
        authEventTarget.addEventListener('authChange', callback);
        return () => authEventTarget.removeEventListener('authChange', callback);
    },
    /**
     * Login with username/email and password.
     */
    async login(username, password) {
        const response = await api.post('/auth/login', { username, password }, false);

        if (response.success) {
            api.setTokens(response.access_token, response.refresh_token);
            api.setUser(response.user);
            this._notifyAuthChange();
        }

        return response;
    },

    /**
     * Register a new patient.
     */
    async register(userData) {
        const response = await api.post('/auth/register', userData, false);

        if (response.success) {
            api.setTokens(response.access_token, response.refresh_token);
            api.setUser(response.user);
            this._notifyAuthChange();
        }

        return response;
    },

    /**
     * Logout the current user.
     */
    async logout() {
        try {
            await api.post('/auth/logout', {});
        } catch (error) {
            // Ignore errors during logout
        }

        api.clearTokens();
        this._notifyAuthChange();
    },

    /**
     * Get the current user info from the server.
     */
    async getCurrentUser() {
        return await api.get('/auth/me');
    },

    /**
     * Change password.
     */
    async changePassword(currentPassword, newPassword) {
        return await api.post('/auth/change-password', {
            current_password: currentPassword,
            new_password: newPassword
        });
    },

    /**
     * Check if user is authenticated.
     */
    isAuthenticated() {
        return api.isAuthenticated();
    },

    /**
     * Get the stored user.
     */
    getUser() {
        return api.getUser();
    },

    /**
     * Get the user's role.
     */
    getRole() {
        const user = this.getUser();
        return user ? user.role : null;
    },

    /**
     * Check if user has a specific role.
     */
    hasRole(role) {
        return this.getRole() === role;
    },

    /**
     * Check if user is admin.
     */
    isAdmin() {
        return this.hasRole('admin');
    },

    /**
     * Check if user is doctor.
     */
    isDoctor() {
        return this.hasRole('doctor');
    },

    /**
     * Check if user is patient.
     */
    isPatient() {
        return this.hasRole('patient');
    },

    /**
     * Get the dashboard route based on user role.
     */
    getDashboardRoute() {
        const role = this.getRole();
        switch (role) {
            case 'admin':
                return '/admin/dashboard';
            case 'doctor':
                return '/doctor/dashboard';
            case 'patient':
                return '/patient/dashboard';
            default:
                return '/login';
        }
    }
};

// Make authService available globally
window.authService = authService;
