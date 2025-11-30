const DoctorAppointments = {
    name: 'DoctorAppointments',

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
                            <li class="breadcrumb-item active">Appointments</li>
                        </ol>
                    </nav>
                    <h2><i class="bi bi-calendar3"></i> My Appointments</h2>
                </div>
            </div>

            <!-- Filters -->
            <div class="card mb-4">
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-2">
                            <label class="form-label">Period</label>
                            <select class="form-select" v-model="filters.period" @change="loadAppointments">
                                <option value="">All</option>
                                <option value="today">Today</option>
                                <option value="week">This Week</option>
                                <option value="month">This Month</option>
                            </select>
                        </div>
                        <div class="col-md-2">
                            <label class="form-label">Status</label>
                            <select class="form-select" v-model="filters.status" @change="loadAppointments">
                                <option value="">All Status</option>
                                <option value="booked">Booked</option>
                                <option value="completed">Completed</option>
                                <option value="cancelled">Cancelled</option>
                            </select>
                        </div>
                        <div class="col-md-3">
                            <label class="form-label">Specific Date</label>
                            <input type="date" class="form-control" v-model="filters.date"
                                   @change="loadAppointments">
                        </div>
                        <div class="col-md-3 d-flex align-items-end">
                            <button class="btn btn-outline-secondary me-2" @click="clearFilters">
                                <i class="bi bi-x-circle"></i> Clear
                            </button>
                            <button class="btn btn-outline-primary" @click="filters.period = 'today'; loadAppointments()">
                                <i class="bi bi-calendar-day"></i> Today
                            </button>
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

            <!-- Appointments Table -->
            <div v-else class="card">
                <div class="card-header">
                    <span class="text-muted">{{ appointments.length }} appointments found</span>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Time</th>
                                    <th>Patient</th>
                                    <th>Contact</th>
                                    <th>Reason</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="apt in appointments" :key="apt.id"
                                    :class="getRowClass(apt)">
                                    <td>
                                        <strong>{{ formatDate(apt.appointment_date) }}</strong>
                                        <span v-if="apt.is_today" class="badge bg-info ms-1">Today</span>
                                    </td>
                                    <td>{{ apt.appointment_time }}</td>
                                    <td>{{ apt.patient?.full_name || 'N/A' }}</td>
                                    <td>{{ apt.patient?.phone || 'N/A' }}</td>
                                    <td>{{ apt.reason || '-' }}</td>
                                    <td>
                                        <span class="badge" :class="getStatusClass(apt.status)">
                                            {{ apt.status }}
                                        </span>
                                    </td>
                                    <td>
                                        <div class="btn-group btn-group-sm" v-if="apt.status === 'booked'">
                                            <button class="btn btn-success" @click="openCompleteModal(apt)"
                                                    title="Complete">
                                                <i class="bi bi-check-circle"></i>
                                            </button>
                                            <button class="btn btn-warning" @click="markNoShow(apt)"
                                                    title="No Show">
                                                <i class="bi bi-person-x"></i>
                                            </button>
                                            <button class="btn btn-danger" @click="openCancelModal(apt)"
                                                    title="Cancel">
                                                <i class="bi bi-x-circle"></i>
                                            </button>
                                        </div>
                                        <button v-else-if="apt.status === 'completed' && apt.treatment"
                                                class="btn btn-sm btn-outline-info"
                                                @click="viewTreatment(apt)">
                                            <i class="bi bi-file-medical"></i> View
                                        </button>
                                        <span v-else class="text-muted">-</span>
                                    </td>
                                </tr>
                                <tr v-if="appointments.length === 0">
                                    <td colspan="7" class="text-center text-muted py-4">
                                        No appointments found
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Complete Modal -->
            <div class="modal fade" :class="{'show d-block': showCompleteModal}" tabindex="-1"
                 v-if="showCompleteModal">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Complete Appointment</h5>
                            <button type="button" class="btn-close" @click="showCompleteModal = false"></button>
                        </div>
                        <div class="modal-body">
                            <div class="alert alert-info mb-3">
                                <strong>Patient:</strong> {{ selectedAppointment?.patient?.full_name }}<br>
                                <strong>Date:</strong> {{ formatDate(selectedAppointment?.appointment_date) }}
                                at {{ selectedAppointment?.appointment_time }}
                            </div>
                            <form>
                                <div class="mb-3">
                                    <label class="form-label">Diagnosis *</label>
                                    <textarea class="form-control" v-model="treatmentForm.diagnosis"
                                              rows="3" required></textarea>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Prescription</label>
                                    <textarea class="form-control" v-model="treatmentForm.prescription"
                                              rows="3" placeholder="One medication per line..."></textarea>
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Follow-up Date</label>
                                        <input type="date" class="form-control"
                                               v-model="treatmentForm.follow_up_date">
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Visit Type</label>
                                        <select class="form-select" v-model="treatmentForm.visit_type">
                                            <option value="in-person">In-Person</option>
                                            <option value="follow-up">Follow-up</option>
                                            <option value="emergency">Emergency</option>
                                            <option value="routine-checkup">Routine Checkup</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Tests Recommended</label>
                                    <textarea class="form-control" v-model="treatmentForm.tests_recommended"
                                              rows="2"></textarea>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Notes</label>
                                    <textarea class="form-control" v-model="treatmentForm.notes"
                                              rows="2"></textarea>
                                </div>
                            </form>
                            <div v-if="formError" class="alert alert-danger">{{ formError }}</div>
                        </div>
                        <div class="modal-footer">
                            <button class="btn btn-secondary" @click="showCompleteModal = false">Cancel</button>
                            <button class="btn btn-success" @click="completeAppointment"
                                    :disabled="saving || !treatmentForm.diagnosis">
                                <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
                                Complete
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-backdrop fade show" v-if="showCompleteModal"></div>

            <!-- Cancel Modal -->
            <div class="modal fade" :class="{'show d-block': showCancelModal}" tabindex="-1"
                 v-if="showCancelModal">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Cancel Appointment</h5>
                            <button type="button" class="btn-close" @click="showCancelModal = false"></button>
                        </div>
                        <div class="modal-body">
                            <p>Are you sure you want to cancel this appointment?</p>
                            <div class="mb-3">
                                <label class="form-label">Reason (optional)</label>
                                <textarea class="form-control" v-model="cancelReason" rows="2"></textarea>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button class="btn btn-secondary" @click="showCancelModal = false">Back</button>
                            <button class="btn btn-danger" @click="cancelAppointment" :disabled="saving">
                                <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
                                Cancel Appointment
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-backdrop fade show" v-if="showCancelModal"></div>

            <!-- Treatment View Modal -->
            <div class="modal fade" :class="{'show d-block': showTreatmentModal}" tabindex="-1"
                 v-if="showTreatmentModal">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Treatment Record</h5>
                            <button type="button" class="btn-close" @click="showTreatmentModal = false"></button>
                        </div>
                        <div class="modal-body" v-if="selectedTreatment">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <strong>Diagnosis:</strong>
                                    <p>{{ selectedTreatment.diagnosis }}</p>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <strong>Visit Type:</strong>
                                    <p>{{ selectedTreatment.visit_type }}</p>
                                </div>
                            </div>
                            <div class="mb-3" v-if="selectedTreatment.prescription">
                                <strong>Prescription:</strong>
                                <p class="mb-0" style="white-space: pre-line">{{ selectedTreatment.prescription }}</p>
                            </div>
                            <div class="mb-3" v-if="selectedTreatment.tests_recommended">
                                <strong>Tests Recommended:</strong>
                                <p class="mb-0">{{ selectedTreatment.tests_recommended }}</p>
                            </div>
                            <div class="mb-3" v-if="selectedTreatment.notes">
                                <strong>Notes:</strong>
                                <p class="mb-0">{{ selectedTreatment.notes }}</p>
                            </div>
                            <div v-if="selectedTreatment.follow_up_date">
                                <strong>Follow-up Date:</strong>
                                <p class="mb-0">{{ selectedTreatment.follow_up_date }}</p>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button class="btn btn-secondary" @click="showTreatmentModal = false">Close</button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-backdrop fade show" v-if="showTreatmentModal"></div>

            <!-- Toast -->
            <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 1100">
                <div class="toast align-items-center text-white border-0" :class="toastClass"
                     :class="{'show': showToast}">
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
            appointments: [],
            loading: true,
            saving: false,
            filters: { period: '', status: '', date: '' },
            showCompleteModal: false,
            showCancelModal: false,
            showTreatmentModal: false,
            selectedAppointment: null,
            selectedTreatment: null,
            treatmentForm: { diagnosis: '', prescription: '', notes: '', tests_recommended: '', follow_up_date: '', visit_type: 'in-person' },
            cancelReason: '',
            formError: null,
            showToast: false,
            toastMessage: '',
            toastClass: 'bg-success'
        };
    },

    async created() {
        await this.loadAppointments();
    },

    methods: {
        async loadAppointments() {
            this.loading = true;
            const response = await doctorService.getAppointments(this.filters);
            if (response.success) {
                this.appointments = response.appointments;
            }
            this.loading = false;
        },

        clearFilters() {
            this.filters = { period: '', status: '', date: '' };
            this.loadAppointments();
        },

        formatDate(dateStr) {
            if (!dateStr) return 'N/A';
            return new Date(dateStr).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
        },

        getStatusClass(status) {
            return { 'booked': 'bg-primary', 'completed': 'bg-success', 'cancelled': 'bg-danger', 'no_show': 'bg-warning' }[status] || 'bg-secondary';
        },

        getRowClass(apt) {
            if (apt.status === 'cancelled') return 'table-danger';
            if (apt.status === 'completed') return 'table-success';
            if (apt.is_today) return 'table-info';
            return '';
        },

        openCompleteModal(apt) {
            this.selectedAppointment = apt;
            this.treatmentForm = { diagnosis: '', prescription: '', notes: '', tests_recommended: '', follow_up_date: '', visit_type: 'in-person' };
            this.formError = null;
            this.showCompleteModal = true;
        },

        async completeAppointment() {
            if (!this.treatmentForm.diagnosis) { this.formError = 'Diagnosis is required'; return; }
            this.saving = true;
            const response = await doctorService.completeAppointment(this.selectedAppointment.id, this.treatmentForm);
            if (response.success) {
                this.showToastMessage('Appointment completed', 'bg-success');
                this.showCompleteModal = false;
                await this.loadAppointments();
            } else {
                this.formError = response.message;
            }
            this.saving = false;
        },

        openCancelModal(apt) {
            this.selectedAppointment = apt;
            this.cancelReason = '';
            this.showCancelModal = true;
        },

        async cancelAppointment() {
            this.saving = true;
            const response = await doctorService.cancelAppointment(this.selectedAppointment.id, this.cancelReason);
            if (response.success) {
                this.showToastMessage('Appointment cancelled', 'bg-success');
                this.showCancelModal = false;
                await this.loadAppointments();
            } else {
                this.showToastMessage(response.message, 'bg-danger');
            }
            this.saving = false;
        },

        async markNoShow(apt) {
            if (!confirm('Mark this appointment as no-show?')) return;
            const response = await doctorService.markNoShow(apt.id);
            if (response.success) {
                this.showToastMessage('Marked as no-show', 'bg-warning');
                await this.loadAppointments();
            }
        },

        viewTreatment(apt) {
            this.selectedTreatment = apt.treatment;
            this.showTreatmentModal = true;
        },

        showToastMessage(msg, cls) {
            this.toastMessage = msg;
            this.toastClass = cls;
            this.showToast = true;
            setTimeout(() => { this.showToast = false; }, 3000);
        }
    }
};

window.DoctorAppointments = DoctorAppointments;
