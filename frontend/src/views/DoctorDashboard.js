/**
 * Doctor Dashboard View Component
 * Displays doctor-specific appointments and patient information.
 */

const DoctorDashboard = {
    name: 'DoctorDashboard',

    template: `
        <div class="container-fluid dashboard-container">
            <div class="row mb-4">
                <div class="col">
                    <h2>Welcome, Dr. {{ userName }}</h2>
                    <p class="text-muted">Your Dashboard</p>
                </div>
            </div>

            <!-- Stats Cards -->
            <div class="row g-4 mb-4">
                <div class="col-md-4">
                    <div class="card stat-card">
                        <div class="card-body d-flex align-items-center">
                            <div class="stat-icon bg-primary-soft me-3">
                                <i class="bi bi-calendar-check"></i>
                            </div>
                            <div>
                                <div class="stat-value">{{ stats.today }}</div>
                                <div class="stat-label">Today's Appointments</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
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
                <div class="col-md-4">
                    <div class="card stat-card">
                        <div class="card-body d-flex align-items-center">
                            <div class="stat-icon bg-warning-soft me-3">
                                <i class="bi bi-hourglass-split"></i>
                            </div>
                            <div>
                                <div class="stat-value">{{ stats.pending }}</div>
                                <div class="stat-label">Pending</div>
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
                                <router-link to="/doctor/appointments" class="btn btn-outline-primary">
                                    <i class="bi bi-calendar"></i> View Appointments
                                </router-link>
                                <router-link to="/doctor/availability" class="btn btn-outline-primary">
                                    <i class="bi bi-clock"></i> Update Availability
                                </router-link>
                                <router-link to="/doctor/patients" class="btn btn-outline-primary">
                                    <i class="bi bi-people"></i> View Patients
                                </router-link>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">Today's Schedule</h5>
                        </div>
                        <div class="card-body">
                            <p class="text-muted">Full dashboard features coming in Milestone 4</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,

    data() {
        return {
            stats: {
                today: 0,
                patients: 0,
                pending: 0
            }
        };
    },

    computed: {
        userName() {
            const user = authService.getUser();
            return user ? user.username : '';
        }
    }
};

// Make component available globally
window.DoctorDashboard = DoctorDashboard;
