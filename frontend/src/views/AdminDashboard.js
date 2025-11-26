/**
 * Admin Dashboard View Component
 * Displays admin-specific statistics and management options.
 */

const AdminDashboard = {
    name: 'AdminDashboard',

    template: `
        <div class="container-fluid dashboard-container">
            <div class="row mb-4">
                <div class="col">
                    <h2>Welcome, Admin</h2>
                    <p class="text-muted">Hospital Management System Dashboard</p>
                </div>
            </div>

            <!-- Stats Cards -->
            <div class="row g-4 mb-4">
                <div class="col-md-3">
                    <div class="card stat-card">
                        <div class="card-body d-flex align-items-center">
                            <div class="stat-icon bg-primary-soft me-3">
                                <i class="bi bi-person-badge"></i>
                            </div>
                            <div>
                                <div class="stat-value">{{ stats.doctors }}</div>
                                <div class="stat-label">Total Doctors</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card stat-card">
                        <div class="card-body d-flex align-items-center">
                            <div class="stat-icon bg-success-soft me-3">
                                <i class="bi bi-people"></i>
                            </div>
                            <div>
                                <div class="stat-value">{{ stats.patients }}</div>
                                <div class="stat-label">Total Patients</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card stat-card">
                        <div class="card-body d-flex align-items-center">
                            <div class="stat-icon bg-warning-soft me-3">
                                <i class="bi bi-calendar-check"></i>
                            </div>
                            <div>
                                <div class="stat-value">{{ stats.appointments_today }}</div>
                                <div class="stat-label">Today's Appointments</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card stat-card">
                        <div class="card-body d-flex align-items-center">
                            <div class="stat-icon bg-info-soft me-3">
                                <i class="bi bi-building"></i>
                            </div>
                            <div>
                                <div class="stat-value">{{ stats.departments }}</div>
                                <div class="stat-label">Departments</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Quick Actions -->
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">Quick Actions</h5>
                        </div>
                        <div class="card-body">
                            <div class="d-grid gap-2">
                                <router-link to="/admin/doctors" class="btn btn-outline-primary">
                                    <i class="bi bi-plus-circle"></i> Manage Doctors
                                </router-link>
                                <router-link to="/admin/appointments" class="btn btn-outline-primary">
                                    <i class="bi bi-calendar"></i> View All Appointments
                                </router-link>
                                <router-link to="/admin/patients" class="btn btn-outline-primary">
                                    <i class="bi bi-search"></i> Search Patients
                                </router-link>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">System Status</h5>
                        </div>
                        <div class="card-body">
                            <p class="text-success"><i class="bi bi-check-circle"></i> All systems operational</p>
                            <p class="text-muted mb-0">Full dashboard features coming in Milestone 3</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,

    data() {
        return {
            stats: {
                doctors: 0,
                patients: 0,
                appointments_today: 0,
                departments: 10
            }
        };
    }
};

// Make component available globally
window.AdminDashboard = AdminDashboard;
