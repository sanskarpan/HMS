const DepartmentList = {
    name: 'DepartmentList',

    template: `
        <div class="container-fluid dashboard-container">
            <!-- Header -->
            <div class="row mb-4">
                <div class="col">
                    <nav aria-label="breadcrumb">
                        <ol class="breadcrumb">
                            <li class="breadcrumb-item">
                                <router-link to="/patient/dashboard">Dashboard</router-link>
                            </li>
                            <li class="breadcrumb-item active">Departments</li>
                        </ol>
                    </nav>
                    <h2><i class="bi bi-building"></i> Departments</h2>
                    <p class="text-muted">Select a department to view doctors and book appointments</p>
                </div>
            </div>

            <!-- Loading -->
            <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>

            <!-- Department Grid -->
            <div v-else class="row g-4">
                <div class="col-md-4 col-lg-3" v-for="dept in departments" :key="dept.id">
                    <div class="card h-100 shadow-sm hover-card" @click="goToDepartment(dept.id)" style="cursor: pointer;">
                        <div class="card-body text-center">
                            <i class="bi bi-hospital display-3 text-primary mb-3"></i>
                            <h5 class="card-title">{{ dept.name }}</h5>
                            <p class="card-text text-muted small">{{ dept.description }}</p>
                            <div class="mt-3">
                                <span class="badge bg-primary">{{ dept.doctor_count }} Doctor(s)</span>
                            </div>
                        </div>
                        <div class="card-footer bg-transparent text-center">
                            <small class="text-primary">Click to view doctors <i class="bi bi-arrow-right"></i></small>
                        </div>
                    </div>
                </div>

                <div v-if="departments.length === 0" class="col-12 text-center py-5">
                    <i class="bi bi-building display-1 text-muted"></i>
                    <p class="text-muted mt-3">No departments available</p>
                </div>
            </div>
        </div>
    `,

    data() {
        return {
            departments: [],
            loading: true
        };
    },

    async created() {
        await this.loadDepartments();
    },

    methods: {
        async loadDepartments() {
            this.loading = true;
            const response = await patientService.getDepartments();
            if (response.success) {
                this.departments = response.departments;
            }
            this.loading = false;
        },

        goToDepartment(deptId) {
            this.$router.push(`/patient/departments/${deptId}`);
        }
    }
};

window.DepartmentList = DepartmentList;
