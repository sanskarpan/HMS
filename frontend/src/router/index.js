/**
 * Vue Router Configuration with Authentication Guards
 * Handles route protection based on authentication and user roles.
 */

const { createRouter, createWebHistory } = VueRouter;

// Define routes
const routes = [
    // Public routes
    {
        path: '/',
        redirect: '/login'
    },
    {
        path: '/login',
        name: 'Login',
        component: Login,
        meta: { public: true, onlyGuest: true }
    },
    {
        path: '/register',
        name: 'Register',
        component: Register,
        meta: { public: true, onlyGuest: true }
    },

    // Admin routes
    {
        path: '/admin/dashboard',
        name: 'AdminDashboard',
        component: AdminDashboard,
        meta: { requiresAuth: true, role: 'admin' }
    },
    {
        path: '/admin/doctors',
        name: 'AdminDoctors',
        component: DoctorManagement,
        meta: { requiresAuth: true, role: 'admin' }
    },
    {
        path: '/admin/patients',
        name: 'AdminPatients',
        component: PatientManagement,
        meta: { requiresAuth: true, role: 'admin' }
    },
    {
        path: '/admin/appointments',
        name: 'AdminAppointments',
        component: AppointmentManagement,
        meta: { requiresAuth: true, role: 'admin' }
    },
    {
        path: '/admin/profile',
        name: 'AdminProfile',
        component: AdminDashboard, // TODO
        meta: { requiresAuth: true, role: 'admin' }
    },

    // Doctor routes
    {
        path: '/doctor/dashboard',
        name: 'DoctorDashboard',
        component: DoctorDashboard,
        meta: { requiresAuth: true, role: 'doctor' }
    },
    {
        path: '/doctor/appointments',
        name: 'DoctorAppointments',
        component: DoctorAppointments,
        meta: { requiresAuth: true, role: 'doctor' }
    },
    {
        path: '/doctor/patients',
        name: 'DoctorPatients',
        component: DoctorPatients,
        meta: { requiresAuth: true, role: 'doctor' }
    },
    {
        path: '/doctor/availability',
        name: 'DoctorAvailability',
        component: DoctorAvailability,
        meta: { requiresAuth: true, role: 'doctor' }
    },
    {
        path: '/doctor/profile',
        name: 'DoctorProfile',
        component: DoctorProfile,
        meta: { requiresAuth: true, role: 'doctor' }
    },

    // Patient routes
    {
        path: '/patient/dashboard',
        name: 'PatientDashboard',
        component: PatientDashboard,
        meta: { requiresAuth: true, role: 'patient' }
    },
    {
        path: '/patient/departments',
        name: 'PatientDepartments',
        component: DepartmentList,
        meta: { requiresAuth: true, role: 'patient' }
    },
    {
        path: '/patient/departments/:id',
        name: 'PatientDepartmentDetails',
        component: DepartmentDetails,
        meta: { requiresAuth: true, role: 'patient' }
    },
    {
        path: '/patient/doctors',
        name: 'PatientDoctorSearch',
        component: DoctorSearch,
        meta: { requiresAuth: true, role: 'patient' }
    },
    {
        path: '/patient/doctors/:id',
        name: 'PatientDoctorDetails',
        component: DoctorDetails,
        meta: { requiresAuth: true, role: 'patient' }
    },
    {
        path: '/patient/appointments',
        name: 'PatientAppointments',
        component: PatientAppointments,
        meta: { requiresAuth: true, role: 'patient' }
    },
    {
        path: '/patient/history',
        name: 'PatientHistory',
        component: PatientHistory,
        meta: { requiresAuth: true, role: 'patient' }
    },
    {
        path: '/patient/treatments',
        name: 'PatientTreatments',
        component: PatientTreatments,
        meta: { requiresAuth: true, role: 'patient' }
    },
    {
        path: '/patient/profile',
        name: 'PatientProfile',
        component: PatientProfile,
        meta: { requiresAuth: true, role: 'patient' }
    },

    // Catch-all route (404)
    {
        path: '/:pathMatch(.*)*',
        name: 'NotFound',
        component: {
            template: `
                <div class="container text-center py-5">
                    <h1 class="display-1">404</h1>
                    <p class="lead">Page not found</p>
                    <router-link to="/" class="btn btn-primary">Go Home</router-link>
                </div>
            `
        }
    }
];

// Create router instance
const router = createRouter({
    history: createWebHistory(),
    routes
});

// Navigation guard for authentication and role-based access
router.beforeEach((to, from, next) => {
    const isAuthenticated = authService.isAuthenticated();
    const userRole = authService.getRole();

    // Public routes that don't require auth
    if (to.meta.public) {
        // If user is logged in and tries to access guest-only pages (login/register)
        if (to.meta.onlyGuest && isAuthenticated) {
            return next(authService.getDashboardRoute());
        }
        return next();
    }

    // Protected routes
    if (to.meta.requiresAuth) {
        if (!isAuthenticated) {
            // Not logged in - redirect to login
            return next('/login');
        }

        // Check role if specified
        if (to.meta.role && to.meta.role !== userRole) {
            // Wrong role - redirect to correct dashboard
            return next(authService.getDashboardRoute());
        }

        return next();
    }

    // Default - allow
    next();
});

// Make router available globally
window.router = router;
