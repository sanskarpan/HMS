/**
 * Doctor Details View Component
 * Shows doctor profile with 7-day availability and booking.
 */

const DoctorDetails = {
    name: 'DoctorDetails',

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
                                <router-link to="/patient/doctors">Find Doctors</router-link>
                            </li>
                            <li class="breadcrumb-item active">Dr. {{ doctor.full_name }}</li>
                        </ol>
                    </nav>
                </div>
            </div>

            <!-- Loading -->
            <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>

            <div v-else class="row">
                <!-- Doctor Profile -->
                <div class="col-lg-4 mb-4">
                    <div class="card shadow-sm">
                        <div class="card-body text-center">
                            <div class="bg-primary rounded-circle mx-auto mb-3" style="width: 100px; height: 100px; display: flex; align-items: center; justify-content: center;">
                                <i class="bi bi-person-fill display-4 text-white"></i>
                            </div>
                            <h4>Dr. {{ doctor.full_name }}</h4>
                            <p class="text-primary mb-2">{{ doctor.department ? doctor.department.name : 'General Practice' }}</p>
                            <p class="text-muted">{{ doctor.qualification || 'Medical Specialist' }}</p>
                            <hr>
                            <div class="text-start">
                                <p class="mb-2"><i class="bi bi-clock me-2"></i><strong>Experience:</strong> {{ doctor.experience_years || 0 }} years</p>
                                <p class="mb-2"><i class="bi bi-currency-dollar me-2"></i><strong>Consultation Fee:</strong> ${{ doctor.consultation_fee || 'N/A' }}</p>
                                <p class="mb-0"><i class="bi bi-telephone me-2"></i><strong>Phone:</strong> {{ doctor.phone || 'Not available' }}</p>
                            </div>
                            <hr>
                            <p class="text-muted small">{{ doctor.bio || 'Experienced medical professional dedicated to patient care.' }}</p>
                        </div>
                    </div>
                </div>

                <!-- Availability & Booking -->
                <div class="col-lg-8">
                    <div class="card shadow-sm">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="bi bi-calendar-week"></i> Availability (Next 7 Days)</h5>
                        </div>
                        <div class="card-body">
                            <!-- Date Selection -->
                            <div class="d-flex flex-wrap gap-2 mb-4">
                                <button v-for="day in availability" :key="day.date"
                                        type="button" class="btn"
                                        :class="getDateButtonClass(day)"
                                        :disabled="!day.is_available"
                                        @click="selectDate(day)">
                                    <div class="text-center" style="min-width: 60px;">
                                        <small>{{ day.day_name.substring(0, 3) }}</small><br>
                                        <strong>{{ formatDateShort(day.date) }}</strong>
                                    </div>
                                </button>
                            </div>

                            <!-- Selected Date Info -->
                            <div v-if="selectedDate" class="mb-4">
                                <h6 class="text-primary mb-3">
                                    <i class="bi bi-calendar-check"></i>
                                    {{ formatDateFull(selectedDate.date) }}
                                </h6>

                                <!-- Morning Slots -->
                                <div v-if="selectedDate.morning_slots.length > 0" class="mb-3">
                                    <label class="form-label text-muted"><i class="bi bi-sun"></i> Morning</label>
                                    <div class="d-flex flex-wrap gap-2">
                                        <button v-for="slot in selectedDate.morning_slots" :key="slot"
                                                type="button" class="btn btn-sm"
                                                :class="selectedSlot === slot ? 'btn-success' : 'btn-outline-success'"
                                                @click="selectedSlot = slot">
                                            {{ slot }}
                                        </button>
                                    </div>
                                </div>

                                <!-- Evening Slots -->
                                <div v-if="selectedDate.evening_slots.length > 0" class="mb-3">
                                    <label class="form-label text-muted"><i class="bi bi-moon"></i> Evening</label>
                                    <div class="d-flex flex-wrap gap-2">
                                        <button v-for="slot in selectedDate.evening_slots" :key="slot"
                                                type="button" class="btn btn-sm"
                                                :class="selectedSlot === slot ? 'btn-success' : 'btn-outline-success'"
                                                @click="selectedSlot = slot">
                                            {{ slot }}
                                        </button>
                                    </div>
                                </div>

                                <!-- No Slots -->
                                <div v-if="selectedDate.morning_slots.length === 0 && selectedDate.evening_slots.length === 0"
                                     class="alert alert-warning">
                                    <i class="bi bi-exclamation-triangle"></i> All slots are booked for this date
                                </div>
                            </div>

                            <!-- Reason Input -->
                            <div v-if="selectedSlot" class="mb-4">
                                <label class="form-label">Reason for Visit (Optional)</label>
                                <textarea class="form-control" v-model="reason" rows="2"
                                          placeholder="Describe your symptoms or reason for visit"></textarea>
                            </div>

                            <!-- Booking Summary -->
                            <div v-if="selectedDate && selectedSlot" class="alert alert-info">
                                <strong>Booking Summary:</strong><br>
                                <i class="bi bi-person"></i> Dr. {{ doctor.full_name }}<br>
                                <i class="bi bi-calendar"></i> {{ formatDateFull(selectedDate.date) }} at {{ selectedSlot }}<br>
                                <i class="bi bi-currency-dollar"></i> Fee: ${{ doctor.consultation_fee || 'TBD' }}
                            </div>

                            <div v-if="bookingError" class="alert alert-danger">{{ bookingError }}</div>

                            <!-- Book Button -->
                            <button class="btn btn-primary btn-lg w-100" @click="bookAppointment"
                                    :disabled="!selectedDate || !selectedSlot || booking">
                                <span v-if="booking" class="spinner-border spinner-border-sm me-2"></span>
                                <i v-else class="bi bi-calendar-plus me-2"></i>
                                Book Appointment
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,

    data() {
        return {
            doctor: {},
            availability: [],
            selectedDate: null,
            selectedSlot: '',
            reason: '',
            loading: true,
            booking: false,
            bookingError: null
        };
    },

    async created() {
        await this.loadDoctor();
    },

    methods: {
        async loadDoctor() {
            this.loading = true;
            const doctorId = this.$route.params.id;
            const response = await patientService.getDoctorDetails(doctorId);
            if (response.success) {
                this.doctor = response.doctor;
                this.availability = response.availability;
            }
            this.loading = false;
        },

        getDateButtonClass(day) {
            if (!day.is_available) return 'btn-outline-secondary';
            if (this.selectedDate && this.selectedDate.date === day.date) return 'btn-primary';
            return 'btn-outline-primary';
        },

        selectDate(day) {
            this.selectedDate = day;
            this.selectedSlot = '';
        },

        formatDateShort(dateStr) {
            const date = new Date(dateStr);
            return date.getDate();
        },

        formatDateFull(dateStr) {
            const date = new Date(dateStr);
            return date.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
        },

        async bookAppointment() {
            if (!this.selectedDate || !this.selectedSlot) return;

            this.booking = true;
            this.bookingError = null;

            const response = await patientService.bookAppointment({
                doctor_id: this.doctor.id,
                appointment_date: this.selectedDate.date,
                appointment_time: this.selectedSlot,
                reason: this.reason
            });

            if (response.success) {
                alert('Appointment booked successfully!');
                this.$router.push('/patient/appointments');
            } else {
                this.bookingError = response.message || 'Failed to book appointment';
            }
            this.booking = false;
        }
    }
};

window.DoctorDetails = DoctorDetails;
