const DoctorProfile = {
    name: 'DoctorProfile',

    template: `
        <div class="container-fluid dashboard-container">
            <!-- Header -->
            <div class="row mb-4">
                <div class="col">
                    <nav aria-label="breadcrumb">
                        <ol class="breadcrumb">
                            <li class="breadcrumb-item">
                                <router-link to="/doctor/dashboard">Dashboard</router-link>
                            </li>
                            <li class="breadcrumb-item active">Profile</li>
                        </ol>
                    </nav>
                    <h2><i class="bi bi-person-circle"></i> My Profile</h2>
                </div>
            </div>

            <!-- Loading -->
            <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>

            <!-- Profile Form -->
            <div v-else class="row">
                <div class="col-lg-8">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">Profile Information</h5>
                        </div>
                        <div class="card-body">
                            <form @submit.prevent="saveProfile">
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Full Name *</label>
                                        <input type="text" class="form-control" v-model="profile.full_name" required>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Email *</label>
                                        <input type="email" class="form-control" v-model="profile.email" required>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Phone</label>
                                        <input type="tel" class="form-control" v-model="profile.phone">
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Specialization</label>
                                        <input type="text" class="form-control" v-model="profile.specialization">
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Qualification</label>
                                        <input type="text" class="form-control" v-model="profile.qualification"
                                               placeholder="e.g., MBBS, MD">
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Experience (Years)</label>
                                        <input type="number" class="form-control" v-model="profile.experience_years"
                                               min="0" max="60">
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Consultation Fee</label>
                                    <div class="input-group">
                                        <span class="input-group-text">$</span>
                                        <input type="number" class="form-control" v-model="profile.consultation_fee"
                                               min="0" step="0.01">
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Bio</label>
                                    <textarea class="form-control" v-model="profile.bio" rows="3"
                                              placeholder="Brief description about yourself..."></textarea>
                                </div>

                                <div v-if="formError" class="alert alert-danger">{{ formError }}</div>
                                <div v-if="formSuccess" class="alert alert-success">{{ formSuccess }}</div>

                                <button type="submit" class="btn btn-primary" :disabled="saving">
                                    <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
                                    Save Changes
                                </button>
                            </form>
                        </div>
                    </div>

                    <!-- Change Password -->
                    <div class="card mt-4">
                        <div class="card-header">
                            <h5 class="mb-0">Change Password</h5>
                        </div>
                        <div class="card-body">
                            <form @submit.prevent="changePassword">
                                <div class="row">
                                    <div class="col-md-4 mb-3">
                                        <label class="form-label">Current Password</label>
                                        <input type="password" class="form-control" v-model="passwordForm.current_password">
                                    </div>
                                    <div class="col-md-4 mb-3">
                                        <label class="form-label">New Password</label>
                                        <input type="password" class="form-control" v-model="passwordForm.new_password">
                                    </div>
                                    <div class="col-md-4 mb-3">
                                        <label class="form-label">Confirm Password</label>
                                        <input type="password" class="form-control" v-model="passwordForm.confirm_password">
                                    </div>
                                </div>
                                <div v-if="passwordError" class="alert alert-danger">{{ passwordError }}</div>
                                <div v-if="passwordSuccess" class="alert alert-success">{{ passwordSuccess }}</div>
                                <button type="submit" class="btn btn-outline-primary" :disabled="savingPassword">
                                    <span v-if="savingPassword" class="spinner-border spinner-border-sm me-1"></span>
                                    Update Password
                                </button>
                            </form>
                        </div>
                    </div>
                </div>

                <!-- Profile Summary -->
                <div class="col-lg-4">
                    <div class="card">
                        <div class="card-body text-center">
                            <div class="bg-primary-soft rounded-circle mx-auto mb-3" style="width: 100px; height: 100px; display: flex; align-items: center; justify-content: center;">
                                <i class="bi bi-person-fill display-4 text-primary"></i>
                            </div>
                            <h5>Dr. {{ profile.full_name }}</h5>
                            <p class="text-muted mb-1">{{ profile.specialization || 'Specialization not set' }}</p>
                            <p class="text-muted small">{{ profile.department || 'Department not assigned' }}</p>
                            <hr>
                            <div class="text-start">
                                <p class="mb-1"><i class="bi bi-envelope me-2"></i>{{ profile.email }}</p>
                                <p class="mb-1"><i class="bi bi-phone me-2"></i>{{ profile.phone || 'Not set' }}</p>
                                <p class="mb-1"><i class="bi bi-mortarboard me-2"></i>{{ profile.qualification || 'Not set' }}</p>
                                <p class="mb-0"><i class="bi bi-clock-history me-2"></i>{{ profile.experience_years || 0 }} years experience</p>
                            </div>
                        </div>
                    </div>

                    <div class="card mt-4">
                        <div class="card-header">
                            <h6 class="mb-0">Account Status</h6>
                        </div>
                        <div class="card-body">
                            <p class="mb-1">
                                <span class="badge" :class="profile.is_active ? 'bg-success' : 'bg-danger'">
                                    {{ profile.is_active ? 'Active' : 'Inactive' }}
                                </span>
                            </p>
                            <small class="text-muted">Member since {{ formatDate(profile.created_at) }}</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,

    data() {
        return {
            profile: {
                full_name: '',
                email: '',
                phone: '',
                specialization: '',
                qualification: '',
                experience_years: 0,
                consultation_fee: 0,
                bio: '',
                department: '',
                is_active: true,
                created_at: null
            },
            passwordForm: {
                current_password: '',
                new_password: '',
                confirm_password: ''
            },
            loading: true,
            saving: false,
            savingPassword: false,
            formError: null,
            formSuccess: null,
            passwordError: null,
            passwordSuccess: null
        };
    },

    async created() {
        await this.loadProfile();
    },

    methods: {
        async loadProfile() {
            this.loading = true;
            const response = await doctorService.getProfile();
            if (response.success) {
                this.profile = { ...this.profile, ...response.doctor };
            }
            this.loading = false;
        },

        async saveProfile() {
            this.saving = true;
            this.formError = null;
            this.formSuccess = null;

            const response = await doctorService.updateProfile({
                full_name: this.profile.full_name,
                email: this.profile.email,
                phone: this.profile.phone,
                specialization: this.profile.specialization,
                qualification: this.profile.qualification,
                experience_years: this.profile.experience_years,
                consultation_fee: this.profile.consultation_fee,
                bio: this.profile.bio
            });

            if (response.success) {
                this.formSuccess = 'Profile updated successfully';
            } else {
                this.formError = response.message || 'Failed to update profile';
            }
            this.saving = false;
        },

        async changePassword() {
            this.passwordError = null;
            this.passwordSuccess = null;

            if (this.passwordForm.new_password !== this.passwordForm.confirm_password) {
                this.passwordError = 'Passwords do not match';
                return;
            }

            if (this.passwordForm.new_password.length < 6) {
                this.passwordError = 'Password must be at least 6 characters';
                return;
            }

            this.savingPassword = true;

            const response = await api.post('/auth/change-password', {
                current_password: this.passwordForm.current_password,
                new_password: this.passwordForm.new_password
            });

            if (response.success) {
                this.passwordSuccess = 'Password changed successfully';
                this.passwordForm = { current_password: '', new_password: '', confirm_password: '' };
            } else {
                this.passwordError = response.message || 'Failed to change password';
            }
            this.savingPassword = false;
        },

        formatDate(dateStr) {
            if (!dateStr) return 'N/A';
            return new Date(dateStr).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
        }
    }
};

window.DoctorProfile = DoctorProfile;
