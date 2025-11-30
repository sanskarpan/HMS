const DoctorSearch = {
    name: 'DoctorSearch',

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
                            <li class="breadcrumb-item active">Find Doctors</li>
                        </ol>
                    </nav>
                    <h2><i class="bi bi-search"></i> Find Doctors</h2>
                </div>
            </div>

            <!-- Search Filters -->
            <div class="card mb-4">
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <div class="input-group">
                                <span class="input-group-text"><i class="bi bi-search"></i></span>
                                <input type="text" class="form-control" v-model="searchQuery"
                                       placeholder="Search by doctor name..." @input="searchDoctors">
                            </div>
                        </div>
                        <div class="col-md-4">
                            <select class="form-select" v-model="selectedDepartment" @change="searchDoctors">
                                <option value="">All Departments</option>
                                <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                                    {{ dept.name }}
                                </option>
                            </select>
                        </div>
                        <div class="col-md-2">
                            <button class="btn btn-outline-secondary w-100" @click="clearFilters">
                                Clear
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Loading -->
            <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>

            <!-- Results -->
            <div v-else>
                <p class="text-muted mb-3">Found {{ doctors.length }} doctor(s)</p>

                <div class="row g-4">
                    <div class="col-md-6 col-lg-4" v-for="doctor in doctors" :key="doctor.id">
                        <div class="card h-100 shadow-sm">
                            <div class="card-body">
                                <div class="d-flex align-items-center mb-3">
                                    <div class="bg-primary rounded-circle me-3" style="width: 50px; height: 50px; display: flex; align-items: center; justify-content: center;">
                                        <i class="bi bi-person-fill text-white fs-5"></i>
                                    </div>
                                    <div>
                                        <h6 class="mb-0">Dr. {{ doctor.full_name }}</h6>
                                        <small class="text-primary">{{ doctor.department ? doctor.department.name : 'General' }}</small>
                                    </div>
                                </div>
                                <p class="text-muted small mb-2">{{ doctor.qualification || 'Medical Specialist' }}</p>
                                <div class="d-flex justify-content-between text-muted small mb-3">
                                    <span><i class="bi bi-clock"></i> {{ doctor.experience_years || 0 }} yrs exp</span>
                                    <span><i class="bi bi-currency-dollar"></i> \${{ doctor.consultation_fee || 'N/A' }}</span>
                                </div>
                            </div>
                            <div class="card-footer bg-transparent">
                                <router-link :to="'/patient/doctors/' + doctor.id" class="btn btn-primary btn-sm w-100">
                                    <i class="bi bi-calendar-plus"></i> View & Book
                                </router-link>
                            </div>
                        </div>
                    </div>

                    <div v-if="doctors.length === 0" class="col-12 text-center py-5">
                        <i class="bi bi-person-x display-1 text-muted"></i>
                        <p class="text-muted mt-3">No doctors found matching your criteria</p>
                    </div>
                </div>
            </div>
        </div>
    `,

    data() {
        return {
            searchQuery: '',
            selectedDepartment: '',
            departments: [],
            doctors: [],
            loading: true,
            searchTimeout: null
        };
    },

    async created() {
        await this.loadDepartments();
        await this.searchDoctors();
    },

    methods: {
        async loadDepartments() {
            const response = await patientService.getDepartments();
            if (response.success) {
                this.departments = response.departments;
            }
        },

        async searchDoctors() {
            // Debounce search
            if (this.searchTimeout) {
                clearTimeout(this.searchTimeout);
            }

            this.searchTimeout = setTimeout(async () => {
                this.loading = true;
                const response = await patientService.searchDoctors({
                    search: this.searchQuery,
                    department_id: this.selectedDepartment || undefined
                });
                if (response.success) {
                    this.doctors = response.doctors;
                }
                this.loading = false;
            }, 300);
        },

        clearFilters() {
            this.searchQuery = '';
            this.selectedDepartment = '';
            this.searchDoctors();
        }
    }
};

window.DoctorSearch = DoctorSearch;
