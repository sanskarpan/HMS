/**
 * Department Details View Component 
 * Shows doctors in a department with booking options.
 */

const DepartmentDetails = {
    name: 'DepartmentDetails',

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
                            <li class="breadcrumb-item">
                                <router-link to="/patient/departments">Departments</router-link>
                            </li>
                            <li class="breadcrumb-item active">{{ department.name }}</li>
                        </ol>
                    </nav>
                    <h2><i class="bi bi-hospital"></i> {{ department.name }}</h2>
                    <p class="text-muted">{{ department.description }}</p>
                </div>
            </div>

            <!-- Loading -->
            <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>

            <!-- Doctors List -->
            <div v-else>
                <div class="row g-4">
                    <div class="col-md-6 col-lg-4" v-for="doctor in doctors" :key="doctor.id">
                        <div class="card h-100 shadow-sm">
                            <div class="card-body">
                                <div class="d-flex align-items-center mb-3">
                                    <div class="bg-primary rounded-circle me-3" style="width: 60px; height: 60px; display: flex; align-items: center; justify-content: center;">
                                        <i class="bi bi-person-fill text-white fs-4"></i>
                                    </div>
                                    <div>
                                        <h5 class="mb-0">Dr. {{ doctor.full_name }}</h5>
                                        <small class="text-muted">{{ doctor.qualification || 'Specialist' }}</small>
                                    </div>
                                </div>
                                <ul class="list-unstyled mb-3">
                                    <li><i class="bi bi-clock me-2 text-muted"></i>{{ doctor.experience_years || 0 }} years experience</li>
                                    <li><i class="bi bi-currency-dollar me-2 text-muted"></i>Fee: ${{ doctor.consultation_fee || 'N/A' }}</li>
                                </ul>
                                <p class="text-muted small mb-3">{{ doctor.bio || 'Experienced medical professional' }}</p>
                            </div>
                            <div class="card-footer bg-transparent">
                                <button class="btn btn-primary w-100" @click="selectDoctor(doctor)">
                                    <i class="bi bi-calendar-plus me-1"></i> Book Appointment
                                </button>
                            </div>
                        </div>
                    </div>

                    <div v-if="doctors.length === 0" class="col-12 text-center py-5">
                        <i class="bi bi-person-x display-1 text-muted"></i>
                        <p class="text-muted mt-3">No doctors available in this department</p>
                    </div>
                </div>
            </div>

            <!-- Booking Modal -->
            <div class="modal fade" id="bookingModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Book Appointment with Dr. {{ selectedDoctor.full_name }}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <!-- Doctor Info -->
                            <div class="alert alert-info">
                                <strong>{{ selectedDoctor.qualification }}</strong> |
                                Fee: ${{ selectedDoctor.consultation_fee }} |
                                {{ selectedDoctor.experience_years }} years experience
                            </div>

                            <!-- Date Selection -->
                            <div class="mb-4">
                                <label class="form-label fw-bold">Select Date</label>
                                <div class="row g-2">
                                    <div class="col-auto" v-for="day in availability" :key="day.date">
                                        <button type="button" class="btn"
                                                :class="day.date === bookingForm.date ? 'btn-primary' : (day.is_available ? 'btn-outline-primary' : 'btn-outline-secondary')"
                                                :disabled="!day.is_available"
                                                @click="selectDate(day)">
                                            <div class="text-center">
                                                <small>{{ day.day_name.substring(0, 3) }}</small><br>
                                                <strong>{{ formatDateShort(day.date) }}</strong>
                                            </div>
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <!-- Time Slots -->
                            <div v-if="bookingForm.date" class="mb-4">
                                <label class="form-label fw-bold">Select Time Slot</label>

                                <div v-if="selectedDaySlots.morning_slots.length > 0" class="mb-3">
                                    <small class="text-muted d-block mb-2">Morning</small>
                                    <div class="d-flex flex-wrap gap-2">
                                        <button v-for="slot in selectedDaySlots.morning_slots" :key="slot"
                                                type="button" class="btn btn-sm"
                                                :class="bookingForm.time === slot ? 'btn-success' : 'btn-outline-success'"
                                                @click="bookingForm.time = slot">
                                            {{ slot }}
                                        </button>
                                    </div>
                                </div>

                                <div v-if="selectedDaySlots.evening_slots.length > 0">
                                    <small class="text-muted d-block mb-2">Evening</small>
                                    <div class="d-flex flex-wrap gap-2">
                                        <button v-for="slot in selectedDaySlots.evening_slots" :key="slot"
                                                type="button" class="btn btn-sm"
                                                :class="bookingForm.time === slot ? 'btn-success' : 'btn-outline-success'"
                                                @click="bookingForm.time = slot">
                                            {{ slot }}
                                        </button>
                                    </div>
                                </div>

                                <div v-if="selectedDaySlots.morning_slots.length === 0 && selectedDaySlots.evening_slots.length === 0"
                                     class="text-muted text-center py-3">
                                    No slots available for this date
                                </div>
                            </div>

                            <!-- Reason -->
                            <div class="mb-3">
                                <label class="form-label">Reason for Visit (Optional)</label>
                                <textarea class="form-control" v-model="bookingForm.reason" rows="2"
                                          placeholder="Describe your symptoms or reason for consultation"></textarea>
                            </div>

                            <div v-if="bookingError" class="alert alert-danger">{{ bookingError }}</div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" @click="confirmBooking"
                                    :disabled="!bookingForm.date || !bookingForm.time || booking">
                                <span v-if="booking" class="spinner-border spinner-border-sm me-1"></span>
                                Confirm Booking
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,

    data() {
        return {
            department: { name: '', description: '' },
            doctors: [],
            loading: true,
            selectedDoctor: {},
            availability: [],
            bookingForm: {
                date: '',
                time: '',
                reason: ''
            },
            booking: false,
            bookingError: null,
            bookingModalInstance: null
        };
    },

    computed: {
        selectedDaySlots() {
            const day = this.availability.find(d => d.date === this.bookingForm.date);
            return day || { morning_slots: [], evening_slots: [] };
        }
    },

    async created() {
        await this.loadDepartment();
    },

    mounted() {
        const modalEl = document.getElementById('bookingModal');
        if (modalEl) {
            this.bookingModalInstance = new bootstrap.Modal(modalEl);
        }
    },

    methods: {
        async loadDepartment() {
            this.loading = true;
            const deptId = this.$route.params.id;
            const response = await patientService.getDepartmentDetails(deptId);
            if (response.success) {
                this.department = response.department;
                this.doctors = response.doctors;
            }
            this.loading = false;
        },

        async selectDoctor(doctor) {
            this.selectedDoctor = doctor;
            this.bookingForm = { date: '', time: '', reason: '' };
            this.bookingError = null;

            // Load doctor availability
            const response = await patientService.getDoctorDetails(doctor.id);
            if (response.success) {
                this.availability = response.availability;
            }

            this.bookingModalInstance.show();
        },

        selectDate(day) {
            this.bookingForm.date = day.date;
            this.bookingForm.time = '';
        },

        formatDateShort(dateStr) {
            const date = new Date(dateStr);
            return date.getDate();
        },

        async confirmBooking() {
            if (!this.bookingForm.date || !this.bookingForm.time) return;

            this.booking = true;
            this.bookingError = null;

            const response = await patientService.bookAppointment({
                doctor_id: this.selectedDoctor.id,
                appointment_date: this.bookingForm.date,
                appointment_time: this.bookingForm.time,
                reason: this.bookingForm.reason
            });

            if (response.success) {
                this.bookingModalInstance.hide();
                alert('Appointment booked successfully!');
                this.$router.push('/patient/appointments');
            } else {
                this.bookingError = response.message || 'Failed to book appointment';
            }
            this.booking = false;
        }
    }
};

window.DepartmentDetails = DepartmentDetails;
