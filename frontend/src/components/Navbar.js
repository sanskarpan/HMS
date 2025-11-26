/**
 * Navbar Component
 * Displays navigation bar with user info and logout button when authenticated.
 */

const Navbar = {
    name: 'Navbar',

    template: `
        <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm" v-if="isAuthenticated">
            <div class="container-fluid">
                <router-link class="navbar-brand" to="/">
                    <i class="bi bi-hospital"></i> HMS
                </router-link>

                <button class="navbar-toggler" type="button" data-bs-toggle="collapse"
                        data-bs-target="#navbarNav" aria-controls="navbarNav"
                        aria-expanded="false" aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>

                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav me-auto">
                        <!-- Admin Navigation -->
                        <template v-if="isAdmin">
                            <li class="nav-item">
                                <router-link class="nav-link" to="/admin/dashboard">
                                    <i class="bi bi-speedometer2"></i> Dashboard
                                </router-link>
                            </li>
                            <li class="nav-item">
                                <router-link class="nav-link" to="/admin/doctors">
                                    <i class="bi bi-person-badge"></i> Doctors
                                </router-link>
                            </li>
                            <li class="nav-item">
                                <router-link class="nav-link" to="/admin/patients">
                                    <i class="bi bi-people"></i> Patients
                                </router-link>
                            </li>
                            <li class="nav-item">
                                <router-link class="nav-link" to="/admin/appointments">
                                    <i class="bi bi-calendar-check"></i> Appointments
                                </router-link>
                            </li>
                        </template>

                        <!-- Doctor Navigation -->
                        <template v-if="isDoctor">
                            <li class="nav-item">
                                <router-link class="nav-link" to="/doctor/dashboard">
                                    <i class="bi bi-speedometer2"></i> Dashboard
                                </router-link>
                            </li>
                            <li class="nav-item">
                                <router-link class="nav-link" to="/doctor/appointments">
                                    <i class="bi bi-calendar-check"></i> Appointments
                                </router-link>
                            </li>
                            <li class="nav-item">
                                <router-link class="nav-link" to="/doctor/patients">
                                    <i class="bi bi-people"></i> My Patients
                                </router-link>
                            </li>
                            <li class="nav-item">
                                <router-link class="nav-link" to="/doctor/availability">
                                    <i class="bi bi-clock"></i> Availability
                                </router-link>
                            </li>
                        </template>

                        <!-- Patient Navigation -->
                        <template v-if="isPatient">
                            <li class="nav-item">
                                <router-link class="nav-link" to="/patient/dashboard">
                                    <i class="bi bi-speedometer2"></i> Dashboard
                                </router-link>
                            </li>
                            <li class="nav-item">
                                <router-link class="nav-link" to="/patient/departments">
                                    <i class="bi bi-building"></i> Departments
                                </router-link>
                            </li>
                            <li class="nav-item">
                                <router-link class="nav-link" to="/patient/appointments">
                                    <i class="bi bi-calendar-check"></i> My Appointments
                                </router-link>
                            </li>
                            <li class="nav-item">
                                <router-link class="nav-link" to="/patient/history">
                                    <i class="bi bi-file-medical"></i> History
                                </router-link>
                            </li>
                        </template>
                    </ul>

                    <!-- User Menu -->
                    <ul class="navbar-nav">
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" href="#" id="userDropdown"
                               role="button" data-bs-toggle="dropdown" aria-expanded="false">
                                <i class="bi bi-person-circle"></i>
                                {{ userName }}
                                <span class="badge bg-secondary ms-1">{{ userRole }}</span>
                            </a>
                            <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
                                <li>
                                    <router-link class="dropdown-item" :to="profileRoute">
                                        <i class="bi bi-person"></i> Profile
                                    </router-link>
                                </li>
                                <li><hr class="dropdown-divider"></li>
                                <li>
                                    <a class="dropdown-item text-danger" href="#" @click.prevent="logout">
                                        <i class="bi bi-box-arrow-right"></i> Logout
                                    </a>
                                </li>
                            </ul>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
    `,

    computed: {
        isAuthenticated() {
            return authService.isAuthenticated();
        },
        isAdmin() {
            return authService.isAdmin();
        },
        isDoctor() {
            return authService.isDoctor();
        },
        isPatient() {
            return authService.isPatient();
        },
        user() {
            return authService.getUser();
        },
        userName() {
            return this.user ? this.user.username : '';
        },
        userRole() {
            return this.user ? this.user.role : '';
        },
        profileRoute() {
            const role = authService.getRole();
            return `/${role}/profile`;
        }
    },

    methods: {
        async logout() {
            await authService.logout();
            this.$router.push('/login');
        }
    }
};

// Make component available globally
window.Navbar = Navbar;
