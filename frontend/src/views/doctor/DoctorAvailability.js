const DoctorAvailability = {
    name: 'DoctorAvailability',

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
                            <li class="breadcrumb-item active">Availability</li>
                        </ol>
                    </nav>
                    <h2><i class="bi bi-clock"></i> My Availability</h2>
                    <p class="text-muted">Set your availability for the next 7 days</p>
                </div>
            </div>

            <!-- Loading -->
            <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>

            <!-- Availability Grid -->
            <div v-else class="row g-4">
                <div v-for="(day, index) in availability" :key="day.date" class="col-md-6 col-lg-4">
                    <div class="card" :class="{'border-success': day.is_available, 'border-secondary': !day.is_available}">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <div>
                                <strong>{{ formatDayName(day.date) }}</strong>
                                <br>
                                <small class="text-muted">{{ formatDate(day.date) }}</small>
                            </div>
                            <div class="form-check form-switch">
                                <input class="form-check-input" type="checkbox" :id="'avail-' + index"
                                       v-model="day.is_available" @change="updateAvailability(day)">
                                <label class="form-check-label" :for="'avail-' + index">
                                    {{ day.is_available ? 'Available' : 'Off' }}
                                </label>
                            </div>
                        </div>
                        <div class="card-body" v-if="day.is_available">
                            <!-- Morning Slot -->
                            <div class="mb-3">
                                <label class="form-label small text-muted">
                                    <i class="bi bi-sunrise"></i> Morning Slot
                                </label>
                                <div class="row g-2">
                                    <div class="col">
                                        <input type="time" class="form-control form-control-sm"
                                               v-model="day.start_time_morning" placeholder="Start">
                                    </div>
                                    <div class="col-auto pt-1">to</div>
                                    <div class="col">
                                        <input type="time" class="form-control form-control-sm"
                                               v-model="day.end_time_morning" placeholder="End">
                                    </div>
                                </div>
                            </div>

                            <!-- Evening Slot -->
                            <div class="mb-3">
                                <label class="form-label small text-muted">
                                    <i class="bi bi-sunset"></i> Evening Slot
                                </label>
                                <div class="row g-2">
                                    <div class="col">
                                        <input type="time" class="form-control form-control-sm"
                                               v-model="day.start_time_evening" placeholder="Start">
                                    </div>
                                    <div class="col-auto pt-1">to</div>
                                    <div class="col">
                                        <input type="time" class="form-control form-control-sm"
                                               v-model="day.end_time_evening" placeholder="End">
                                    </div>
                                </div>
                            </div>

                            <!-- Slot Duration -->
                            <div class="mb-3">
                                <label class="form-label small text-muted">Slot Duration</label>
                                <select class="form-select form-select-sm" v-model="day.slot_duration">
                                    <option :value="15">15 minutes</option>
                                    <option :value="20">20 minutes</option>
                                    <option :value="30">30 minutes</option>
                                    <option :value="45">45 minutes</option>
                                    <option :value="60">60 minutes</option>
                                </select>
                            </div>

                            <!-- Available Slots Preview -->
                            <div v-if="day.morning_slots?.length || day.evening_slots?.length">
                                <small class="text-muted">Available Slots:</small>
                                <div class="d-flex flex-wrap gap-1 mt-1">
                                    <span v-for="slot in day.morning_slots?.slice(0, 4)" :key="'m'+slot"
                                          class="badge bg-light text-dark">{{ slot }}</span>
                                    <span v-for="slot in day.evening_slots?.slice(0, 4)" :key="'e'+slot"
                                          class="badge bg-light text-dark">{{ slot }}</span>
                                    <span v-if="(day.morning_slots?.length || 0) + (day.evening_slots?.length || 0) > 8"
                                          class="badge bg-secondary">+{{ (day.morning_slots?.length || 0) + (day.evening_slots?.length || 0) - 8 }} more</span>
                                </div>
                            </div>

                            <button class="btn btn-primary btn-sm w-100 mt-3" @click="saveDay(day)"
                                    :disabled="day.saving">
                                <span v-if="day.saving" class="spinner-border spinner-border-sm me-1"></span>
                                Save
                            </button>
                        </div>
                        <div class="card-body text-center text-muted" v-else>
                            <i class="bi bi-moon-stars display-6"></i>
                            <p class="mt-2 mb-0">Day Off</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Quick Actions -->
            <div class="card mt-4">
                <div class="card-header">
                    <h5 class="mb-0">Quick Setup</h5>
                </div>
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-3">
                            <label class="form-label">Morning Start</label>
                            <input type="time" class="form-control" v-model="quickSetup.morning_start" value="09:00">
                        </div>
                        <div class="col-md-3">
                            <label class="form-label">Morning End</label>
                            <input type="time" class="form-control" v-model="quickSetup.morning_end" value="13:00">
                        </div>
                        <div class="col-md-3">
                            <label class="form-label">Evening Start</label>
                            <input type="time" class="form-control" v-model="quickSetup.evening_start" value="17:00">
                        </div>
                        <div class="col-md-3">
                            <label class="form-label">Evening End</label>
                            <input type="time" class="form-control" v-model="quickSetup.evening_end" value="21:00">
                        </div>
                    </div>
                    <div class="mt-3">
                        <button class="btn btn-outline-primary me-2" @click="applyToWeekdays">
                            Apply to Weekdays (Mon-Fri)
                        </button>
                        <button class="btn btn-outline-secondary me-2" @click="applyToAll">
                            Apply to All Days
                        </button>
                        <button class="btn btn-success" @click="saveAll" :disabled="savingAll">
                            <span v-if="savingAll" class="spinner-border spinner-border-sm me-1"></span>
                            Save All Changes
                        </button>
                    </div>
                </div>
            </div>

            <!-- Toast -->
            <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 1100">
                <div class="toast align-items-center text-white border-0" :class="toastClass"
                     :class="{'show': showToast}">
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
            availability: [],
            loading: true,
            savingAll: false,
            quickSetup: {
                morning_start: '09:00',
                morning_end: '13:00',
                evening_start: '17:00',
                evening_end: '21:00',
                slot_duration: 30
            },
            showToast: false,
            toastMessage: '',
            toastClass: 'bg-success'
        };
    },

    async created() {
        await this.loadAvailability();
    },

    methods: {
        async loadAvailability() {
            this.loading = true;
            const response = await doctorService.getAvailability();
            if (response.success) {
                this.availability = response.availability.map(day => ({
                    ...day,
                    saving: false,
                    slot_duration: day.slot_duration || 30
                }));
            }
            this.loading = false;
        },

        formatDayName(dateStr) {
            return new Date(dateStr).toLocaleDateString('en-US', { weekday: 'long' });
        },

        formatDate(dateStr) {
            return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        },

        async updateAvailability(day) {
            // Just toggle, actual save happens on button click
        },

        async saveDay(day) {
            day.saving = true;
            const response = await doctorService.setAvailability({
                date: day.date,
                is_available: day.is_available,
                start_time_morning: day.start_time_morning,
                end_time_morning: day.end_time_morning,
                start_time_evening: day.start_time_evening,
                end_time_evening: day.end_time_evening,
                slot_duration: day.slot_duration
            });

            if (response.success) {
                this.showToastMessage('Availability saved', 'bg-success');
                // Update slots preview
                if (response.availability) {
                    day.morning_slots = response.availability.morning_slots;
                    day.evening_slots = response.availability.evening_slots;
                }
            } else {
                this.showToastMessage(response.message || 'Failed to save', 'bg-danger');
            }
            day.saving = false;
        },

        applyToWeekdays() {
            this.availability.forEach(day => {
                const dayOfWeek = new Date(day.date).getDay();
                // Monday = 1, Friday = 5
                if (dayOfWeek >= 1 && dayOfWeek <= 5) {
                    day.is_available = true;
                    day.start_time_morning = this.quickSetup.morning_start;
                    day.end_time_morning = this.quickSetup.morning_end;
                    day.start_time_evening = this.quickSetup.evening_start;
                    day.end_time_evening = this.quickSetup.evening_end;
                    day.slot_duration = this.quickSetup.slot_duration;
                } else {
                    day.is_available = false;
                }
            });
            this.showToastMessage('Applied to weekdays - click Save All to confirm', 'bg-info');
        },

        applyToAll() {
            this.availability.forEach(day => {
                day.is_available = true;
                day.start_time_morning = this.quickSetup.morning_start;
                day.end_time_morning = this.quickSetup.morning_end;
                day.start_time_evening = this.quickSetup.evening_start;
                day.end_time_evening = this.quickSetup.evening_end;
                day.slot_duration = this.quickSetup.slot_duration;
            });
            this.showToastMessage('Applied to all days - click Save All to confirm', 'bg-info');
        },

        async saveAll() {
            this.savingAll = true;
            const slots = this.availability.map(day => ({
                date: day.date,
                is_available: day.is_available,
                start_time_morning: day.start_time_morning,
                end_time_morning: day.end_time_morning,
                start_time_evening: day.start_time_evening,
                end_time_evening: day.end_time_evening,
                slot_duration: day.slot_duration
            }));

            const response = await doctorService.setBulkAvailability(slots);

            if (response.success) {
                this.showToastMessage('All availability saved successfully', 'bg-success');
                await this.loadAvailability(); // Refresh to get updated slots
            } else {
                this.showToastMessage(response.message || 'Failed to save', 'bg-danger');
            }
            this.savingAll = false;
        },

        showToastMessage(msg, cls) {
            this.toastMessage = msg;
            this.toastClass = cls;
            this.showToast = true;
            setTimeout(() => { this.showToast = false; }, 3000);
        }
    }
};

window.DoctorAvailability = DoctorAvailability;
