/**
 * Patient Appointments View Component 
 * Shows all appointments with filtering and management options.
 */

const PatientAppointments = {
    name: 'PatientAppointments',

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
                            <li class="breadcrumb-item active">My Appointments</li>
                        </ol>
                    </nav>
                    <h2><i class="bi bi-calendar-check"></i> My Appointments</h2>
                </div>
                <div class="col-auto">
                    <router-link to="/patient/departments" class="btn btn-primary">
                        <i class="bi bi-plus"></i> Book New
                    </router-link>
                </div>
            </div>

            <!-- Filters -->
            <div class="card mb-4">
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-4">
                            <select class="form-select" v-model="filter.period" @change="loadAppointments">
                                <option value="">All Appointments</option>
                                <option value="upcoming">Upcoming</option>
                                <option value="today">Today</option>
                                <option value="past">Past</option>
                            </select>
                        </div>
                        <div class="col-md-4">
                            <select class="form-select" v-model="filter.status" @change="loadAppointments">
                                <option value="">All Status</option>
                                <option value="booked">Booked</option>
                                <option value="completed">Completed</option>
                                <option value="cancelled">Cancelled</option>
                                <option value="no_show">No Show</option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Loading -->
            <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>

            <!-- Appointments List -->
            <div v-else>
                <div class="card">
                    <div class="table-responsive" v-if="appointments.length > 0">
                        <table class="table table-hover mb-0">
                            <thead>
                                <tr>
                                    <th>Date & Time</th>
                                    <th>Doctor</th>
                                    <th>Department</th>
                                    <th>Reason</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="apt in appointments" :key="apt.id">
                                    <td>
                                        <strong>{{ formatDate(apt.appointment_date) }}</strong><br>
                                        <small class="text-muted">{{ apt.appointment_time }}</small>
                                    </td>
                                    <td>
                                        Dr. {{ apt.doctor ? apt.doctor.full_name : 'N/A' }}
                                    </td>
                                    <td>{{ apt.department_name || 'General' }}</td>
                                    <td>
                                        <span class="text-truncate d-inline-block" style="max-width: 150px;"
                                              :title="apt.reason">
                                            {{ apt.reason || '-' }}
                                        </span>
                                    </td>
                                    <td>
                                        <span class="badge" :class="getStatusBadge(apt.status)">
                                            {{ apt.status }}
                                        </span>
                                    </td>
                                    <td>
                                        <div class="btn-group btn-group-sm">
                                            <button v-if="apt.status === 'booked'" class="btn btn-outline-warning"
                                                    @click="openReschedule(apt)" title="Reschedule">
                                                <i class="bi bi-calendar"></i>
                                            </button>
                                            <button v-if="apt.status === 'booked'" class="btn btn-outline-danger"
                                                    @click="cancelAppointment(apt)" title="Cancel">
                                                <i class="bi bi-x-circle"></i>
                                            </button>
                                            <button v-if="apt.treatment" class="btn btn-outline-info"
                                                    @click="viewTreatment(apt)" title="View Treatment">
                                                <i class="bi bi-file-medical"></i>
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <div v-else class="card-body text-center py-5">
                        <i class="bi bi-calendar-x display-1 text-muted"></i>
                        <p class="text-muted mt-3">No appointments found</p>
                        <router-link to="/patient/departments" class="btn btn-primary">
                            Book Your First Appointment
                        </router-link>
                    </div>
                </div>
            </div>

            <!-- Reschedule Modal -->
            <div class="modal fade" id="rescheduleModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Reschedule Appointment</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label">New Date</label>
                                <input type="date" class="form-control" v-model="rescheduleForm.date"
                                       :min="minDate" @change="loadSlots">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Available Slots</label>
                                <div v-if="loadingSlots" class="text-center">
                                    <div class="spinner-border spinner-border-sm"></div>
                                </div>
                                <select v-else class="form-select" v-model="rescheduleForm.time"
                                        :disabled="!availableSlots.length">
                                    <option value="">Select time</option>
                                    <option v-for="slot in availableSlots" :key="slot" :value="slot">
                                        {{ slot }}
                                    </option>
                                </select>
                                <small v-if="rescheduleForm.date && !availableSlots.length && !loadingSlots"
                                       class="text-danger">
                                    No slots available
                                </small>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" @click="confirmReschedule"
                                    :disabled="!rescheduleForm.date || !rescheduleForm.time">
                                Confirm
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Treatment Modal -->
            <div class="modal fade" id="treatmentModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Treatment Details</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body" v-if="selectedTreatment">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label text-muted">Diagnosis</label>
                                    <p class="fw-bold">{{ selectedTreatment.diagnosis || 'N/A' }}</p>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label text-muted">Visit Type</label>
                                    <p>{{ selectedTreatment.visit_type || 'In-person' }}</p>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label text-muted">Prescription</label>
                                <pre class="bg-light p-3 rounded">{{ selectedTreatment.prescription || 'N/A' }}</pre>
                            </div>
                            <div class="mb-3">
                                <label class="form-label text-muted">Tests Recommended</label>
                                <p>{{ selectedTreatment.tests_recommended || 'None' }}</p>
                            </div>
                            <div class="mb-3">
                                <label class="form-label text-muted">Doctor's Notes</label>
                                <p>{{ selectedTreatment.notes || 'No additional notes' }}</p>
                            </div>
                            <div v-if="selectedTreatment.follow_up_date">
                                <label class="form-label text-muted">Follow-up Date</label>
                                <p class="text-primary">{{ formatDate(selectedTreatment.follow_up_date) }}</p>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,

    data() {
        return {
            appointments: [],
            filter: {
                period: '',
                status: ''
            },
            loading: true,
            rescheduleForm: {
                appointmentId: null,
                doctorId: null,
                date: '',
                time: ''
            },
            availableSlots: [],
            loadingSlots: false,
            selectedTreatment: null,
            rescheduleModalInstance: null,
            treatmentModalInstance: null
        };
    },

    computed: {
        minDate() {
            return new Date().toISOString().split('T')[0];
        }
    },

    async created() {
        // Check URL params for initial filter
        if (this.$route.query.period) {
            this.filter.period = this.$route.query.period;
        }
        await this.loadAppointments();
    },

    mounted() {
        this.rescheduleModalInstance = new bootstrap.Modal(document.getElementById('rescheduleModal'));
        this.treatmentModalInstance = new bootstrap.Modal(document.getElementById('treatmentModal'));
    },

    methods: {
        async loadAppointments() {
            this.loading = true;
            const response = await patientService.getAppointments({
                period: this.filter.period || undefined,
                status: this.filter.status || undefined
            });
            if (response.success) {
                this.appointments = response.appointments;
            }
            this.loading = false;
        },

        formatDate(dateStr) {
            if (!dateStr) return '';
            const date = new Date(dateStr);
            return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
        },

        getStatusBadge(status) {
            const badges = {
                'booked': 'bg-primary',
                'completed': 'bg-success',
                'cancelled': 'bg-danger',
                'no_show': 'bg-warning text-dark'
            };
            return badges[status] || 'bg-secondary';
        },

        openReschedule(appointment) {
            this.rescheduleForm = {
                appointmentId: appointment.id,
                doctorId: appointment.doctor_id,
                date: '',
                time: ''
            };
            this.availableSlots = [];
            this.rescheduleModalInstance.show();
        },

        async loadSlots() {
            if (!this.rescheduleForm.date) return;

            this.loadingSlots = true;
            this.availableSlots = [];

            const response = await patientService.getDoctorSlots(
                this.rescheduleForm.doctorId,
                this.rescheduleForm.date
            );

            if (response.success && response.available) {
                this.availableSlots = response.slots;
            }
            this.loadingSlots = false;
        },

        async confirmReschedule() {
            const response = await patientService.rescheduleAppointment(
                this.rescheduleForm.appointmentId,
                this.rescheduleForm.date,
                this.rescheduleForm.time
            );

            if (response.success) {
                this.rescheduleModalInstance.hide();
                await this.loadAppointments();
                alert('Appointment rescheduled successfully!');
            } else {
                alert(response.message || 'Failed to reschedule');
            }
        },

        async cancelAppointment(appointment) {
            if (!confirm('Are you sure you want to cancel this appointment?')) return;

            const response = await patientService.cancelAppointment(appointment.id);
            if (response.success) {
                await this.loadAppointments();
                alert('Appointment cancelled successfully');
            } else {
                alert(response.message || 'Failed to cancel');
            }
        },

        viewTreatment(appointment) {
            this.selectedTreatment = appointment.treatment;
            this.treatmentModalInstance.show();
        }
    }
};

window.PatientAppointments = PatientAppointments;
