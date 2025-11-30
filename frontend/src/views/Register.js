const Register = {
    name: 'Register',

    template: `
        <div class="auth-container">
            <div class="auth-card" style="max-width: 500px;">
                <div class="card-header">
                    <h3><i class="bi bi-hospital text-primary"></i> HMS</h3>
                    <p class="subtitle">Patient Registration</p>
                </div>

                <div class="card-body">
                    <!-- Alert Messages -->
                    <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
                        <span v-if="typeof error === 'string'">{{ error }}</span>
                        <ul v-else class="mb-0">
                            <li v-for="err in error" :key="err">{{ err }}</li>
                        </ul>
                        <button type="button" class="btn-close" @click="error = ''"></button>
                    </div>

                    <form @submit.prevent="handleRegister">
                        <!-- Username -->
                        <div class="mb-3">
                            <label for="username" class="form-label">Username *</label>
                            <input type="text"
                                   class="form-control"
                                   id="username"
                                   v-model="form.username"
                                   placeholder="Choose a username"
                                   required
                                   minlength="3"
                                   :disabled="loading">
                            <div class="form-text">At least 3 characters</div>
                        </div>

                        <!-- Email -->
                        <div class="mb-3">
                            <label for="email" class="form-label">Email *</label>
                            <input type="email"
                                   class="form-control"
                                   id="email"
                                   v-model="form.email"
                                   placeholder="your@email.com"
                                   required
                                   :disabled="loading">
                        </div>

                        <!-- Password -->
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="password" class="form-label">Password *</label>
                                <input :type="showPassword ? 'text' : 'password'"
                                       class="form-control"
                                       id="password"
                                       v-model="form.password"
                                       placeholder="Password"
                                       required
                                       minlength="6"
                                       :disabled="loading">
                                <div class="form-text">At least 6 characters</div>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="confirmPassword" class="form-label">Confirm Password *</label>
                                <input :type="showPassword ? 'text' : 'password'"
                                       class="form-control"
                                       id="confirmPassword"
                                       v-model="form.confirmPassword"
                                       placeholder="Confirm password"
                                       required
                                       :disabled="loading">
                            </div>
                        </div>

                        <div class="form-check mb-3">
                            <input class="form-check-input" type="checkbox" id="showPassword"
                                   v-model="showPassword">
                            <label class="form-check-label" for="showPassword">
                                Show password
                            </label>
                        </div>

                        <hr>

                        <!-- Full Name -->
                        <div class="mb-3">
                            <label for="fullName" class="form-label">Full Name *</label>
                            <input type="text"
                                   class="form-control"
                                   id="fullName"
                                   v-model="form.full_name"
                                   placeholder="Your full name"
                                   required
                                   :disabled="loading">
                        </div>

                        <!-- Phone -->
                        <div class="mb-3">
                            <label for="phone" class="form-label">Phone Number *</label>
                            <input type="tel"
                                   class="form-control"
                                   id="phone"
                                   v-model="form.phone"
                                   placeholder="+1234567890"
                                   required
                                   :disabled="loading">
                        </div>

                        <div class="row">
                            <!-- Date of Birth -->
                            <div class="col-md-6 mb-3">
                                <label for="dob" class="form-label">Date of Birth</label>
                                <input type="date"
                                       class="form-control"
                                       id="dob"
                                       v-model="form.date_of_birth"
                                       :max="maxDate"
                                       :disabled="loading">
                            </div>

                            <!-- Gender -->
                            <div class="col-md-6 mb-3">
                                <label for="gender" class="form-label">Gender</label>
                                <select class="form-select" id="gender" v-model="form.gender"
                                        :disabled="loading">
                                    <option value="">Select gender</option>
                                    <option value="male">Male</option>
                                    <option value="female">Female</option>
                                    <option value="other">Other</option>
                                </select>
                            </div>
                        </div>

                        <!-- Blood Group -->
                        <div class="mb-3">
                            <label for="bloodGroup" class="form-label">Blood Group</label>
                            <select class="form-select" id="bloodGroup" v-model="form.blood_group"
                                    :disabled="loading">
                                <option value="">Select blood group</option>
                                <option value="A+">A+</option>
                                <option value="A-">A-</option>
                                <option value="B+">B+</option>
                                <option value="B-">B-</option>
                                <option value="AB+">AB+</option>
                                <option value="AB-">AB-</option>
                                <option value="O+">O+</option>
                                <option value="O-">O-</option>
                            </select>
                        </div>

                        <!-- Address -->
                        <div class="mb-3">
                            <label for="address" class="form-label">Address</label>
                            <textarea class="form-control"
                                      id="address"
                                      v-model="form.address"
                                      rows="2"
                                      placeholder="Your address"
                                      :disabled="loading"></textarea>
                        </div>

                        <!-- Submit Button -->
                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-primary" :disabled="loading">
                                <span v-if="loading">
                                    <span class="spinner-border spinner-border-sm" role="status"></span>
                                    Registering...
                                </span>
                                <span v-else>
                                    <i class="bi bi-person-plus"></i> Register
                                </span>
                            </button>
                        </div>
                    </form>

                    <!-- Login Link -->
                    <div class="text-center mt-4">
                        <p class="mb-0">
                            Already have an account?
                            <router-link to="/login" class="text-primary text-decoration-none">
                                Login
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
                email: '',
                password: '',
                confirmPassword: '',
                full_name: '',
                phone: '',
                date_of_birth: '',
                gender: '',
                blood_group: '',
                address: ''
            },
            loading: false,
            error: '',
            showPassword: false
        };
    },

    computed: {
        maxDate() {
            // Maximum date is today (can't be born in the future)
            return new Date().toISOString().split('T')[0];
        }
    },

    created() {
        // Redirect if already logged in
        if (authService.isAuthenticated()) {
            this.$router.push(authService.getDashboardRoute());
        }
    },

    methods: {
        validateForm() {
            const errors = [];

            if (!this.form.username || this.form.username.length < 3) {
                errors.push('Username must be at least 3 characters');
            }

            if (!this.form.email || !this.form.email.includes('@')) {
                errors.push('Please enter a valid email address');
            }

            if (!this.form.password || this.form.password.length < 6) {
                errors.push('Password must be at least 6 characters');
            }

            if (this.form.password !== this.form.confirmPassword) {
                errors.push('Passwords do not match');
            }

            if (!this.form.full_name) {
                errors.push('Full name is required');
            }

            if (!this.form.phone) {
                errors.push('Phone number is required');
            }

            return errors;
        },

        async handleRegister() {
            // Reset error
            this.error = '';

            // Validate form
            const errors = this.validateForm();
            if (errors.length > 0) {
                this.error = errors;
                return;
            }

            this.loading = true;

            try {
                // Prepare data (exclude confirmPassword)
                const { confirmPassword, ...userData } = this.form;

                const response = await authService.register(userData);

                if (response.success) {
                    // Redirect to patient dashboard
                    this.$router.push('/patient/dashboard');
                } else {
                    this.error = response.errors || response.message || 'Registration failed';
                }
            } catch (err) {
                this.error = 'An error occurred. Please try again.';
                console.error('Registration error:', err);
            } finally {
                this.loading = false;
            }
        }
    }
};

// Make component available globally
window.Register = Register;
