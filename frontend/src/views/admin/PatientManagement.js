const PatientManagement = {
    name: 'PatientManagement',

    template: `
        <div class="container-fluid dashboard-container">
            <!-- Header -->
            <div class="row mb-4">
                <div class="col">
                    <nav aria-label="breadcrumb">
                        <ol class="breadcrumb">
                            <li class="breadcrumb-item">
                                <router-link to="/admin/dashboard">Dashboard</router-link>
                            </li>
                            <li class="breadcrumb-item active">Patients</li>
                        </ol>
                    </nav>
                    <h2><i class="bi bi-people"></i> Patient Management</h2>
                </div>
            </div>

            <!-- Search and Filter -->
            <div class="card mb-4">
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <div class="input-group">
                                <span class="input-group-text"><i class="bi bi-search"></i></span>
                                <input type="text" class="form-control"
                                       placeholder="Search by name, phone, or email..."
                                       v-model="searchQuery" @input="debouncedSearch">
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-check mt-2">
                                <input class="form-check-input" type="checkbox" id="includeInactive"
                                       v-model="includeInactive" @change="loadPatients">
                                <label class="form-check-label" for="includeInactive">
                                    Include inactive
                                </label>
                            </div>
                        </div>
                        <div class="col-md-3 text-end">
                            <span class="text-muted">{{ patients.length }} patients found</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>

            <!-- Patients Table -->
            <div v-else class="card">
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Email</th>
                                    <th>Phone</th>
                                    <th>Age</th>
                                    <th>Gender</th>
                                    <th>Blood Group</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="patient in patients" :key="patient.id"
                                    :class="{'table-secondary': !patient.is_active || patient.is_blacklisted}">
                                    <td><strong>{{ patient.full_name }}</strong></td>
                                    <td>{{ patient.email }}</td>
                                    <td>{{ patient.phone }}</td>
                                    <td>{{ patient.age || 'N/A' }}</td>
                                    <td>{{ formatGender(patient.gender) }}</td>
                                    <td>{{ patient.blood_group || 'N/A' }}</td>
                                    <td>
                                        <span v-if="patient.is_blacklisted" class="badge bg-danger">Blacklisted</span>
                                        <span v-else-if="!patient.is_active" class="badge bg-secondary">Inactive</span>
                                        <span v-else class="badge bg-success">Active</span>
                                    </td>
                                    <td>
                                        <div class="btn-group btn-group-sm">
                                            <button class="btn btn-outline-info" @click="viewPatient(patient)"
                                                    title="View Details">
                                                <i class="bi bi-eye"></i>
                                            </button>
                                            <button class="btn btn-outline-success" @click="viewTreatmentHistory(patient)"
                                                    title="Treatment History">
                                                <i class="bi bi-file-medical"></i>
                                            </button>
                                            <button class="btn btn-outline-primary" @click="editPatient(patient)"
                                                    title="Edit">
                                                <i class="bi bi-pencil"></i>
                                            </button>
                                            <button v-if="!patient.is_blacklisted"
                                                    class="btn btn-outline-warning" @click="blacklistPatient(patient)"
                                                    title="Blacklist">
                                                <i class="bi bi-person-slash"></i>
                                            </button>
                                            <button v-else class="btn btn-outline-success"
                                                    @click="unblacklistPatient(patient)" title="Unblacklist">
                                                <i class="bi bi-person-check"></i>
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                                <tr v-if="patients.length === 0">
                                    <td colspan="8" class="text-center text-muted py-4">
                                        No patients found
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- View Patient Modal -->
            <div class="modal fade" :class="{'show d-block': showViewModal}" tabindex="-1" v-if="showViewModal">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Patient Details</h5>
                            <button type="button" class="btn-close" @click="showViewModal = false"></button>
                        </div>
                        <div class="modal-body" v-if="selectedPatient">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6 class="text-muted">Personal Information</h6>
                                    <table class="table table-sm">
                                        <tr>
                                            <th>Full Name:</th>
                                            <td>{{ selectedPatient.full_name }}</td>
                                        </tr>
                                        <tr>
                                            <th>Email:</th>
                                            <td>{{ selectedPatient.email }}</td>
                                        </tr>
                                        <tr>
                                            <th>Phone:</th>
                                            <td>{{ selectedPatient.phone }}</td>
                                        </tr>
                                        <tr>
                                            <th>Date of Birth:</th>
                                            <td>{{ selectedPatient.date_of_birth || 'N/A' }}</td>
                                        </tr>
                                        <tr>
                                            <th>Age:</th>
                                            <td>{{ selectedPatient.age || 'N/A' }}</td>
                                        </tr>
                                        <tr>
                                            <th>Gender:</th>
                                            <td>{{ formatGender(selectedPatient.gender) }}</td>
                                        </tr>
                                    </table>
                                </div>
                                <div class="col-md-6">
                                    <h6 class="text-muted">Medical Information</h6>
                                    <table class="table table-sm">
                                        <tr>
                                            <th>Blood Group:</th>
                                            <td>{{ selectedPatient.blood_group || 'N/A' }}</td>
                                        </tr>
                                        <tr>
                                            <th>Emergency Contact:</th>
                                            <td>{{ selectedPatient.emergency_contact || 'N/A' }}</td>
                                        </tr>
                                        <tr>
                                            <th>Address:</th>
                                            <td>{{ selectedPatient.address || 'N/A' }}</td>
                                        </tr>
                                    </table>

                                    <h6 class="text-muted mt-3">Appointment Stats</h6>
                                    <div class="row text-center">
                                        <div class="col-4">
                                            <h4 class="mb-0">{{ selectedPatient.appointment_stats?.total || 0 }}</h4>
                                            <small class="text-muted">Total</small>
                                        </div>
                                        <div class="col-4">
                                            <h4 class="mb-0 text-success">{{ selectedPatient.appointment_stats?.completed || 0 }}</h4>
                                            <small class="text-muted">Completed</small>
                                        </div>
                                        <div class="col-4">
                                            <h4 class="mb-0 text-primary">{{ selectedPatient.appointment_stats?.upcoming || 0 }}</h4>
                                            <small class="text-muted">Upcoming</small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="row mt-3" v-if="selectedPatient.medical_history">
                                <div class="col-12">
                                    <h6 class="text-muted">Medical History</h6>
                                    <p class="mb-0">{{ selectedPatient.medical_history }}</p>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" @click="showViewModal = false">
                                Close
                            </button>
                            <button type="button" class="btn btn-primary" @click="editPatient(selectedPatient); showViewModal = false">
                                Edit Patient
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-backdrop fade show" v-if="showViewModal"></div>

            <!-- Edit Patient Modal -->
            <div class="modal fade" :class="{'show d-block': showEditModal}" tabindex="-1" v-if="showEditModal">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Edit Patient</h5>
                            <button type="button" class="btn-close" @click="showEditModal = false"></button>
                        </div>
                        <div class="modal-body">
                            <form @submit.prevent="savePatient">
                                <div class="row g-3">
                                    <div class="col-md-6">
                                        <label class="form-label">Full Name *</label>
                                        <input type="text" class="form-control" v-model="patientForm.full_name"
                                               required>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label">Phone *</label>
                                        <input type="tel" class="form-control" v-model="patientForm.phone"
                                               required>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label">Date of Birth</label>
                                        <input type="date" class="form-control" v-model="patientForm.date_of_birth">
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label">Gender</label>
                                        <select class="form-select" v-model="patientForm.gender">
                                            <option value="">Select Gender</option>
                                            <option value="male">Male</option>
                                            <option value="female">Female</option>
                                            <option value="other">Other</option>
                                        </select>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label">Blood Group</label>
                                        <select class="form-select" v-model="patientForm.blood_group">
                                            <option value="">Select Blood Group</option>
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
                                    <div class="col-md-6">
                                        <label class="form-label">Emergency Contact</label>
                                        <input type="tel" class="form-control" v-model="patientForm.emergency_contact">
                                    </div>
                                    <div class="col-12">
                                        <label class="form-label">Address</label>
                                        <textarea class="form-control" v-model="patientForm.address" rows="2"></textarea>
                                    </div>
                                    <div class="col-12">
                                        <label class="form-label">Medical History</label>
                                        <textarea class="form-control" v-model="patientForm.medical_history"
                                                  rows="3" placeholder="Pre-existing conditions, allergies..."></textarea>
                                    </div>
                                </div>

                                <div v-if="formError" class="alert alert-danger mt-3 mb-0">
                                    {{ formError }}
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" @click="showEditModal = false">
                                Cancel
                            </button>
                            <button type="button" class="btn btn-primary" @click="savePatient" :disabled="saving">
                                <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
                                Update
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-backdrop fade show" v-if="showEditModal"></div>

            <!-- Treatment History Modal -->
            <div class="modal fade" :class="{'show d-block': showTreatmentModal}" tabindex="-1" v-if="showTreatmentModal">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="bi bi-file-medical me-2"></i>
                                Treatment History - {{ selectedPatient?.full_name }}
                            </h5>
                            <button type="button" class="btn-close" @click="showTreatmentModal = false"></button>
                        </div>
                        <div class="modal-body">
                            <div v-if="loadingTreatments" class="text-center py-4">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                            </div>
                            <div v-else-if="treatments.length === 0" class="text-center py-4 text-muted">
                                <i class="bi bi-folder-x display-4"></i>
                                <p class="mt-2">No treatment records found</p>
                            </div>
                            <div v-else class="accordion" id="treatmentAccordion">
                                <div class="accordion-item" v-for="(treatment, index) in treatments" :key="treatment.id">
                                    <h2 class="accordion-header">
                                        <button class="accordion-button collapsed" type="button"
                                                :data-bs-toggle="'collapse'" :data-bs-target="'#treatment' + treatment.id">
                                            <div class="d-flex w-100 justify-content-between align-items-center me-3">
                                                <span>
                                                    <strong>{{ formatDate(treatment.appointment?.date) }}</strong>
                                                    <span class="text-muted ms-2">{{ treatment.visit_type }}</span>
                                                </span>
                                                <span class="badge bg-primary">
                                                    Dr. {{ treatment.appointment?.doctor_name || 'N/A' }}
                                                </span>
                                            </div>
                                        </button>
                                    </h2>
                                    <div :id="'treatment' + treatment.id" class="accordion-collapse collapse">
                                        <div class="accordion-body">
                                            <div class="row">
                                                <div class="col-md-6">
                                                    <h6 class="text-primary">Diagnosis</h6>
                                                    <p>{{ treatment.diagnosis }}</p>
                                                </div>
                                                <div class="col-md-6">
                                                    <h6 class="text-primary">Prescription</h6>
                                                    <pre class="bg-light p-2 rounded small" style="white-space: pre-wrap;">{{ treatment.prescription || 'None' }}</pre>
                                                </div>
                                            </div>
                                            <div class="row mt-3" v-if="treatment.tests_recommended || treatment.notes">
                                                <div class="col-md-6" v-if="treatment.tests_recommended">
                                                    <h6 class="text-primary">Tests Recommended</h6>
                                                    <p>{{ treatment.tests_recommended }}</p>
                                                </div>
                                                <div class="col-md-6" v-if="treatment.notes">
                                                    <h6 class="text-primary">Doctor's Notes</h6>
                                                    <p class="text-muted">{{ treatment.notes }}</p>
                                                </div>
                                            </div>
                                            <div v-if="treatment.follow_up_date" class="mt-2">
                                                <span class="badge bg-info">
                                                    <i class="bi bi-calendar-check me-1"></i>
                                                    Follow-up: {{ formatDate(treatment.follow_up_date) }}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" @click="showTreatmentModal = false">
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-backdrop fade show" v-if="showTreatmentModal"></div>

            <!-- Toast Notification -->
            <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 1100">
                <div class="toast align-items-center text-white border-0" :class="toastClass"
                     :class="{'show': showToast}" role="alert">
                    <div class="d-flex">
                        <div class="toast-body">{{ toastMessage }}</div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto"
                                @click="showToast = false"></button>
                    </div>
                </div>
            </div>
        </div>
    `,

    data() {
        return {
            patients: [],
            loading: true,
            saving: false,
            searchQuery: '',
            includeInactive: false,
            showViewModal: false,
            showEditModal: false,
            showTreatmentModal: false,
            selectedPatient: null,
            patientForm: {},
            formError: null,
            showToast: false,
            toastMessage: '',
            toastClass: 'bg-success',
            searchTimeout: null,
            treatments: [],
            loadingTreatments: false
        };
    },

    async created() {
        await this.loadPatients();
    },

    methods: {
        async loadPatients() {
            this.loading = true;
            const response = await adminService.getPatients({
                search: this.searchQuery,
                include_inactive: this.includeInactive
            });

            if (response.success) {
                this.patients = response.patients;
            }
            this.loading = false;
        },

        debouncedSearch() {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => {
                this.loadPatients();
            }, 300);
        },

        formatGender(gender) {
            if (!gender) return 'N/A';
            return gender.charAt(0).toUpperCase() + gender.slice(1);
        },

        async viewPatient(patient) {
            // Load full patient details
            const response = await adminService.getPatient(patient.id);
            if (response.success) {
                this.selectedPatient = response.patient;
                this.showViewModal = true;
            }
        },

        editPatient(patient) {
            this.selectedPatient = patient;
            this.patientForm = {
                full_name: patient.full_name,
                phone: patient.phone,
                date_of_birth: patient.date_of_birth || '',
                gender: patient.gender || '',
                blood_group: patient.blood_group || '',
                emergency_contact: patient.emergency_contact || '',
                address: patient.address || '',
                medical_history: patient.medical_history || ''
            };
            this.formError = null;
            this.showEditModal = true;
        },

        async savePatient() {
            this.saving = true;
            this.formError = null;

            try {
                const response = await adminService.updatePatient(this.selectedPatient.id, this.patientForm);

                if (response.success) {
                    this.showToastMessage('Patient updated successfully', 'bg-success');
                    this.showEditModal = false;
                    await this.loadPatients();
                } else {
                    this.formError = response.message || 'Update failed';
                }
            } catch (err) {
                this.formError = 'An error occurred';
            } finally {
                this.saving = false;
            }
        },

        async blacklistPatient(patient) {
            if (!confirm('Are you sure you want to blacklist ' + patient.full_name + '?')) return;

            const response = await adminService.togglePatientBlacklist(patient.id, true);
            if (response.success) {
                this.showToastMessage('Patient blacklisted successfully', 'bg-warning');
                await this.loadPatients();
            } else {
                this.showToastMessage(response.message || 'Failed to blacklist', 'bg-danger');
            }
        },

        async unblacklistPatient(patient) {
            const response = await adminService.togglePatientBlacklist(patient.id, false);
            if (response.success) {
                this.showToastMessage('Patient unblacklisted successfully', 'bg-success');
                await this.loadPatients();
            } else {
                this.showToastMessage(response.message || 'Failed to unblacklist', 'bg-danger');
            }
        },

        async viewTreatmentHistory(patient) {
            this.selectedPatient = patient;
            this.treatments = [];
            this.loadingTreatments = true;
            this.showTreatmentModal = true;

            const response = await adminService.getPatientTreatments(patient.id);
            if (response.success) {
                this.treatments = response.treatments;
            }
            this.loadingTreatments = false;
        },

        formatDate(dateStr) {
            if (!dateStr) return 'N/A';
            const date = new Date(dateStr);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        },

        showToastMessage(message, className = 'bg-success') {
            this.toastMessage = message;
            this.toastClass = className;
            this.showToast = true;
            setTimeout(() => {
                this.showToast = false;
            }, 3000);
        }
    }
};

// Make component available globally
window.PatientManagement = PatientManagement;
