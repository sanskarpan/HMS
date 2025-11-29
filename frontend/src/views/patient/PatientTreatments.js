/**
 * Patient Treatments View Component
 * Shows all treatment records.
 */

const PatientTreatments = {
    name: 'PatientTreatments',

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
                            <li class="breadcrumb-item active">Treatment Records</li>
                        </ol>
                    </nav>
                    <h2><i class="bi bi-file-medical"></i> Treatment Records</h2>
                    <p class="text-muted">View all your treatment and diagnosis records</p>
                </div>
            </div>

            <!-- Loading -->
            <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>

            <!-- Treatments List -->
            <div v-else>
                <div v-if="treatments.length === 0" class="text-center py-5">
                    <i class="bi bi-file-medical display-1 text-muted"></i>
                    <p class="text-muted mt-3">No treatment records found</p>
                </div>

                <div class="row g-4">
                    <div class="col-md-6" v-for="treatment in treatments" :key="treatment.id">
                        <div class="card h-100 shadow-sm">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <span>
                                    <i class="bi bi-calendar me-2"></i>
                                    {{ formatDate(treatment.treatment_date || treatment.appointment.appointment_date) }}
                                </span>
                                <span class="badge bg-success">{{ treatment.visit_type || 'In-person' }}</span>
                            </div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <small class="text-muted">Treated by</small>
                                    <p class="mb-0 fw-bold">
                                        Dr. {{ treatment.appointment.doctor ? treatment.appointment.doctor.full_name : 'N/A' }}
                                        <span class="text-muted fw-normal">
                                            ({{ treatment.appointment.doctor ? treatment.appointment.doctor.department : 'General' }})
                                        </span>
                                    </p>
                                </div>

                                <div class="mb-3">
                                    <small class="text-muted">Diagnosis</small>
                                    <p class="mb-0">{{ treatment.diagnosis || 'Not specified' }}</p>
                                </div>

                                <div class="mb-3">
                                    <small class="text-muted">Prescription</small>
                                    <pre class="bg-light p-2 rounded small mb-0" style="white-space: pre-wrap;">{{ treatment.prescription || 'No prescription' }}</pre>
                                </div>

                                <div v-if="treatment.tests_recommended" class="mb-3">
                                    <small class="text-muted">Tests Recommended</small>
                                    <p class="mb-0">{{ treatment.tests_recommended }}</p>
                                </div>

                                <div v-if="treatment.notes" class="mb-3">
                                    <small class="text-muted">Doctor's Notes</small>
                                    <p class="mb-0 text-muted small">{{ treatment.notes }}</p>
                                </div>
                            </div>
                            <div class="card-footer bg-transparent" v-if="treatment.follow_up_date">
                                <small class="text-primary">
                                    <i class="bi bi-calendar-check me-1"></i>
                                    Follow-up: {{ formatDate(treatment.follow_up_date) }}
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,

    data() {
        return {
            treatments: [],
            loading: true
        };
    },

    async created() {
        await this.loadTreatments();
    },

    methods: {
        async loadTreatments() {
            this.loading = true;
            const response = await patientService.getTreatments();
            if (response.success) {
                this.treatments = response.treatments;
            }
            this.loading = false;
        },

        formatDate(dateStr) {
            if (!dateStr) return '';
            const date = new Date(dateStr);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        }
    }
};

window.PatientTreatments = PatientTreatments;
