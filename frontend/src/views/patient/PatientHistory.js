const PatientHistory = {
    name: 'PatientHistory',

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
                            <li class="breadcrumb-item active">Appointment History</li>
                        </ol>
                    </nav>
                    <h2><i class="bi bi-clock-history"></i> Appointment History</h2>
                    <p class="text-muted">View all your past appointments and treatment records</p>
                </div>
            </div>

            <!-- Loading -->
            <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>

            <!-- History List -->
            <div v-else>
                <div v-if="history.length === 0" class="text-center py-5">
                    <i class="bi bi-folder-x display-1 text-muted"></i>
                    <p class="text-muted mt-3">No appointment history found</p>
                </div>

                <div class="accordion" id="historyAccordion">
                    <div class="accordion-item" v-for="(apt, index) in history" :key="apt.id">
                        <h2 class="accordion-header">
                            <button class="accordion-button collapsed" type="button"
                                    :data-bs-toggle="'collapse'" :data-bs-target="'#collapse' + apt.id">
                                <div class="d-flex w-100 justify-content-between align-items-center me-3">
                                    <div>
                                        <strong>{{ formatDate(apt.appointment_date) }}</strong>
                                        <span class="text-muted ms-2">{{ apt.appointment_time }}</span>
                                    </div>
                                    <div class="d-flex align-items-center">
                                        <span class="me-3">Dr. {{ apt.doctor ? apt.doctor.full_name : 'N/A' }}</span>
                                        <span class="badge" :class="getStatusBadge(apt.status)">{{ apt.status }}</span>
                                    </div>
                                </div>
                            </button>
                        </h2>
                        <div :id="'collapse' + apt.id" class="accordion-collapse collapse"
                             data-bs-parent="#historyAccordion">
                            <div class="accordion-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6>Appointment Details</h6>
                                        <table class="table table-sm">
                                            <tr>
                                                <td class="text-muted">Department</td>
                                                <td>{{ apt.department_name || 'General' }}</td>
                                            </tr>
                                            <tr>
                                                <td class="text-muted">Doctor</td>
                                                <td>Dr. {{ apt.doctor ? apt.doctor.full_name : 'N/A' }}</td>
                                            </tr>
                                            <tr>
                                                <td class="text-muted">Reason</td>
                                                <td>{{ apt.reason || 'Not specified' }}</td>
                                            </tr>
                                            <tr v-if="apt.cancelled_at">
                                                <td class="text-muted">Cancelled</td>
                                                <td>{{ apt.cancellation_reason || 'No reason provided' }}</td>
                                            </tr>
                                        </table>
                                    </div>
                                    <div class="col-md-6" v-if="apt.treatment">
                                        <h6>Treatment Details</h6>
                                        <div class="bg-light p-3 rounded">
                                            <p class="mb-2">
                                                <strong>Diagnosis:</strong><br>
                                                {{ apt.treatment.diagnosis || 'N/A' }}
                                            </p>
                                            <p class="mb-2">
                                                <strong>Prescription:</strong><br>
                                                <pre class="mb-0" style="white-space: pre-wrap;">{{ apt.treatment.prescription || 'N/A' }}</pre>
                                            </p>
                                            <p class="mb-2" v-if="apt.treatment.tests_recommended">
                                                <strong>Tests:</strong><br>
                                                {{ apt.treatment.tests_recommended }}
                                            </p>
                                            <p class="mb-2" v-if="apt.treatment.notes">
                                                <strong>Notes:</strong><br>
                                                {{ apt.treatment.notes }}
                                            </p>
                                            <p class="mb-0" v-if="apt.treatment.follow_up_date">
                                                <strong>Follow-up:</strong>
                                                <span class="text-primary">{{ formatDate(apt.treatment.follow_up_date) }}</span>
                                            </p>
                                        </div>
                                    </div>
                                    <div class="col-md-6" v-else-if="apt.status === 'completed'">
                                        <div class="alert alert-info mb-0">
                                            <i class="bi bi-info-circle"></i> Treatment details not yet available
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,

    data() {
        return {
            history: [],
            loading: true
        };
    },

    async created() {
        await this.loadHistory();
    },

    methods: {
        async loadHistory() {
            this.loading = true;
            const response = await patientService.getAppointmentHistory();
            if (response.success) {
                this.history = response.history;
            }
            this.loading = false;
        },

        formatDate(dateStr) {
            if (!dateStr) return '';
            const date = new Date(dateStr);
            return date.toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        },

        getStatusBadge(status) {
            const badges = {
                'booked': 'bg-primary',
                'completed': 'bg-success',
                'cancelled': 'bg-danger',
                'no_show': 'bg-warning text-dark'
            };
            return badges[status] || 'bg-secondary';
        }
    }
};

window.PatientHistory = PatientHistory;
