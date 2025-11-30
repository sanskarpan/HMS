// Form validation service - matches backend validation rules

const validationService = {
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

    validateField(fieldType, value, options = {}) {
        const rule = this.rules[fieldType];
        const { required = true, customMessage = null } = options;

        if (required && (!value || (typeof value === 'string' && !value.trim()))) {
            return {
                valid: false,
                message: customMessage || `This field is required`
            };
        }

        if (!required && (!value || (typeof value === 'string' && !value.trim()))) {
            return { valid: true, message: '' };
        }

        if (!rule) {
            return { valid: true, message: '' };
        }

        const strValue = String(value).trim();

        if (rule.minLength && strValue.length < rule.minLength) {
            return {
                valid: false,
                message: customMessage || rule.message || `Minimum ${rule.minLength} characters required`
            };
        }

        if (rule.maxLength && strValue.length > rule.maxLength) {
            return {
                valid: false,
                message: customMessage || `Maximum ${rule.maxLength} characters allowed`
            };
        }

        if (rule.pattern && !rule.pattern.test(strValue)) {
            return {
                valid: false,
                message: customMessage || rule.message
            };
        }

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

    validateEmail(email) {
        return this.validateField('email', email);
    },

    validateUsername(username) {
        return this.validateField('username', username);
    },

    validatePassword(password) {
        const result = this.validateField('password', password);

        if (!result.valid) {
            return { ...result, strength: 'weak' };
        }

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

    validatePasswordMatch(password, confirmPassword) {
        if (!confirmPassword) {
            return { valid: false, message: 'Please confirm your password' };
        }
        if (password !== confirmPassword) {
            return { valid: false, message: 'Passwords do not match' };
        }
        return { valid: true, message: '' };
    },

    validatePhone(phone, required = true) {
        return this.validateField('phone', phone, { required });
    },

    validateDateOfBirth(dateString) {
        if (!dateString) {
            return { valid: true, message: '' };
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

        const maxDate = new Date();
        maxDate.setDate(maxDate.getDate() + 7);
        if (date > maxDate) {
            return { valid: false, message: 'Appointments can only be booked up to 7 days in advance' };
        }

        return { valid: true, message: '' };
    },

    validateForm(formData, validations) {
        const errors = {};
        let valid = true;

        for (const [field, config] of Object.entries(validations)) {
            const value = formData[field];
            let result;

            if (typeof config === 'function') {
                result = config(value, formData);
            } else if (typeof config === 'string') {
                result = this.validateField(config, value);
            } else {
                result = this.validateField(config.type, value, config);
            }

            if (!result.valid) {
                errors[field] = result.message;
                valid = false;
            }
        }

        return { valid, errors };
    },

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

    setValidationState(element, isValid) {
        if (!element) return;
        element.classList.remove('is-valid', 'is-invalid');
        element.classList.add(isValid ? 'is-valid' : 'is-invalid');
    },

    clearValidationState(element) {
        if (!element) return;
        element.classList.remove('is-valid', 'is-invalid');
    },

    showError(element, message) {
        if (!element) return;

        let feedback = element.parentElement.querySelector('.invalid-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            element.parentElement.appendChild(feedback);
        }

        feedback.textContent = message;
        this.setValidationState(element, false);
    },

    clearError(element) {
        if (!element) return;

        const feedback = element.parentElement.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.textContent = '';
        }
        this.clearValidationState(element);
    }
};

window.validationService = validationService;
