/**
 * Login View Component
 * Handles user authentication with username/email and password.
 */

const Login = {
    name: 'Login',

    template: `
        <div class="auth-container">
            <div class="auth-card">
                <div class="card-header">
                    <h3><i class="bi bi-hospital text-primary"></i> HMS</h3>
                    <p class="subtitle">Hospital Management System</p>
                </div>

                <div class="card-body">
                    <!-- Alert Messages -->
                    <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
                        {{ error }}
                        <button type="button" class="btn-close" @click="error = ''"></button>
                    </div>

                    <div v-if="success" class="alert alert-success alert-dismissible fade show" role="alert">
                        {{ success }}
                        <button type="button" class="btn-close" @click="success = ''"></button>
                    </div>

                    <form @submit.prevent="handleLogin">
                        <!-- Username/Email Field -->
                        <div class="mb-3">
                            <label for="username" class="form-label">Username or Email</label>
                            <div class="input-group">
                                <span class="input-group-text">
                                    <i class="bi bi-person"></i>
                                </span>
                                <input type="text"
                                       class="form-control"
                                       id="username"
                                       v-model="form.username"
                                       placeholder="Enter username or email"
                                       required
                                       :disabled="loading">
                            </div>
                        </div>

                        <!-- Password Field -->
                        <div class="mb-3">
                            <label for="password" class="form-label">Password</label>
                            <div class="input-group">
                                <span class="input-group-text">
                                    <i class="bi bi-lock"></i>
                                </span>
                                <input :type="showPassword ? 'text' : 'password'"
                                       class="form-control"
                                       id="password"
                                       v-model="form.password"
                                       placeholder="Enter password"
                                       required
                                       :disabled="loading">
                                <button class="btn btn-outline-secondary" type="button"
                                        @click="showPassword = !showPassword">
                                    <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                                </button>
                            </div>
                        </div>

                        <!-- Submit Button -->
                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-primary" :disabled="loading">
                                <span v-if="loading">
                                    <span class="spinner-border spinner-border-sm" role="status"></span>
                                    Logging in...
                                </span>
                                <span v-else>
                                    <i class="bi bi-box-arrow-in-right"></i> Login
                                </span>
                            </button>
                        </div>
                    </form>

                    <!-- Register Link -->
                    <div class="text-center mt-4">
                        <p class="mb-0">
                            Don't have an account?
                            <router-link to="/register" class="text-primary text-decoration-none">
                                Register as Patient
                            </router-link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    `,

    data() {
        return {
            form: {
                username: '',
                password: ''
            },
            loading: false,
            error: '',
            success: '',
            showPassword: false
        };
    },

    created() {
        // Redirect if already logged in
        if (authService.isAuthenticated()) {
            this.$router.push(authService.getDashboardRoute());
        }

        // Check for registration success message
        if (this.$route.query.registered) {
            this.success = 'Registration successful! Please login.';
        }
    },

    methods: {
        async handleLogin() {
            // Reset messages
            this.error = '';
            this.success = '';

            // Validate form
            if (!this.form.username || !this.form.password) {
                this.error = 'Please enter username and password';
                return;
            }

            this.loading = true;

            try {
                const response = await authService.login(
                    this.form.username,
                    this.form.password
                );

                if (response.success) {
                    // Redirect to appropriate dashboard
                    const dashboardRoute = authService.getDashboardRoute();
                    this.$router.push(dashboardRoute);
                } else {
                    this.error = response.message || 'Login failed. Please try again.';
                }
            } catch (err) {
                this.error = 'An error occurred. Please try again.';
                console.error('Login error:', err);
            } finally {
                this.loading = false;
            }
        }
    }
};

// Make component available globally
window.Login = Login;
