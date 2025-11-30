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
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h2><i class="bi bi-file-medical"></i> Treatment Records</h2>
                            <p class="text-muted mb-0">View all your treatment and diagnosis records</p>
                        </div>
                        <button
                            class="btn btn-success"
                            @click="exportToCSV"
                            :disabled="exporting || treatments.length === 0">
                            <span v-if="exporting">
                                <span class="spinner-border spinner-border-sm me-1"></span>
                                Exporting...
                            </span>
                            <span v-else>
                                <i class="bi bi-download me-1"></i> Export as CSV
                            </span>
                        </button>
                    </div>
                </div>
            </div>

            <!-- Export Status Alert -->
            <div v-if="exportStatus" class="alert" :class="exportStatusClass" role="alert">
                <i class="bi" :class="exportStatusIcon"></i>
                {{ exportStatus }}
                <a v-if="downloadUrl" :href="downloadUrl" class="alert-link ms-2" download>
                    Download Now
                </a>
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
            loading: true,
            exporting: false,
            exportStatus: null,
            exportStatusType: 'info',
            downloadUrl: null,
            exportTaskId: null
        };
    },

    computed: {
        exportStatusClass() {
            return `alert-${this.exportStatusType}`;
        },
        exportStatusIcon() {
            const icons = {
                'info': 'bi-info-circle',
                'success': 'bi-check-circle',
                'warning': 'bi-exclamation-triangle',
                'danger': 'bi-x-circle'
            };
            return icons[this.exportStatusType] || 'bi-info-circle';
        }
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

        async exportToCSV() {
            this.exporting = true;
            this.exportStatus = 'Starting export...';
            this.exportStatusType = 'info';
            this.downloadUrl = null;

            try {
                const response = await patientService.downloadExportDirect();

                if (response.blob) {
                    // Synchronous download (fallback when Celery not available)
                    const url = window.URL.createObjectURL(response.blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `treatment_history_${new Date().toISOString().split('T')[0]}.csv`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);

                    this.exportStatus = 'Export downloaded successfully!';
                    this.exportStatusType = 'success';
                } else if (response.task_id) {
                    // Async export started
                    this.exportTaskId = response.task_id;
                    this.exportStatus = 'Export started. Processing...';
                    this.pollExportStatus();
                } else {
                    this.exportStatus = response.message || 'Export failed';
                    this.exportStatusType = 'danger';
                }
            } catch (error) {
                this.exportStatus = 'Export failed: ' + error.message;
                this.exportStatusType = 'danger';
            } finally {
                this.exporting = false;
            }
        },

        async pollExportStatus() {
            if (!this.exportTaskId) return;

            const maxAttempts = 30;
            let attempts = 0;

            const poll = async () => {
                attempts++;
                try {
                    const status = await patientService.getExportStatus(this.exportTaskId);

                    if (status.status === 'completed') {
                        this.exportStatus = 'Export ready!';
                        this.exportStatusType = 'success';
                        if (status.file_id) {
                            this.downloadUrl = patientService.getExportDownloadUrl(status.file_id);
                        }
                        return;
                    } else if (status.status === 'failed') {
                        this.exportStatus = 'Export failed: ' + (status.error || 'Unknown error');
                        this.exportStatusType = 'danger';
                        return;
                    } else if (attempts < maxAttempts) {
                        this.exportStatus = `Processing... ${status.progress || 0}%`;
                        setTimeout(poll, 2000);
                    } else {
                        this.exportStatus = 'Export is taking longer than expected. Check back later.';
                        this.exportStatusType = 'warning';
                    }
                } catch (error) {
                    this.exportStatus = 'Error checking status: ' + error.message;
                    this.exportStatusType = 'warning';
                }
            };

            poll();
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
