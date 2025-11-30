/**
 * Frontend Validation Service
 * Provides comprehensive form validation with inline error messages.
 * Matches backend validation rules for consistency.
 */

const validationService = {
    // Validation Rules
    rules: {
        username: {
            minLength: 3,
            maxLength: 50,
            pattern: /^[a-zA-Z0-9_]+$/,
            message: 'Username must be 3-50 characters, letters, numbers, and underscores only'
        },
        email: {
            pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            message: 'Please enter a valid email address'
        },
        password: {
            minLength: 6,
            maxLength: 128,
            message: 'Password must be at least 6 characters'
        },
        phone: {
            pattern: /^[\d\s\-+()]{7,20}$/,
            message: 'Please enter a valid phone number'
        },
        fullName: {
            minLength: 2,
            maxLength: 100,
            pattern: /^[a-zA-Z\s'-]+$/,
            message: 'Name must be 2-100 characters, letters only'
        },
        date: {
            message: 'Please enter a valid date'
        },
        time: {
            pattern: /^([01]?[0-9]|2[0-3]):[0-5][0-9]$/,
            message: 'Please enter a valid time (HH:MM)'
        },
        consultationFee: {
            min: 0,
            max: 10000,
            message: 'Fee must be between 0 and 10000'
        },
        experienceYears: {
            min: 0,
            max: 70,
            message: 'Experience must be between 0 and 70 years'
        }
    },

    /**
     * Validate a single field
     * @param {string} fieldType - Type of field (username, email, etc.)
     * @param {any} value - Value to validate
     * @param {Object} options - Additional options (required, custom message)
     * @returns {Object} { valid: boolean, message: string }
     */
    validateField(fieldType, value, options = {}) {
        const rule = this.rules[fieldType];
        const { required = true, customMessage = null } = options;

        // Check required
        if (required && (!value || (typeof value === 'string' && !value.trim()))) {
            return {
                valid: false,
                message: customMessage || `This field is required`
            };
        }

        // Skip validation if not required and empty
        if (!required && (!value || (typeof value === 'string' && !value.trim()))) {
            return { valid: true, message: '' };
        }

        if (!rule) {
            return { valid: true, message: '' };
        }

        // String value validation
        const strValue = String(value).trim();

        // Min length check
        if (rule.minLength && strValue.length < rule.minLength) {
            return {
                valid: false,
                message: customMessage || rule.message || `Minimum ${rule.minLength} characters required`
            };
        }

        // Max length check
        if (rule.maxLength && strValue.length > rule.maxLength) {
            return {
                valid: false,
                message: customMessage || `Maximum ${rule.maxLength} characters allowed`
            };
        }

        // Pattern check
        if (rule.pattern && !rule.pattern.test(strValue)) {
            return {
                valid: false,
                message: customMessage || rule.message
            };
        }

        // Numeric min/max
        if (rule.min !== undefined || rule.max !== undefined) {
            const numValue = parseFloat(value);
            if (isNaN(numValue)) {
                return {
                    valid: false,
                    message: 'Please enter a valid number'
                };
            }
            if (rule.min !== undefined && numValue < rule.min) {
                return {
                    valid: false,
                    message: customMessage || rule.message || `Minimum value is ${rule.min}`
                };
            }
            if (rule.max !== undefined && numValue > rule.max) {
                return {
                    valid: false,
                    message: customMessage || rule.message || `Maximum value is ${rule.max}`
                };
            }
        }

        return { valid: true, message: '' };
    },

    /**
     * Validate email format
     * @param {string} email
     * @returns {Object} { valid: boolean, message: string }
     */
    validateEmail(email) {
        return this.validateField('email', email);
    },

    /**
     * Validate username
     * @param {string} username
     * @returns {Object} { valid: boolean, message: string }
     */
    validateUsername(username) {
        return this.validateField('username', username);
    },

    /**
     * Validate password with strength indicator
     * @param {string} password
     * @returns {Object} { valid: boolean, message: string, strength: string }
     */
    validatePassword(password) {
        const result = this.validateField('password', password);

        if (!result.valid) {
            return { ...result, strength: 'weak' };
        }

        // Calculate password strength
        let strength = 0;
        if (password.length >= 8) strength++;
        if (password.length >= 12) strength++;
        if (/[A-Z]/.test(password)) strength++;
        if (/[a-z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^A-Za-z0-9]/.test(password)) strength++;

        let strengthLabel = 'weak';
        let strengthMessage = 'Weak password';

        if (strength >= 5) {
            strengthLabel = 'strong';
            strengthMessage = 'Strong password';
        } else if (strength >= 3) {
            strengthLabel = 'good';
            strengthMessage = 'Good password';
        } else if (strength >= 2) {
            strengthLabel = 'fair';
            strengthMessage = 'Fair password';
        }

        return {
            valid: true,
            message: strengthMessage,
            strength: strengthLabel
        };
    },

    /**
     * Validate password confirmation
     * @param {string} password
     * @param {string} confirmPassword
     * @returns {Object} { valid: boolean, message: string }
     */
    validatePasswordMatch(password, confirmPassword) {
        if (!confirmPassword) {
            return { valid: false, message: 'Please confirm your password' };
        }
        if (password !== confirmPassword) {
            return { valid: false, message: 'Passwords do not match' };
        }
        return { valid: true, message: '' };
    },

    /**
     * Validate phone number
     * @param {string} phone
     * @param {boolean} required
     * @returns {Object} { valid: boolean, message: string }
     */
    validatePhone(phone, required = true) {
        return this.validateField('phone', phone, { required });
    },

    /**
     * Validate date of birth
     * @param {string} dateString - Date in YYYY-MM-DD format
     * @returns {Object} { valid: boolean, message: string }
     */
    validateDateOfBirth(dateString) {
        if (!dateString) {
            return { valid: true, message: '' }; // Optional field
        }

        const date = new Date(dateString);
        const today = new Date();

        if (isNaN(date.getTime())) {
            return { valid: false, message: 'Invalid date format' };
        }

        if (date > today) {
            return { valid: false, message: 'Date cannot be in the future' };
        }

        const maxAge = new Date();
        maxAge.setFullYear(maxAge.getFullYear() - 150);
        if (date < maxAge) {
            return { valid: false, message: 'Invalid date of birth' };
        }

        return { valid: true, message: '' };
    },

    /**
     * Validate appointment date
     * @param {string} dateString - Date in YYYY-MM-DD format
     * @returns {Object} { valid: boolean, message: string }
     */
    validateAppointmentDate(dateString) {
        if (!dateString) {
            return { valid: false, message: 'Please select a date' };
        }

        const date = new Date(dateString);
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        if (isNaN(date.getTime())) {
            return { valid: false, message: 'Invalid date format' };
        }

        if (date < today) {
            return { valid: false, message: 'Cannot book appointments in the past' };
        }

        // Max 7 days in advance
        const maxDate = new Date();
        maxDate.setDate(maxDate.getDate() + 7);
        if (date > maxDate) {
            return { valid: false, message: 'Appointments can only be booked up to 7 days in advance' };
        }

        return { valid: true, message: '' };
    },

    /**
     * Validate a form with multiple fields
     * @param {Object} formData - Form data object
     * @param {Object} validations - Validation rules for each field
     * @returns {Object} { valid: boolean, errors: Object }
     */
    validateForm(formData, validations) {
        const errors = {};
        let valid = true;

        for (const [field, config] of Object.entries(validations)) {
            const value = formData[field];
            let result;

            if (typeof config === 'function') {
                // Custom validation function
                result = config(value, formData);
            } else if (typeof config === 'string') {
                // Simple field type validation
                result = this.validateField(config, value);
            } else {
                // Object config
                result = this.validateField(config.type, value, config);
            }

            if (!result.valid) {
                errors[field] = result.message;
                valid = false;
            }
        }

        return { valid, errors };
    },

    /**
     * Sanitize input to prevent XSS
     * @param {string} input
     * @returns {string} Sanitized input
     */
    sanitize(input) {
        if (typeof input !== 'string') return input;
        return input
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#x27;')
            .trim();
    },

    /**
     * Apply validation class to form element
     * @param {HTMLElement} element
     * @param {boolean} isValid
     */
    setValidationState(element, isValid) {
        if (!element) return;
        element.classList.remove('is-valid', 'is-invalid');
        element.classList.add(isValid ? 'is-valid' : 'is-invalid');
    },

    /**
     * Clear validation state from element
     * @param {HTMLElement} element
     */
    clearValidationState(element) {
        if (!element) return;
        element.classList.remove('is-valid', 'is-invalid');
    },

    /**
     * Show inline error message
     * @param {HTMLElement} element
     * @param {string} message
     */
    showError(element, message) {
        if (!element) return;

        // Find or create feedback element
        let feedback = element.parentElement.querySelector('.invalid-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            element.parentElement.appendChild(feedback);
        }

        feedback.textContent = message;
        this.setValidationState(element, false);
    },

    /**
     * Clear error from element
     * @param {HTMLElement} element
     */
    clearError(element) {
        if (!element) return;

        const feedback = element.parentElement.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.textContent = '';
        }
        this.clearValidationState(element);
    }
};

// Make service available globally
window.validationService = validationService;
