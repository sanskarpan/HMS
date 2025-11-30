// Doctor service - handles doctor-specific API calls

const doctorService = {
    // Dashboard
    async getDashboardStats() {
        return await api.get('/doctor/dashboard/stats');
    },

    // Appointments
    async getAppointments(params = {}) {
        const queryParams = new URLSearchParams();
        if (params.date) queryParams.append('date', params.date);
        if (params.status) queryParams.append('status', params.status);
        if (params.upcoming) queryParams.append('upcoming', 'true');
        if (params.period) queryParams.append('period', params.period);

        const query = queryParams.toString();
        return await api.get(`/doctor/appointments${query ? '?' + query : ''}`);
    },

    async getAppointment(appointmentId) {
        return await api.get(`/doctor/appointments/${appointmentId}`);
    },

    async completeAppointment(appointmentId, treatmentData) {
        return await api.post(`/doctor/appointments/${appointmentId}/complete`, treatmentData);
    },

    async cancelAppointment(appointmentId, reason = '') {
        return await api.post(`/doctor/appointments/${appointmentId}/cancel`, { reason });
    },

    async markNoShow(appointmentId) {
        return await api.post(`/doctor/appointments/${appointmentId}/no-show`, {});
    },

    // Patients
    async getPatients(search = '') {
        const query = search ? `?search=${encodeURIComponent(search)}` : '';
        return await api.get(`/doctor/patients${query}`);
    },

    async getPatient(patientId) {
        return await api.get(`/doctor/patients/${patientId}`);
    },

    async getPatientHistory(patientId) {
        return await api.get(`/doctor/patients/${patientId}/history`);
    },

    // Treatments
    async getTreatment(treatmentId) {
        return await api.get(`/doctor/treatments/${treatmentId}`);
    },

    async updateTreatment(treatmentId, treatmentData) {
        return await api.put(`/doctor/treatments/${treatmentId}`, treatmentData);
    },

    // Availability
    async getAvailability() {
        return await api.get('/doctor/availability');
    },

    async setAvailability(availabilityData) {
        return await api.post('/doctor/availability', availabilityData);
    },

    async setBulkAvailability(slots) {
        return await api.post('/doctor/availability/bulk', { slots });
    },

    // Profile
    async getProfile() {
        return await api.get('/doctor/profile');
    },

    async updateProfile(profileData) {
        return await api.put('/doctor/profile', profileData);
    },

    // Charts
    async getChartData(chartType, params = {}) {
        const queryParams = new URLSearchParams();
        if (params.weeks) queryParams.append('weeks', params.weeks);
        if (params.months) queryParams.append('months', params.months);
        const query = queryParams.toString();
        return await api.get(`/doctor/charts/${chartType}${query ? '?' + query : ''}`);
    }
};

window.doctorService = doctorService;
window.DoctorService = doctorService;
