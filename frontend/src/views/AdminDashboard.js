const AdminDashboard = {
    name: 'AdminDashboard',

    template: `
        <div class="container-fluid dashboard-container">
            <!-- Header -->
            <div class="row mb-4">
                <div class="col">
                    <h2>Welcome, Admin</h2>
                    <p class="text-muted">Hospital Management System Dashboard</p>
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
                                    <i class="bi bi-person-badge"></i>
                                </div>
                                <div>
                                    <div class="stat-value">{{ stats.total_doctors }}</div>
                                    <div class="stat-label">Total Doctors</div>
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
                                    <i class="bi bi-calendar-plus"></i>
                                </div>
                                <div>
                                    <div class="stat-value">{{ stats.new_patients_this_week }}</div>
                                    <div class="stat-label">New Patients (7 days)</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Appointment Status Cards -->
                <div class="row g-4 mb-4">
                    <div class="col-md-4">
                        <div class="card border-primary h-100">
                            <div class="card-body text-center">
                                <h3 class="text-primary">{{ stats.appointments_by_status?.booked || 0 }}</h3>
                                <p class="text-muted mb-0">Booked Appointments</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card border-success h-100">
                            <div class="card-body text-center">
                                <h3 class="text-success">{{ stats.appointments_by_status?.completed || 0 }}</h3>
                                <p class="text-muted mb-0">Completed</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card border-danger h-100">
                            <div class="card-body text-center">
                                <h3 class="text-danger">{{ stats.appointments_by_status?.cancelled || 0 }}</h3>
                                <p class="text-muted mb-0">Cancelled</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Main Content Row -->
                <div class="row g-4">
                    <!-- Quick Actions -->
                    <div class="col-md-4">
                        <div class="card h-100">
                            <div class="card-header">
                                <h5 class="mb-0"><i class="bi bi-lightning"></i> Quick Actions</h5>
                            </div>
                            <div class="card-body">
                                <div class="d-grid gap-2">
                                    <router-link to="/admin/doctors" class="btn btn-outline-primary">
                                        <i class="bi bi-person-plus"></i> Manage Doctors
                                    </router-link>
                                    <router-link to="/admin/patients" class="btn btn-outline-success">
                                        <i class="bi bi-people"></i> Manage Patients
                                    </router-link>
                                    <router-link to="/admin/appointments" class="btn btn-outline-warning">
                                        <i class="bi bi-calendar3"></i> View Appointments
                                    </router-link>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Departments Overview -->
                    <div class="col-md-8">
                        <div class="card h-100">
                            <div class="card-header">
                                <h5 class="mb-0"><i class="bi bi-building"></i> Departments Overview</h5>
                            </div>
                            <div class="card-body">
                                <div class="table-responsive">
                                    <table class="table table-hover mb-0">
                                        <thead>
                                            <tr>
                                                <th>Department</th>
                                                <th class="text-center">Doctors</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr v-for="dept in stats.departments" :key="dept.id">
                                                <td>{{ dept.name }}</td>
                                                <td class="text-center">
                                                    <span class="badge bg-primary">{{ dept.doctors_count }}</span>
                                                </td>
                                            </tr>
                                            <tr v-if="!stats.departments || stats.departments.length === 0">
                                                <td colspan="2" class="text-center text-muted">
                                                    No departments found
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </template>

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
            stats: {
                total_doctors: 0,
                total_patients: 0,
                total_appointments: 0,
                today_appointments: 0,
                new_patients_this_week: 0,
                appointments_by_status: {
                    booked: 0,
                    completed: 0,
                    cancelled: 0
                },
                departments: []
            }
        };
    },

    async created() {
        await this.loadDashboardStats();
    },

    methods: {
        async loadDashboardStats() {
            this.loading = true;
            this.error = null;

            try {
                const response = await adminService.getDashboardStats();

                if (response.success) {
                    this.stats = response.stats;
                } else {
                    this.error = response.message || 'Failed to load dashboard statistics';
                }
            } catch (err) {
                this.error = 'An error occurred while loading dashboard data';
                console.error('Dashboard error:', err);
            } finally {
                this.loading = false;
            }
        }
    }
};

// Make component available globally
window.AdminDashboard = AdminDashboard;
