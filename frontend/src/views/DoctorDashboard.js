const DoctorDashboard = {
    name: 'DoctorDashboard',

    template: `
        <div class="container-fluid dashboard-container">
            <!-- Header -->
            <div class="row mb-4">
                <div class="col">
                    <h2>Welcome, Dr. {{ doctorName }}</h2>
                    <p class="text-muted">{{ departmentName }} Department</p>
                </div>
                <div class="col-auto">
                    <router-link to="/doctor/availability" class="btn btn-outline-primary">
                        <i class="bi bi-clock"></i> Update Availability
                    </router-link>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>

            <template v-else>
                <!-- Stats Cards -->
                <div class="row g-4 mb-4">
                    <div class="col-md-3">
                        <div class="card stat-card h-100">
                            <div class="card-body d-flex align-items-center">
                                <div class="stat-icon bg-primary-soft me-3">
                                    <i class="bi bi-calendar-check"></i>
                                </div>
                                <div>
                                    <div class="stat-value">{{ stats.today_appointments }}</div>
                                    <div class="stat-label">Today's Appointments</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stat-card h-100">
                            <div class="card-body d-flex align-items-center">
                                <div class="stat-icon bg-info-soft me-3">
                                    <i class="bi bi-calendar-week"></i>
                                </div>
                                <div>
                                    <div class="stat-value">{{ stats.week_appointments }}</div>
                                    <div class="stat-label">This Week</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stat-card h-100">
                            <div class="card-body d-flex align-items-center">
                                <div class="stat-icon bg-success-soft me-3">
                                    <i class="bi bi-people"></i>
                                </div>
                                <div>
                                    <div class="stat-value">{{ stats.total_patients }}</div>
                                    <div class="stat-label">Total Patients</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stat-card h-100">
                            <div class="card-body d-flex align-items-center">
                                <div class="stat-icon bg-warning-soft me-3">
                                    <i class="bi bi-hourglass-split"></i>
                                </div>
                                <div>
                                    <div class="stat-value">{{ stats.pending_appointments }}</div>
                                    <div class="stat-label">Pending</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Main Content Row -->
                <div class="row g-4">
                    <!-- Today's Schedule -->
                    <div class="col-md-8">
                        <div class="card h-100">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <h5 class="mb-0"><i class="bi bi-calendar-day"></i> Today's Schedule</h5>
                                <router-link to="/doctor/appointments" class="btn btn-sm btn-outline-primary">
                                    View All
                                </router-link>
                            </div>
                            <div class="card-body">
                                <div class="table-responsive" v-if="todayAppointments.length > 0">
                                    <table class="table table-hover mb-0">
                                        <thead>
                                            <tr>
                                                <th>Time</th>
                                                <th>Patient</th>
                                                <th>Status</th>
                                                <th>Action</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr v-for="apt in todayAppointments" :key="apt.id">
                                                <td>
                                                    <strong>{{ apt.appointment_time }}</strong>
                                                </td>
                                                <td>
                                                    {{ apt.patient && apt.patient.full_name ? apt.patient.full_name : 'N/A' }}
                                                    <br>
                                                    <small class="text-muted">{{ apt.patient ? apt.patient.phone : '' }}</small>
                                                </td>
                                                <td>
                                                    <span class="badge" :class="getStatusClass(apt.status)">
                                                        {{ apt.status }}
                                                    </span>
                                                </td>
                                                <td>
                                                    <button v-if="apt.status === 'booked'"
                                                            class="btn btn-sm btn-success"
                                                            @click="openCompleteModal(apt)">
                                                        <i class="bi bi-check-circle"></i> Complete
                                                    </button>
                                                    <span v-else class="text-muted">-</span>
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                                <div v-else class="text-center text-muted py-4">
                                    <i class="bi bi-calendar-x display-4"></i>
                                    <p class="mt-2">No appointments scheduled for today</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Quick Actions -->
                    <div class="col-md-4">
                        <div class="card h-100">
                            <div class="card-header">
                                <h5 class="mb-0"><i class="bi bi-lightning"></i> Quick Actions</h5>
                            </div>
                            <div class="card-body">
                                <div class="d-grid gap-2">
                                    <router-link to="/doctor/appointments" class="btn btn-outline-primary">
                                        <i class="bi bi-calendar3"></i> View Appointments
                                    </router-link>
                                    <router-link to="/doctor/patients" class="btn btn-outline-success">
                                        <i class="bi bi-people"></i> My Patients
                                    </router-link>
                                    <router-link to="/doctor/availability" class="btn btn-outline-warning">
                                        <i class="bi bi-clock"></i> Update Availability
                                    </router-link>
                                    <router-link to="/doctor/charts" class="btn btn-outline-info">
                                        <i class="bi bi-bar-chart"></i> My Analytics
                                    </router-link>
                                    <router-link to="/doctor/profile" class="btn btn-outline-secondary">
                                        <i class="bi bi-person"></i> Edit Profile
                                    </router-link>
                                </div>
                            </div>
                        </div>

                        <!-- Stats Summary -->
                        <div class="card mt-4">
                            <div class="card-header">
                                <h5 class="mb-0"><i class="bi bi-bar-chart"></i> Performance</h5>
                            </div>
                            <div class="card-body">
                                <div class="d-flex justify-content-between mb-2">
                                    <span>Completed</span>
                                    <strong class="text-success">{{ stats.completed_appointments }}</strong>
                                </div>
                                <div class="d-flex justify-content-between">
                                    <span>Pending</span>
                                    <strong class="text-warning">{{ stats.pending_appointments }}</strong>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </template>

            <!-- Complete Appointment Modal -->
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
                                <strong>Patient:</strong> {{ selectedAppointment && selectedAppointment.patient ? selectedAppointment.patient.full_name : '' }}
                                <br>
                                <strong>Time:</strong> {{ selectedAppointment ? selectedAppointment.appointment_time : '' }}
                            </div>
                            <form @submit.prevent="completeAppointment">
                                <div class="mb-3">
                                    <label class="form-label">Diagnosis *</label>
                                    <textarea class="form-control" v-model="treatmentForm.diagnosis"
                                              rows="3" required placeholder="Enter diagnosis..."></textarea>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Prescription</label>
                                    <textarea class="form-control" v-model="treatmentForm.prescription"
                                              rows="3" placeholder="Enter prescriptions (one per line)..."></textarea>
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
                                    <label class="form-label">Notes</label>
                                    <textarea class="form-control" v-model="treatmentForm.notes"
                                              rows="2" placeholder="Additional notes..."></textarea>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Tests Recommended</label>
                                    <textarea class="form-control" v-model="treatmentForm.tests_recommended"
                                              rows="2" placeholder="Recommended tests (one per line)..."></textarea>
                                </div>
                            </form>
                            <div v-if="formError" class="alert alert-danger">{{ formError }}</div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" @click="showCompleteModal = false">
                                Cancel
                            </button>
                            <button type="button" class="btn btn-success" @click="completeAppointment"
                                    :disabled="saving || !treatmentForm.diagnosis">
                                <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
                                Complete Appointment
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-backdrop fade show" v-if="showCompleteModal"></div>

            <!-- Error Message -->
            <div v-if="error" class="alert alert-danger mt-4">
                <i class="bi bi-exclamation-triangle"></i> {{ error }}
            </div>
        </div>
    `,

    data() {
        return {
            loading: true,
            error: null,
            saving: false,
            doctorName: '',
            departmentName: '',
            stats: {
                today_appointments: 0,
                week_appointments: 0,
                total_patients: 0,
                pending_appointments: 0,
                completed_appointments: 0
            },
            todayAppointments: [],
            showCompleteModal: false,
            selectedAppointment: null,
            treatmentForm: {
                diagnosis: '',
                prescription: '',
                notes: '',
                tests_recommended: '',
                follow_up_date: '',
                visit_type: 'in-person'
            },
            formError: null
        };
    },

    async created() {
        await this.loadDashboardData();
    },

    methods: {
        async loadDashboardData() {
            this.loading = true;
            this.error = null;

            try {
                const response = await doctorService.getDashboardStats();

                if (response.success) {
                    this.stats = response.stats;
                    this.todayAppointments = response.stats.today_appointments_list || [];
                    this.doctorName = (response.doctor && response.doctor.full_name) ? response.doctor.full_name : 'Doctor';
                    this.departmentName = (response.doctor && response.doctor.department) ? response.doctor.department : '';
                } else {
                    this.error = response.message || 'Failed to load dashboard data';
                }
            } catch (err) {
                this.error = 'An error occurred while loading dashboard';
                console.error('Dashboard error:', err);
            } finally {
                this.loading = false;
            }
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

        openCompleteModal(appointment) {
            this.selectedAppointment = appointment;
            this.treatmentForm = {
                diagnosis: '',
                prescription: '',
                notes: '',
                tests_recommended: '',
                follow_up_date: '',
                visit_type: 'in-person'
            };
            this.formError = null;
            this.showCompleteModal = true;
        },

        async completeAppointment() {
            if (!this.treatmentForm.diagnosis) {
                this.formError = 'Diagnosis is required';
                return;
            }

            this.saving = true;
            this.formError = null;

            try {
                const response = await doctorService.completeAppointment(
                    this.selectedAppointment.id,
                    this.treatmentForm
                );

                if (response.success) {
                    this.showCompleteModal = false;
                    await this.loadDashboardData();
                } else {
                    this.formError = response.message || 'Failed to complete appointment';
                }
            } catch (err) {
                this.formError = 'An error occurred';
            } finally {
                this.saving = false;
            }
        }
    }
};

// Make component available globally
window.DoctorDashboard = DoctorDashboard;
