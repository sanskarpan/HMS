const { createRouter, createWebHistory } = VueRouter;

const routes = [
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

const router = createRouter({
    history: createWebHistory(),
    routes
});

router.beforeEach((to, from, next) => {
    const isAuthenticated = authService.isAuthenticated();
    const userRole = authService.getRole();

    if (to.meta.public) {
        if (to.meta.onlyGuest && isAuthenticated) {
            return next(authService.getDashboardRoute());
        }
        return next();
    }

    if (to.meta.requiresAuth) {
        if (!isAuthenticated) {
            return next('/login');
        }
        if (to.meta.role && to.meta.role !== userRole) {
            return next(authService.getDashboardRoute());
        }
        return next();
    }

    next();
});

window.router = router;
