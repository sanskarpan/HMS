/**
 * Doctor Service for Hospital Management System.
 * Provides methods for doctor-specific API operations.
 * Reuses the base api object for DRY implementation.
 */

const doctorService = {
    // ========================================================================
    // Dashboard
    // ========================================================================

    /**
     * Get dashboard statistics.
     */
    async getDashboardStats() {
        return await api.get('/doctor/dashboard/stats');
    },

    // ========================================================================
    // Appointments
    // ========================================================================

    /**
     * Get appointments with optional filters.
     */
    async getAppointments(params = {}) {
        const queryParams = new URLSearchParams();
        if (params.date) queryParams.append('date', params.date);
        if (params.status) queryParams.append('status', params.status);
        if (params.upcoming) queryParams.append('upcoming', 'true');
        if (params.period) queryParams.append('period', params.period);

        const query = queryParams.toString();
        return await api.get(`/doctor/appointments${query ? '?' + query : ''}`);
    },

    /**
     * Get a specific appointment.
     */
    async getAppointment(appointmentId) {
        return await api.get(`/doctor/appointments/${appointmentId}`);
    },

    /**
     * Complete an appointment with treatment details.
     */
    async completeAppointment(appointmentId, treatmentData) {
        return await api.post(`/doctor/appointments/${appointmentId}/complete`, treatmentData);
    },

    /**
     * Cancel an appointment.
     */
    async cancelAppointment(appointmentId, reason = '') {
        return await api.post(`/doctor/appointments/${appointmentId}/cancel`, { reason });
    },

    /**
     * Mark appointment as no-show.
     */
    async markNoShow(appointmentId) {
        return await api.post(`/doctor/appointments/${appointmentId}/no-show`, {});
    },

    // ========================================================================
    // Patients
    // ========================================================================

    /**
     * Get list of assigned patients.
     */
    async getPatients(search = '') {
        const query = search ? `?search=${encodeURIComponent(search)}` : '';
        return await api.get(`/doctor/patients${query}`);
    },

    /**
     * Get patient details.
     */
    async getPatient(patientId) {
        return await api.get(`/doctor/patients/${patientId}`);
    },

    /**
     * Get patient's full treatment history.
     */
    async getPatientHistory(patientId) {
        return await api.get(`/doctor/patients/${patientId}/history`);
    },

    // ========================================================================
    // Treatments
    // ========================================================================

    /**
     * Get a treatment record.
     */
    async getTreatment(treatmentId) {
        return await api.get(`/doctor/treatments/${treatmentId}`);
    },

    /**
     * Update a treatment record.
     */
    async updateTreatment(treatmentId, treatmentData) {
        return await api.put(`/doctor/treatments/${treatmentId}`, treatmentData);
    },

    // ========================================================================
    // Availability
    // ========================================================================

    /**
     * Get availability for the next 7 days.
     */
    async getAvailability() {
        return await api.get('/doctor/availability');
    },

    /**
     * Set availability for a specific date.
     */
    async setAvailability(availabilityData) {
        return await api.post('/doctor/availability', availabilityData);
    },

    /**
     * Set availability for multiple dates.
     */
    async setBulkAvailability(slots) {
        return await api.post('/doctor/availability/bulk', { slots });
    },

    // ========================================================================
    // Profile
    // ========================================================================

    /**
     * Get doctor's profile.
     */
    async getProfile() {
        return await api.get('/doctor/profile');
    },

    /**
     * Update doctor's profile.
     */
    async updateProfile(profileData) {
        return await api.put('/doctor/profile', profileData);
    }
};

// Make service available globally
window.doctorService = doctorService;
