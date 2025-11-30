const PatientProfile = {
    name: 'PatientProfile',

    template: `
        <div class="container-fluid dashboard-container">
            <!-- Header -->
            <div class="row mb-4">
                <div class="col">
                    <nav aria-label="breadcrumb">
                        <ol class="breadcrumb">
                            <li class="breadcrumb-item">
                                <router-link to="/patient/dashboard">Dashboard</router-link>
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
                            <h5 class="mb-0">Personal Information</h5>
                        </div>
                        <div class="card-body">
                            <form @submit.prevent="saveProfile">
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Full Name *</label>
                                        <input type="text" class="form-control" v-model="profile.full_name" required>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Email</label>
                                        <input type="email" class="form-control" :value="profile.email" disabled>
                                        <small class="text-muted">Email cannot be changed</small>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Phone *</label>
                                        <input type="tel" class="form-control" v-model="profile.phone" required>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Date of Birth</label>
                                        <input type="date" class="form-control" v-model="profile.date_of_birth">
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Gender</label>
                                        <select class="form-select" v-model="profile.gender">
                                            <option value="">Select Gender</option>
                                            <option value="male">Male</option>
                                            <option value="female">Female</option>
                                            <option value="other">Other</option>
                                        </select>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Blood Group</label>
                                        <select class="form-select" v-model="profile.blood_group">
                                            <option value="">Select Blood Group</option>
                                            <option v-for="bg in bloodGroups" :key="bg" :value="bg">{{ bg }}</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Address</label>
                                    <textarea class="form-control" v-model="profile.address" rows="2"></textarea>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Emergency Contact</label>
                                    <input type="tel" class="form-control" v-model="profile.emergency_contact"
                                           placeholder="Emergency contact number">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Medical History</label>
                                    <textarea class="form-control" v-model="profile.medical_history" rows="3"
                                              placeholder="Pre-existing conditions, allergies, etc."></textarea>
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
                </div>

                <!-- Profile Summary -->
                <div class="col-lg-4">
                    <div class="card">
                        <div class="card-body text-center">
                            <div class="bg-primary rounded-circle mx-auto mb-3" style="width: 100px; height: 100px; display: flex; align-items: center; justify-content: center;">
                                <i class="bi bi-person-fill display-4 text-white"></i>
                            </div>
                            <h5>{{ profile.full_name }}</h5>
                            <p class="text-muted mb-1">{{ profile.email }}</p>
                            <hr>
                            <div class="text-start">
                                <p class="mb-1"><i class="bi bi-phone me-2"></i>{{ profile.phone || 'Not set' }}</p>
                                <p class="mb-1"><i class="bi bi-calendar me-2"></i>Age: {{ profile.age || 'N/A' }}</p>
                                <p class="mb-1"><i class="bi bi-droplet me-2"></i>Blood: {{ profile.blood_group || 'Not set' }}</p>
                                <p class="mb-0"><i class="bi bi-geo-alt me-2"></i>{{ profile.address || 'Address not set' }}</p>
                            </div>
                        </div>
                    </div>

                    <div class="card mt-4">
                        <div class="card-header">
                            <h6 class="mb-0">Quick Stats</h6>
                        </div>
                        <div class="card-body">
                            <div class="d-flex justify-content-between mb-2">
                                <span>Total Appointments</span>
                                <strong>{{ stats.total || 0 }}</strong>
                            </div>
                            <div class="d-flex justify-content-between mb-2">
                                <span>Completed</span>
                                <strong class="text-success">{{ stats.completed || 0 }}</strong>
                            </div>
                            <div class="d-flex justify-content-between">
                                <span>Upcoming</span>
                                <strong class="text-primary">{{ stats.upcoming || 0 }}</strong>
                            </div>
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
                date_of_birth: '',
                gender: '',
                blood_group: '',
                address: '',
                emergency_contact: '',
                medical_history: '',
                age: null
            },
            stats: {
                total: 0,
                completed: 0,
                upcoming: 0
            },
            bloodGroups: ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
            loading: true,
            saving: false,
            formError: null,
            formSuccess: null
        };
    },

    async created() {
        await this.loadProfile();
    },

    methods: {
        async loadProfile() {
            this.loading = true;
            try {
                const [profileRes, statsRes] = await Promise.all([
                    patientService.getProfile(),
                    patientService.getDashboardStats()
                ]);

                if (profileRes.success) {
                    this.profile = { ...this.profile, ...profileRes.patient };
                }
                if (statsRes.success) {
                    this.stats = {
                        total: (statsRes.stats.upcoming_appointments || 0) + (statsRes.stats.completed_appointments || 0),
                        completed: statsRes.stats.completed_appointments || 0,
                        upcoming: statsRes.stats.upcoming_appointments || 0
                    };
                }
            } catch (error) {
                console.error('Failed to load profile:', error);
            }
            this.loading = false;
        },

        async saveProfile() {
            this.saving = true;
            this.formError = null;
            this.formSuccess = null;

            const response = await patientService.updateProfile({
                full_name: this.profile.full_name,
                phone: this.profile.phone,
                date_of_birth: this.profile.date_of_birth,
                gender: this.profile.gender,
                blood_group: this.profile.blood_group,
                address: this.profile.address,
                emergency_contact: this.profile.emergency_contact,
                medical_history: this.profile.medical_history
            });

            if (response.success) {
                this.formSuccess = 'Profile updated successfully';
                this.profile = { ...this.profile, ...response.patient };
            } else {
                this.formError = response.message || 'Failed to update profile';
            }
            this.saving = false;
        }
    }
};

window.PatientProfile = PatientProfile;
