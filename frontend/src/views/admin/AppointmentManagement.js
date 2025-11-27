/**
 * Appointment Management View Component
 * Admin interface for viewing and managing all appointments.
 */

const AppointmentManagement = {
    name: 'AppointmentManagement',

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
                            <li class="breadcrumb-item active">Appointments</li>
                        </ol>
                    </nav>
                    <h2><i class="bi bi-calendar3"></i> Appointment Management</h2>
                </div>
            </div>

            <!-- Filters -->
            <div class="card mb-4">
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-2">
                            <label class="form-label">Status</label>
                            <select class="form-select" v-model="filters.status" @change="loadAppointments">
                                <option value="">All Status</option>
                                <option value="booked">Booked</option>
                                <option value="completed">Completed</option>
                                <option value="cancelled">Cancelled</option>
                            </select>
                        </div>
                        <div class="col-md-2">
                            <label class="form-label">From Date</label>
                            <input type="date" class="form-control" v-model="filters.date_from"
                                   @change="loadAppointments">
                        </div>
                        <div class="col-md-2">
                            <label class="form-label">To Date</label>
                            <input type="date" class="form-control" v-model="filters.date_to"
                                   @change="loadAppointments">
                        </div>
                        <div class="col-md-3">
                            <label class="form-label">Doctor</label>
                            <select class="form-select" v-model="filters.doctor_id" @change="loadAppointments">
                                <option value="">All Doctors</option>
                                <option v-for="doctor in doctors" :key="doctor.id" :value="doctor.id">
                                    {{ doctor.full_name }}
                                </option>
                            </select>
                        </div>
                        <div class="col-md-3 d-flex align-items-end">
                            <button class="btn btn-outline-secondary me-2" @click="clearFilters">
                                <i class="bi bi-x-circle"></i> Clear
                            </button>
                            <button class="btn btn-outline-primary" @click="showUpcoming">
                                <i class="bi bi-calendar-check"></i> Upcoming Only
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Quick Stats -->
            <div class="row g-3 mb-4">
                <div class="col-md-3">
                    <div class="card border-primary">
                        <div class="card-body py-2 text-center">
                            <h5 class="text-primary mb-0">{{ stats.booked }}</h5>
                            <small class="text-muted">Booked</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card border-success">
                        <div class="card-body py-2 text-center">
                            <h5 class="text-success mb-0">{{ stats.completed }}</h5>
                            <small class="text-muted">Completed</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card border-danger">
                        <div class="card-body py-2 text-center">
                            <h5 class="text-danger mb-0">{{ stats.cancelled }}</h5>
                            <small class="text-muted">Cancelled</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card border-secondary">
                        <div class="card-body py-2 text-center">
                            <h5 class="mb-0">{{ appointments.length }}</h5>
                            <small class="text-muted">Total Shown</small>
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
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Date & Time</th>
                                    <th>Patient</th>
                                    <th>Doctor</th>
                                    <th>Department</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="apt in appointments" :key="apt.id"
                                    :class="getRowClass(apt)">
                                    <td>#{{ apt.id }}</td>
                                    <td>
                                        <div>{{ formatDate(apt.appointment_date) }}</div>
                                        <small class="text-muted">{{ apt.appointment_time }}</small>
                                    </td>
                                    <td>
                                        <strong>{{ apt.patient?.full_name || 'N/A' }}</strong>
                                        <br>
                                        <small class="text-muted">{{ apt.patient?.phone || '' }}</small>
                                    </td>
                                    <td>Dr. {{ apt.doctor?.full_name || 'N/A' }}</td>
                                    <td>{{ apt.department_name || apt.doctor?.department || 'N/A' }}</td>
                                    <td>
                                        <span class="badge" :class="getStatusClass(apt.status)">
                                            {{ apt.status.charAt(0).toUpperCase() + apt.status.slice(1) }}
                                        </span>
                                        <span v-if="apt.is_today" class="badge bg-info ms-1">Today</span>
                                    </td>
                                    <td>
                                        <div class="btn-group btn-group-sm">
                                            <button class="btn btn-outline-info" @click="viewAppointment(apt)"
                                                    title="View Details">
                                                <i class="bi bi-eye"></i>
                                            </button>
                                            <button v-if="apt.status === 'booked'"
                                                    class="btn btn-outline-danger"
                                                    @click="cancelAppointment(apt)"
                                                    title="Cancel">
                                                <i class="bi bi-x-circle"></i>
                                            </button>
                                        </div>
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

            <!-- View Appointment Modal -->
            <div class="modal fade" :class="{'show d-block': showViewModal}" tabindex="-1" v-if="showViewModal">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Appointment Details #{{ selectedAppointment?.id }}</h5>
                            <button type="button" class="btn-close" @click="showViewModal = false"></button>
                        </div>
                        <div class="modal-body" v-if="selectedAppointment">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6 class="text-muted">Appointment Info</h6>
                                    <table class="table table-sm">
                                        <tr>
                                            <th>Date:</th>
                                            <td>{{ formatDate(selectedAppointment.appointment_date) }}</td>
                                        </tr>
                                        <tr>
                                            <th>Time:</th>
                                            <td>{{ selectedAppointment.appointment_time }} - {{ selectedAppointment.end_time }}</td>
                                        </tr>
                                        <tr>
                                            <th>Duration:</th>
                                            <td>{{ selectedAppointment.duration }} minutes</td>
                                        </tr>
                                        <tr>
                                            <th>Status:</th>
                                            <td>
                                                <span class="badge" :class="getStatusClass(selectedAppointment.status)">
                                                    {{ selectedAppointment.status }}
                                                </span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <th>Reason:</th>
                                            <td>{{ selectedAppointment.reason || 'Not specified' }}</td>
                                        </tr>
                                    </table>
                                </div>
                                <div class="col-md-6">
                                    <h6 class="text-muted">Patient & Doctor</h6>
                                    <table class="table table-sm">
                                        <tr>
                                            <th>Patient:</th>
                                            <td>{{ selectedAppointment.patient?.full_name }}</td>
                                        </tr>
                                        <tr>
                                            <th>Patient Phone:</th>
                                            <td>{{ selectedAppointment.patient?.phone }}</td>
                                        </tr>
                                        <tr>
                                            <th>Doctor:</th>
                                            <td>Dr. {{ selectedAppointment.doctor?.full_name }}</td>
                                        </tr>
                                        <tr>
                                            <th>Department:</th>
                                            <td>{{ selectedAppointment.department_name }}</td>
                                        </tr>
                                    </table>
                                </div>
                            </div>

                            <!-- Cancellation Info -->
                            <div v-if="selectedAppointment.status === 'cancelled'" class="alert alert-danger mt-3">
                                <strong>Cancelled:</strong>
                                {{ formatDate(selectedAppointment.cancelled_at) }}
                                by {{ selectedAppointment.cancelled_by }}
                                <br v-if="selectedAppointment.cancellation_reason">
                                <em>{{ selectedAppointment.cancellation_reason }}</em>
                            </div>

                            <!-- Treatment Info -->
                            <div v-if="selectedAppointment.treatment" class="mt-3">
                                <h6 class="text-muted">Treatment Record</h6>
                                <div class="card">
                                    <div class="card-body">
                                        <p><strong>Diagnosis:</strong> {{ selectedAppointment.treatment.diagnosis }}</p>
                                        <p><strong>Prescription:</strong> {{ selectedAppointment.treatment.prescription }}</p>
                                        <p v-if="selectedAppointment.treatment.notes">
                                            <strong>Notes:</strong> {{ selectedAppointment.treatment.notes }}
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <!-- Notes -->
                            <div v-if="selectedAppointment.notes" class="mt-3">
                                <h6 class="text-muted">Notes</h6>
                                <p>{{ selectedAppointment.notes }}</p>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" @click="showViewModal = false">
                                Close
                            </button>
                            <button v-if="selectedAppointment?.status === 'booked'"
                                    type="button" class="btn btn-danger"
                                    @click="cancelAppointment(selectedAppointment); showViewModal = false">
                                Cancel Appointment
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-backdrop fade show" v-if="showViewModal"></div>

            <!-- Cancel Confirmation Modal -->
            <div class="modal fade" :class="{'show d-block': showCancelModal}" tabindex="-1" v-if="showCancelModal">
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
                                <textarea class="form-control" v-model="cancelReason" rows="2"
                                          placeholder="Enter cancellation reason..."></textarea>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" @click="showCancelModal = false">
                                Back
                            </button>
                            <button type="button" class="btn btn-danger" @click="confirmCancel" :disabled="saving">
                                <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
                                Cancel Appointment
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-backdrop fade show" v-if="showCancelModal"></div>

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
            appointments: [],
            doctors: [],
            loading: true,
            saving: false,
            filters: {
                status: '',
                date_from: '',
                date_to: '',
                doctor_id: '',
                upcoming: false
            },
            stats: {
                booked: 0,
                completed: 0,
                cancelled: 0
            },
            showViewModal: false,
            showCancelModal: false,
            selectedAppointment: null,
            cancelReason: '',
            showToast: false,
            toastMessage: '',
            toastClass: 'bg-success'
        };
    },

    async created() {
        await Promise.all([
            this.loadDoctors(),
            this.loadAppointments()
        ]);
    },

    methods: {
        async loadDoctors() {
            const response = await adminService.getDoctors();
            if (response.success) {
                this.doctors = response.doctors;
            }
        },

        async loadAppointments() {
            this.loading = true;
            const response = await adminService.getAppointments(this.filters);

            if (response.success) {
                this.appointments = response.appointments;
                this.calculateStats();
            }
            this.loading = false;
        },

        calculateStats() {
            this.stats = {
                booked: this.appointments.filter(a => a.status === 'booked').length,
                completed: this.appointments.filter(a => a.status === 'completed').length,
                cancelled: this.appointments.filter(a => a.status === 'cancelled').length
            };
        },

        clearFilters() {
            this.filters = {
                status: '',
                date_from: '',
                date_to: '',
                doctor_id: '',
                upcoming: false
            };
            this.loadAppointments();
        },

        showUpcoming() {
            this.filters.upcoming = true;
            this.filters.status = '';
            this.loadAppointments();
        },

        formatDate(dateStr) {
            if (!dateStr) return 'N/A';
            const date = new Date(dateStr);
            return date.toLocaleDateString('en-US', {
                weekday: 'short',
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        },

        getStatusClass(status) {
            const classes = {
                'booked': 'bg-primary',
                'completed': 'bg-success',
                'cancelled': 'bg-danger',
                'no_show': 'bg-warning'
            };
            return classes[status] || 'bg-secondary';
        },

        getRowClass(apt) {
            if (apt.status === 'cancelled') return 'table-danger';
            if (apt.status === 'completed') return 'table-success';
            if (apt.is_today) return 'table-info';
            return '';
        },

        async viewAppointment(apt) {
            // Load full appointment details
            const response = await adminService.getAppointment(apt.id);
            if (response.success) {
                this.selectedAppointment = response.appointment;
                this.showViewModal = true;
            }
        },

        cancelAppointment(apt) {
            this.selectedAppointment = apt;
            this.cancelReason = '';
            this.showCancelModal = true;
        },

        async confirmCancel() {
            this.saving = true;
            const response = await adminService.cancelAppointment(
                this.selectedAppointment.id,
                this.cancelReason
            );

            if (response.success) {
                this.showToastMessage('Appointment cancelled successfully', 'bg-success');
                this.showCancelModal = false;
                await this.loadAppointments();
            } else {
                this.showToastMessage(response.message || 'Failed to cancel', 'bg-danger');
            }
            this.saving = false;
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
window.AppointmentManagement = AppointmentManagement;
