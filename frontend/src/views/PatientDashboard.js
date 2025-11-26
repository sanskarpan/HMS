/**
 * Patient Dashboard View Component
 * Displays departments, appointments, and patient-specific options.
 */

const PatientDashboard = {
    name: 'PatientDashboard',

    template: `
        <div class="container-fluid dashboard-container">
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

            <!-- Departments Section -->
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0"><i class="bi bi-building"></i> Departments</h5>
                </div>
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-4" v-for="dept in departments" :key="dept.id">
                            <div class="card h-100">
                                <div class="card-body">
                                    <h6>{{ dept.name }}</h6>
                                    <p class="text-muted small mb-2">{{ dept.description }}</p>
                                    <router-link :to="'/patient/departments/' + dept.id"
                                                 class="btn btn-sm btn-outline-primary">
                                        View Details
                                    </router-link>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div v-if="loading" class="text-center py-4">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading...</span>
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
                    <div class="table-responsive">
                        <table class="table table-hover" v-if="appointments.length > 0">
                            <thead>
                                <tr>
                                    <th>Sr. No</th>
                                    <th>Doctor Name</th>
                                    <th>Department</th>
                                    <th>Date</th>
                                    <th>Time</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="(apt, index) in appointments" :key="apt.id">
                                    <td>{{ index + 1 }}</td>
                                    <td>{{ apt.doctor_name }}</td>
                                    <td>{{ apt.department }}</td>
                                    <td>{{ apt.date }}</td>
                                    <td>{{ apt.time }}</td>
                                    <td>
                                        <button class="btn btn-sm btn-outline-danger">
                                            Cancel
                                        </button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                        <div v-else class="text-center py-4">
                            <p class="text-muted mb-0">No upcoming appointments</p>
                            <router-link to="/patient/departments" class="btn btn-primary mt-2">
                                Book Your First Appointment
                            </router-link>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,

    data() {
        return {
            departments: [],
            appointments: [],
            loading: true
        };
    },

    computed: {
        userName() {
            const user = authService.getUser();
            if (user && user.profile) {
                return user.profile.full_name || user.username;
            }
            return user ? user.username : '';
        }
    },

    async created() {
        // Load departments (placeholder data for now, will be replaced in Milestone 5)
        this.departments = [
            { id: 1, name: 'Cardiology', description: 'Heart and cardiovascular care' },
            { id: 2, name: 'Oncology', description: 'Cancer diagnosis and treatment' },
            { id: 3, name: 'General Medicine', description: 'Primary healthcare services' },
            { id: 4, name: 'Orthopedics', description: 'Bone and joint care' },
            { id: 5, name: 'Pediatrics', description: 'Child healthcare' },
            { id: 6, name: 'Neurology', description: 'Brain and nervous system' }
        ];
        this.loading = false;
    }
};

// Make component available globally
window.PatientDashboard = PatientDashboard;
