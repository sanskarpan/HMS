/**
 * Register View Component
 * Handles patient registration with form validation.
 */

const Register = {
    name: 'Register',

    

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
