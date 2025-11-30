const PatientDashboard = {
    name: 'PatientDashboard',

    template: `
        <div class="container-fluid dashboard-container">
            <!-- Header -->
            <div class="row mb-4">
                <div class="col">
                    <h2>Welcome, {{ userName }}</h2>
                    <p class="text-muted">Patient Dashboard</p>
                </div>
                <div class="col-auto">
                    <router-link to="/patient/profile" class="btn btn-outline-primary me-2">
                        <i class="bi bi-person"></i> Edit Profile
                    </router-link>
                    <router-link to="/patient/history" class="btn btn-outline-secondary">
                        <i class="bi bi-clock-history"></i> History
                    </router-link>
                </div>
            </div>

            <!-- Loading -->
            <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>

            <div v-else>
                <!-- Stats Cards -->
                <div class="row g-4 mb-4">
                    <div class="col-md-4">
                        <div class="card bg-primary text-white h-100">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <h6 class="card-subtitle mb-1 text-white-50">Upcoming</h6>
                                        <h2 class="mb-0">{{ stats.upcoming_appointments }}</h2>
                                    </div>
                                    <i class="bi bi-calendar-check display-4 opacity-50"></i>
                                </div>
                            </div>
                            <div class="card-footer bg-transparent border-0">
                                <router-link to="/patient/appointments?period=upcoming" class="text-white text-decoration-none small">
                                    View All <i class="bi bi-arrow-right"></i>
                                </router-link>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card bg-success text-white h-100">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <h6 class="card-subtitle mb-1 text-white-50">Completed</h6>
                                        <h2 class="mb-0">{{ stats.completed_appointments }}</h2>
                                    </div>
                                    <i class="bi bi-check-circle display-4 opacity-50"></i>
                                </div>
                            </div>
                            <div class="card-footer bg-transparent border-0">
                                <router-link to="/patient/history" class="text-white text-decoration-none small">
                                    View History <i class="bi bi-arrow-right"></i>
                                </router-link>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card bg-info text-white h-100">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <h6 class="card-subtitle mb-1 text-white-50">Treatments</h6>
                                        <h2 class="mb-0">{{ stats.total_treatments }}</h2>
                                    </div>
                                    <i class="bi bi-file-medical display-4 opacity-50"></i>
                                </div>
                            </div>
                            <div class="card-footer bg-transparent border-0">
                                <router-link to="/patient/treatments" class="text-white text-decoration-none small">
                                    View Records <i class="bi bi-arrow-right"></i>
                                </router-link>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Today's Appointments -->
                <div class="card mb-4" v-if="stats.today_appointments && stats.today_appointments.length > 0">
                    <div class="card-header bg-warning text-dark">
                        <h5 class="mb-0"><i class="bi bi-bell"></i> Today's Appointments</h5>
                    </div>
                    <div class="card-body">
                        <div class="list-group list-group-flush">
                            <div v-for="apt in stats.today_appointments" :key="apt.id"
                                 class="list-group-item d-flex justify-content-between align-items-center">
                                <div>
                                    <strong>{{ apt.appointment_time }}</strong> -
                                    Dr. {{ apt.doctor ? apt.doctor.full_name : 'N/A' }}
                                    <span class="text-muted ms-2">({{ apt.department_name || 'General' }})</span>
                                </div>
                                <span class="badge bg-primary">{{ apt.status }}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Departments Section -->
                <div class="card mb-4">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0"><i class="bi bi-building"></i> Departments</h5>
                        <router-link to="/patient/doctors" class="btn btn-sm btn-outline-primary">
                            <i class="bi bi-search"></i> Search All Doctors
                        </router-link>
                    </div>
                    <div class="card-body">
                        <div class="row g-3">
                            <div class="col-md-4 col-lg-3" v-for="dept in departments" :key="dept.id">
                                <div class="card h-100 border-0 shadow-sm">
                                    <div class="card-body text-center">
                                        <i class="bi bi-hospital display-4 text-primary mb-2"></i>
                                        <h6>{{ dept.name }}</h6>
                                        <p class="text-muted small mb-2">{{ dept.doctor_count }} Doctor(s)</p>
                                        <router-link :to="'/patient/departments/' + dept.id"
                                                     class="btn btn-sm btn-outline-primary">
                                            View Doctors
                                        </router-link>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Upcoming Appointments -->
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0"><i class="bi bi-calendar-check"></i> Upcoming Appointments</h5>
                        <router-link to="/patient/departments" class="btn btn-primary btn-sm">
                            <i class="bi bi-plus"></i> Book Appointment
                        </router-link>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive" v-if="upcomingAppointments.length > 0">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>#</th>
                                        <th>Doctor</th>
                                        <th>Department</th>
                                        <th>Date</th>
                                        <th>Time</th>
                                        <th>Status</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="(apt, index) in upcomingAppointments" :key="apt.id">
                                        <td>{{ index + 1 }}</td>
                                        <td>Dr. {{ apt.doctor ? apt.doctor.full_name : 'N/A' }}</td>
                                        <td>{{ apt.department_name || 'N/A' }}</td>
                                        <td>{{ formatDate(apt.appointment_date) }}</td>
                                        <td>{{ apt.appointment_time }}</td>
                                        <td>
                                            <span class="badge" :class="getStatusBadge(apt.status)">
                                                {{ apt.status }}
                                            </span>
                                        </td>
                                        <td>
                                            <button class="btn btn-sm btn-outline-warning me-1"
                                                    @click="openRescheduleModal(apt)"
                                                    title="Reschedule">
                                                <i class="bi bi-calendar"></i>
                                            </button>
                                            <button class="btn btn-sm btn-outline-danger"
                                                    @click="cancelAppointment(apt)"
                                                    title="Cancel">
                                                <i class="bi bi-x-circle"></i>
                                            </button>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <div v-else class="text-center py-4">
                            <i class="bi bi-calendar-x display-4 text-muted"></i>
                            <p class="text-muted mb-3">No upcoming appointments</p>
                            <router-link to="/patient/departments" class="btn btn-primary">
                                Book Your First Appointment
                            </router-link>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Reschedule Modal -->
            <div class="modal fade" id="rescheduleModal" tabindex="-1" ref="rescheduleModal">
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
                                       :min="minDate" @change="loadAvailableSlots">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Available Slots</label>
                                <select class="form-select" v-model="rescheduleForm.time" :disabled="!availableSlots.length">
                                    <option value="">Select a time slot</option>
                                    <option v-for="slot in availableSlots" :key="slot" :value="slot">
                                        {{ slot }}
                                    </option>
                                </select>
                                <small v-if="loadingSlots" class="text-muted">Loading slots...</small>
                                <small v-else-if="rescheduleForm.date && !availableSlots.length" class="text-danger">
                                    No slots available on this date
                                </small>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" @click="confirmReschedule"
                                    :disabled="!rescheduleForm.date || !rescheduleForm.time">
                                Reschedule
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,

    data() {
        return {
            loading: true,
            stats: {
                upcoming_appointments: 0,
                completed_appointments: 0,
                total_treatments: 0,
                today_appointments: []
            },
            departments: [],
            upcomingAppointments: [],
            rescheduleForm: {
                appointmentId: null,
                doctorId: null,
                date: '',
                time: ''
            },
            availableSlots: [],
            loadingSlots: false,
            rescheduleModalInstance: null
        };
    },

    computed: {
        userName() {
            const user = authService.getUser();
            if (user && user.profile) {
                return user.profile.full_name || user.username;
            }
            return user ? user.username : '';
        },
        minDate() {
            return new Date().toISOString().split('T')[0];
        }
    },

    async created() {
        await this.loadDashboard();
    },

    mounted() {
        const modalEl = document.getElementById('rescheduleModal');
        if (modalEl) {
            this.rescheduleModalInstance = new bootstrap.Modal(modalEl);
        }
    },

    methods: {
        async loadDashboard() {
            this.loading = true;
            try {
                // Load stats and departments in parallel
                const [statsRes, deptsRes, aptsRes] = await Promise.all([
                    patientService.getDashboardStats(),
                    patientService.getDepartments(),
                    patientService.getAppointments({ period: 'upcoming' })
                ]);

                if (statsRes.success) {
                    this.stats = statsRes.stats;
                }
                if (deptsRes.success) {
                    this.departments = deptsRes.departments;
                }
                if (aptsRes.success) {
                    this.upcomingAppointments = aptsRes.appointments;
                }
            } catch (error) {
                console.error('Failed to load dashboard:', error);
            }
            this.loading = false;
        },

        formatDate(dateStr) {
            if (!dateStr) return '';
            const date = new Date(dateStr);
            return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
        },

        getStatusBadge(status) {
            const badges = {
                'booked': 'bg-primary',
                'completed': 'bg-success',
                'cancelled': 'bg-danger',
                'no_show': 'bg-warning'
            };
            return badges[status] || 'bg-secondary';
        },

        openRescheduleModal(appointment) {
            this.rescheduleForm = {
                appointmentId: appointment.id,
                doctorId: appointment.doctor_id,
                date: '',
                time: ''
            };
            this.availableSlots = [];
            this.rescheduleModalInstance.show();
        },

        async loadAvailableSlots() {
            if (!this.rescheduleForm.date || !this.rescheduleForm.doctorId) return;

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
            if (!this.rescheduleForm.date || !this.rescheduleForm.time) return;

            const response = await patientService.rescheduleAppointment(
                this.rescheduleForm.appointmentId,
                this.rescheduleForm.date,
                this.rescheduleForm.time
            );

            if (response.success) {
                this.rescheduleModalInstance.hide();
                await this.loadDashboard();
                alert('Appointment rescheduled successfully!');
            } else {
                alert(response.message || 'Failed to reschedule appointment');
            }
        },

        async cancelAppointment(appointment) {
            if (!confirm('Are you sure you want to cancel this appointment?')) return;

            const response = await patientService.cancelAppointment(appointment.id);
            if (response.success) {
                await this.loadDashboard();
                alert('Appointment cancelled successfully');
            } else {
                alert(response.message || 'Failed to cancel appointment');
            }
        }
    }
};

// Make component available globally
window.PatientDashboard = PatientDashboard;
