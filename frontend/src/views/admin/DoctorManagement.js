/**
 * Doctor Management View Component
 * Admin interface for managing doctors (CRUD operations).
 */

const DoctorManagement = {
    name: 'DoctorManagement',

    template: `
        <div class="container-fluid dashboard-container">
            <!-- Header -->
            <div class="row mb-4">
                <div class="col">
                    <nav aria-label="breadcrumb">
                        <ol class="breadcrumb">
                            <li class="breadcrumb-item">
                                <router-link to="/admin/dashboard">Dashboard</router-link>
                            </li>
                            <li class="breadcrumb-item active">Doctors</li>
                        </ol>
                    </nav>
                    <h2><i class="bi bi-person-badge"></i> Doctor Management</h2>
                </div>
                <div class="col-auto">
                    <button class="btn btn-primary" @click="showAddModal = true">
                        <i class="bi bi-plus-circle"></i> Add Doctor
                    </button>
                </div>
            </div>

            <!-- Search and Filter -->
            <div class="card mb-4">
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-4">
                            <input type="text" class="form-control" placeholder="Search by name..."
                                   v-model="searchQuery" @input="debouncedSearch">
                        </div>
                        <div class="col-md-3">
                            <select class="form-select" v-model="filterDepartment" @change="loadDoctors">
                                <option value="">All Departments</option>
                                <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                                    {{ dept.name }}
                                </option>
                            </select>
                        </div>
                        <div class="col-md-3">
                            <div class="form-check mt-2">
                                <input class="form-check-input" type="checkbox" id="includeInactive"
                                       v-model="includeInactive" @change="loadDoctors">
                                <label class="form-check-label" for="includeInactive">
                                    Include inactive
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>

            <!-- Doctors Table -->
            <div v-else class="card">
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Department</th>
                                    <th>Qualification</th>
                                    <th>Experience</th>
                                    <th>Email</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="doctor in doctors" :key="doctor.id"
                                    :class="{'table-secondary': !doctor.is_active || doctor.is_blacklisted}">
                                    <td>
                                        <strong>{{ doctor.full_name }}</strong>
                                    </td>
                                    <td>{{ doctor.department?.name || 'N/A' }}</td>
                                    <td>{{ doctor.qualification || 'N/A' }}</td>
                                    <td>{{ doctor.experience_years }} years</td>
                                    <td>{{ doctor.email }}</td>
                                    <td>
                                        <span v-if="doctor.is_blacklisted" class="badge bg-danger">Blacklisted</span>
                                        <span v-else-if="!doctor.is_active" class="badge bg-secondary">Inactive</span>
                                        <span v-else class="badge bg-success">Active</span>
                                    </td>
                                    <td>
                                        <div class="btn-group btn-group-sm">
                                            <button class="btn btn-outline-primary" @click="editDoctor(doctor)"
                                                    title="Edit">
                                                <i class="bi bi-pencil"></i>
                                            </button>
                                            <button v-if="!doctor.is_blacklisted"
                                                    class="btn btn-outline-warning" @click="blacklistDoctor(doctor)"
                                                    title="Blacklist">
                                                <i class="bi bi-person-slash"></i>
                                            </button>
                                            <button v-else class="btn btn-outline-success"
                                                    @click="unblacklistDoctor(doctor)" title="Unblacklist">
                                                <i class="bi bi-person-check"></i>
                                            </button>
                                            <button class="btn btn-outline-danger" @click="confirmDelete(doctor)"
                                                    title="Delete">
                                                <i class="bi bi-trash"></i>
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                                <tr v-if="doctors.length === 0">
                                    <td colspan="7" class="text-center text-muted py-4">
                                        No doctors found
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Add/Edit Doctor Modal -->
            <div class="modal fade" :class="{'show d-block': showAddModal || showEditModal}" tabindex="-1"
                 v-if="showAddModal || showEditModal">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                {{ showEditModal ? 'Edit Doctor' : 'Add New Doctor' }}
                            </h5>
                            <button type="button" class="btn-close" @click="closeModal"></button>
                        </div>
                        <div class="modal-body">
                            <form @submit.prevent="saveDoctor">
                                <div class="row g-3">
                                    <!-- User Account Fields (only for new doctors) -->
                                    <template v-if="showAddModal">
                                        <div class="col-md-6">
                                            <label class="form-label">Username *</label>
                                            <input type="text" class="form-control" v-model="doctorForm.username"
                                                   required>
                                        </div>
                                        <div class="col-md-6">
                                            <label class="form-label">Email *</label>
                                            <input type="email" class="form-control" v-model="doctorForm.email"
                                                   required>
                                        </div>
                                        <div class="col-md-6">
                                            <label class="form-label">Password *</label>
                                            <input type="password" class="form-control" v-model="doctorForm.password"
                                                   required minlength="6">
                                        </div>
                                    </template>

                                    <!-- Profile Fields -->
                                    <div class="col-md-6">
                                        <label class="form-label">Full Name *</label>
                                        <input type="text" class="form-control" v-model="doctorForm.full_name"
                                               required>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label">Department *</label>
                                        <select class="form-select" v-model="doctorForm.department_id" required>
                                            <option value="">Select Department</option>
                                            <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                                                {{ dept.name }}
                                            </option>
                                        </select>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label">Qualification</label>
                                        <input type="text" class="form-control" v-model="doctorForm.qualification"
                                               placeholder="e.g., MBBS, MD - Cardiology">
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label">Experience (years)</label>
                                        <input type="number" class="form-control" v-model="doctorForm.experience_years"
                                               min="0">
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label">Phone</label>
                                        <input type="tel" class="form-control" v-model="doctorForm.phone">
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label">Consultation Fee</label>
                                        <input type="number" class="form-control" v-model="doctorForm.consultation_fee"
                                               min="0" step="0.01">
                                    </div>
                                    <div class="col-12">
                                        <label class="form-label">Bio</label>
                                        <textarea class="form-control" v-model="doctorForm.bio" rows="3"></textarea>
                                    </div>
                                </div>

                                <!-- Error Message -->
                                <div v-if="formError" class="alert alert-danger mt-3 mb-0">
                                    {{ formError }}
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
                            <button type="button" class="btn btn-primary" @click="saveDoctor" :disabled="saving">
                                <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
                                {{ showEditModal ? 'Update' : 'Create' }}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-backdrop fade show" v-if="showAddModal || showEditModal"></div>

            <!-- Delete Confirmation Modal -->
            <div class="modal fade" :class="{'show d-block': showDeleteModal}" tabindex="-1" v-if="showDeleteModal">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Confirm Delete</h5>
                            <button type="button" class="btn-close" @click="showDeleteModal = false"></button>
                        </div>
                        <div class="modal-body">
                            <p>Are you sure you want to deactivate <strong>{{ selectedDoctor?.full_name }}</strong>?</p>
                            <p class="text-muted small">This will prevent them from logging in.</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" @click="showDeleteModal = false">
                                Cancel
                            </button>
                            <button type="button" class="btn btn-danger" @click="deleteDoctor" :disabled="saving">
                                <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
                                Deactivate
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-backdrop fade show" v-if="showDeleteModal"></div>

            <!-- Toast Notification -->
            <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 1100">
                <div class="toast align-items-center text-white border-0" :class="toastClass"
                     :class="{'show': showToast}" role="alert">
                    <div class="d-flex">
                        <div class="toast-body">{{ toastMessage }}</div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto"
                                @click="showToast = false"></button>
                    </div>
                </div>
            </div>
        </div>
    `,

    data() {
        return {
            doctors: [],
            departments: [],
            loading: true,
            saving: false,
            searchQuery: '',
            filterDepartment: '',
            includeInactive: false,
            showAddModal: false,
            showEditModal: false,
            showDeleteModal: false,
            selectedDoctor: null,
            doctorForm: this.getEmptyForm(),
            formError: null,
            showToast: false,
            toastMessage: '',
            toastClass: 'bg-success',
            searchTimeout: null
        };
    },

    async created() {
        await Promise.all([
            this.loadDepartments(),
            this.loadDoctors()
        ]);
    },

    methods: {
        getEmptyForm() {
            return {
                username: '',
                email: '',
                password: '',
                full_name: '',
                department_id: '',
                qualification: '',
                experience_years: 0,
                phone: '',
                bio: '',
                consultation_fee: 0
            };
        },

        async loadDepartments() {
            const response = await adminService.getDepartments();
            if (response.success) {
                this.departments = response.departments;
            }
        },

        async loadDoctors() {
            this.loading = true;
            const response = await adminService.getDoctors({
                search: this.searchQuery,
                department_id: this.filterDepartment,
                include_inactive: this.includeInactive
            });

            if (response.success) {
                this.doctors = response.doctors;
            }
            this.loading = false;
        },

        debouncedSearch() {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => {
                this.loadDoctors();
            }, 300);
        },

        editDoctor(doctor) {
            this.selectedDoctor = doctor;
            this.doctorForm = {
                full_name: doctor.full_name,
                department_id: doctor.department?.id || '',
                qualification: doctor.qualification || '',
                experience_years: doctor.experience_years || 0,
                phone: doctor.phone || '',
                bio: doctor.bio || '',
                consultation_fee: doctor.consultation_fee || 0
            };
            this.formError = null;
            this.showEditModal = true;
        },

        async saveDoctor() {
            this.saving = true;
            this.formError = null;

            try {
                let response;
                if (this.showEditModal) {
                    response = await adminService.updateDoctor(this.selectedDoctor.id, this.doctorForm);
                } else {
                    response = await adminService.createDoctor(this.doctorForm);
                }

                if (response.success) {
                    this.showToastMessage(
                        this.showEditModal ? 'Doctor updated successfully' : 'Doctor created successfully',
                        'bg-success'
                    );
                    this.closeModal();
                    await this.loadDoctors();
                } else {
                    this.formError = response.message || 'Operation failed';
                }
            } catch (err) {
                this.formError = 'An error occurred';
            } finally {
                this.saving = false;
            }
        },

        async blacklistDoctor(doctor) {
            if (!confirm('Are you sure you want to blacklist ' + doctor.full_name + '?')) return;

            const response = await adminService.toggleDoctorBlacklist(doctor.id, true);
            if (response.success) {
                this.showToastMessage('Doctor blacklisted successfully', 'bg-warning');
                await this.loadDoctors();
            } else {
                this.showToastMessage(response.message || 'Failed to blacklist', 'bg-danger');
            }
        },

        async unblacklistDoctor(doctor) {
            const response = await adminService.toggleDoctorBlacklist(doctor.id, false);
            if (response.success) {
                this.showToastMessage('Doctor unblacklisted successfully', 'bg-success');
                await this.loadDoctors();
            } else {
                this.showToastMessage(response.message || 'Failed to unblacklist', 'bg-danger');
            }
        },

        confirmDelete(doctor) {
            this.selectedDoctor = doctor;
            this.showDeleteModal = true;
        },

        async deleteDoctor() {
            this.saving = true;
            const response = await adminService.deleteDoctor(this.selectedDoctor.id);

            if (response.success) {
                this.showToastMessage('Doctor deactivated successfully', 'bg-success');
                this.showDeleteModal = false;
                await this.loadDoctors();
            } else {
                this.showToastMessage(response.message || 'Failed to deactivate', 'bg-danger');
            }
            this.saving = false;
        },

        closeModal() {
            this.showAddModal = false;
            this.showEditModal = false;
            this.selectedDoctor = null;
            this.doctorForm = this.getEmptyForm();
            this.formError = null;
        },

        showToastMessage(message, className = 'bg-success') {
            this.toastMessage = message;
            this.toastClass = className;
            this.showToast = true;
            setTimeout(() => {
                this.showToast = false;
            }, 3000);
        }
    }
};

// Make component available globally
window.DoctorManagement = DoctorManagement;
