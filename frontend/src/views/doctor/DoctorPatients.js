const DoctorPatients = {
    name: 'DoctorPatients',

    template: `
        <div class="container-fluid dashboard-container">
            <!-- Header -->
            <div class="row mb-4">
                <div class="col">
                    <nav aria-label="breadcrumb">
                        <ol class="breadcrumb">
                            <li class="breadcrumb-item">
                                <router-link to="/doctor/dashboard">Dashboard</router-link>
                            </li>
                            <li class="breadcrumb-item active">My Patients</li>
                        </ol>
                    </nav>
                    <h2><i class="bi bi-people"></i> My Patients</h2>
                </div>
            </div>

            <!-- Search -->
            <div class="card mb-4">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="input-group">
                                <span class="input-group-text"><i class="bi bi-search"></i></span>
                                <input type="text" class="form-control" placeholder="Search by name or phone..."
                                       v-model="searchQuery" @input="debouncedSearch">
                            </div>
                        </div>
                        <div class="col-md-6 text-end">
                            <span class="text-muted">{{ patients.length }} patients found</span>
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

            <!-- Patients Grid -->
            <div v-else class="row g-4">
                <div v-for="patient in patients" :key="patient.id" class="col-md-6 col-lg-4">
                    <div class="card h-100">
                        <div class="card-body">
                            <div class="d-flex align-items-center mb-3">
                                <div class="bg-primary-soft rounded-circle p-3 me-3">
                                    <i class="bi bi-person-fill text-primary"></i>
                                </div>
                                <div>
                                    <h5 class="mb-0">{{ patient.full_name }}</h5>
                                    <small class="text-muted">{{ patient.phone }}</small>
                                </div>
                            </div>
                            <div class="row text-center mb-3">
                                <div class="col">
                                    <div class="text-primary fw-bold">{{ patient.appointment_count || 0 }}</div>
                                    <small class="text-muted">Visits</small>
                                </div>
                                <div class="col">
                                    <div class="text-muted">{{ patient.age || 'N/A' }}</div>
                                    <small class="text-muted">Age</small>
                                </div>
                                <div class="col">
                                    <div class="text-muted">{{ patient.blood_group || 'N/A' }}</div>
                                    <small class="text-muted">Blood</small>
                                </div>
                            </div>
                            <button class="btn btn-outline-primary btn-sm w-100" @click="viewPatient(patient)">
                                <i class="bi bi-file-medical"></i> View History
                            </button>
                        </div>
                    </div>
                </div>

                <div v-if="patients.length === 0" class="col-12">
                    <div class="text-center text-muted py-5">
                        <i class="bi bi-people display-4"></i>
                        <p class="mt-2">No patients found</p>
                    </div>
                </div>
            </div>

            <!-- Patient Details Modal -->
            <div class="modal fade" :class="{'show d-block': showPatientModal}" tabindex="-1"
                 v-if="showPatientModal">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Patient Details</h5>
                            <button type="button" class="btn-close" @click="showPatientModal = false"></button>
                        </div>
                        <div class="modal-body" v-if="selectedPatient">
                            <!-- Patient Info -->
                            <div class="row mb-4">
                                <div class="col-md-6">
                                    <h6 class="text-muted">Personal Information</h6>
                                    <table class="table table-sm">
                                        <tr><th>Name:</th><td>{{ selectedPatient.full_name }}</td></tr>
                                        <tr><th>Phone:</th><td>{{ selectedPatient.phone }}</td></tr>
                                        <tr><th>Email:</th><td>{{ selectedPatient.email || 'N/A' }}</td></tr>
                                        <tr><th>Age:</th><td>{{ selectedPatient.age || 'N/A' }}</td></tr>
                                        <tr><th>Gender:</th><td>{{ selectedPatient.gender || 'N/A' }}</td></tr>
                                    </table>
                                </div>
                                <div class="col-md-6">
                                    <h6 class="text-muted">Medical Information</h6>
                                    <table class="table table-sm">
                                        <tr><th>Blood Group:</th><td>{{ selectedPatient.blood_group || 'N/A' }}</td></tr>
                                        <tr><th>Emergency Contact:</th><td>{{ selectedPatient.emergency_contact || 'N/A' }}</td></tr>
                                    </table>
                                    <div v-if="selectedPatient.medical_history">
                                        <h6 class="text-muted mt-3">Medical History</h6>
                                        <p class="small">{{ selectedPatient.medical_history }}</p>
                                    </div>
                                </div>
                            </div>

                            <!-- Appointment History -->
                            <h6 class="text-muted">Appointment History (with you)</h6>
                            <div class="table-responsive">
                                <table class="table table-hover table-sm">
                                    <thead>
                                        <tr>
                                            <th>Date</th>
                                            <th>Time</th>
                                            <th>Status</th>
                                            <th>Diagnosis</th>
                                            <th>Action</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="apt in selectedPatient.appointments" :key="apt.id">
                                            <td>{{ apt.appointment_date }}</td>
                                            <td>{{ apt.appointment_time }}</td>
                                            <td>
                                                <span class="badge" :class="getStatusClass(apt.status)">
                                                    {{ apt.status }}
                                                </span>
                                            </td>
                                            <td>{{ apt.treatment?.diagnosis || '-' }}</td>
                                            <td>
                                                <button v-if="apt.treatment" class="btn btn-sm btn-outline-info"
                                                        @click="viewTreatment(apt.treatment)">
                                                    <i class="bi bi-eye"></i>
                                                </button>
                                            </td>
                                        </tr>
                                        <tr v-if="!selectedPatient.appointments?.length">
                                            <td colspan="5" class="text-center text-muted">No appointments</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>

                            <!-- Full Treatment History Button -->
                            <button class="btn btn-outline-primary mt-2" @click="loadFullHistory">
                                <i class="bi bi-clock-history"></i> View Full Treatment History (All Doctors)
                            </button>

                            <!-- Full History -->
                            <div v-if="showFullHistory" class="mt-4">
                                <h6 class="text-muted">Complete Treatment History</h6>
                                <div class="table-responsive">
                                    <table class="table table-hover table-sm">
                                        <thead>
                                            <tr>
                                                <th>Date</th>
                                                <th>Doctor</th>
                                                <th>Diagnosis</th>
                                                <th>Prescription</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr v-for="h in fullHistory" :key="h.id">
                                                <td>{{ h.appointment?.date }}</td>
                                                <td>{{ h.appointment?.doctor_name }}</td>
                                                <td>{{ h.diagnosis }}</td>
                                                <td>{{ h.prescription || '-' }}</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button class="btn btn-secondary" @click="showPatientModal = false">Close</button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-backdrop fade show" v-if="showPatientModal"></div>

            <!-- Treatment Modal -->
            <div class="modal fade" :class="{'show d-block': showTreatmentModal}" tabindex="-1"
                 v-if="showTreatmentModal">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Treatment Details</h5>
                            <button type="button" class="btn-close" @click="showTreatmentModal = false"></button>
                        </div>
                        <div class="modal-body" v-if="selectedTreatment">
                            <p><strong>Diagnosis:</strong> {{ selectedTreatment.diagnosis }}</p>
                            <p v-if="selectedTreatment.prescription"><strong>Prescription:</strong><br>
                                <span style="white-space: pre-line">{{ selectedTreatment.prescription }}</span>
                            </p>
                            <p v-if="selectedTreatment.tests_recommended"><strong>Tests:</strong> {{ selectedTreatment.tests_recommended }}</p>
                            <p v-if="selectedTreatment.notes"><strong>Notes:</strong> {{ selectedTreatment.notes }}</p>
                            <p v-if="selectedTreatment.follow_up_date"><strong>Follow-up:</strong> {{ selectedTreatment.follow_up_date }}</p>
                        </div>
                        <div class="modal-footer">
                            <button class="btn btn-secondary" @click="showTreatmentModal = false">Close</button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-backdrop fade show" v-if="showTreatmentModal"></div>
        </div>
    `,

    data() {
        return {
            patients: [],
            loading: true,
            searchQuery: '',
            searchTimeout: null,
            showPatientModal: false,
            showTreatmentModal: false,
            selectedPatient: null,
            selectedTreatment: null,
            showFullHistory: false,
            fullHistory: []
        };
    },

    async created() {
        await this.loadPatients();
    },

    methods: {
        async loadPatients() {
            this.loading = true;
            const response = await doctorService.getPatients(this.searchQuery);
            if (response.success) {
                this.patients = response.patients;
            }
            this.loading = false;
        },

        debouncedSearch() {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => this.loadPatients(), 300);
        },

        async viewPatient(patient) {
            const response = await doctorService.getPatient(patient.id);
            if (response.success) {
                this.selectedPatient = response.patient;
                this.showFullHistory = false;
                this.fullHistory = [];
                this.showPatientModal = true;
            }
        },

        async loadFullHistory() {
            const response = await doctorService.getPatientHistory(this.selectedPatient.id);
            if (response.success) {
                this.fullHistory = response.history;
                this.showFullHistory = true;
            }
        },

        viewTreatment(treatment) {
            this.selectedTreatment = treatment;
            this.showTreatmentModal = true;
        },

        getStatusClass(status) {
            return { 'booked': 'bg-primary', 'completed': 'bg-success', 'cancelled': 'bg-danger' }[status] || 'bg-secondary';
        }
    }
};

window.DoctorPatients = DoctorPatients;
