/**
 * Patient Service - API client for patient-related operations
 * Reuses the base api object for DRY implementation
 */

const patientService = {
    // Dashboard & Profile (Ticket 5.1)
    async getDashboardStats() {
        return await api.get('/patient/dashboard/stats');
    },

    async getProfile() {
        return await api.get('/patient/profile');
    },

    async updateProfile(profileData) {
        return await api.put('/patient/profile', profileData);
    },

    // Departments & Doctor Search (Ticket 5.2)
    async getDepartments() {
        return await api.get('/patient/departments');
    },

    async getDepartmentDetails(departmentId) {
        return await api.get(`/patient/departments/${departmentId}`);
    },

    async searchDoctors(params = {}) {
        const queryParams = new URLSearchParams();
        if (params.search) queryParams.append('search', params.search);
        if (params.department_id) queryParams.append('department_id', params.department_id);
        const queryString = queryParams.toString();
        return await api.get(`/patient/doctors${queryString ? '?' + queryString : ''}`);
    },

    async getDoctorDetails(doctorId) {
        return await api.get(`/patient/doctors/${doctorId}`);
    },

    async getDoctorSlots(doctorId, date) {
        return await api.get(`/patient/doctors/${doctorId}/slots?date=${date}`);
    },

    // Appointments (Ticket 5.3)
    async getAppointments(params = {}) {
        const queryParams = new URLSearchParams();
        if (params.status) queryParams.append('status', params.status);
        if (params.period) queryParams.append('period', params.period);
        const queryString = queryParams.toString();
        return await api.get(`/patient/appointments${queryString ? '?' + queryString : ''}`);
    },

    async getAppointmentDetails(appointmentId) {
        return await api.get(`/patient/appointments/${appointmentId}`);
    },

    async bookAppointment(appointmentData) {
        return await api.post('/patient/appointments', appointmentData);
    },

    async cancelAppointment(appointmentId, reason = '') {
        return await api.post(`/patient/appointments/${appointmentId}/cancel`, { reason });
    },

    async rescheduleAppointment(appointmentId, newDate, newTime) {
        return await api.post(`/patient/appointments/${appointmentId}/reschedule`, {
            appointment_date: newDate,
            appointment_time: newTime
        });
    },

    // History & Treatments (Ticket 5.4)
    async getAppointmentHistory() {
        return await api.get('/patient/history');
    },

    async getTreatments() {
        return await api.get('/patient/treatments');
    },

    async getTreatmentDetails(treatmentId) {
        return await api.get(`/patient/treatments/${treatmentId}`);
    },

    // CSV Export (Ticket 7.6, 7.7)
    async triggerExport() {
        return await api.post('/patient/export-history', {});
    },

    async getExportStatus(taskId) {
        return await api.get(`/patient/export-status/${taskId}`);
    },

    getExportDownloadUrl(fileId) {
        return `${api.baseURL}/patient/download-export/${fileId}`;
    },

    async downloadExportDirect() {
        // For synchronous fallback download
        const token = localStorage.getItem('token');
        const response = await fetch(`${api.baseURL}/patient/export-history`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.headers.get('content-type')?.includes('text/csv')) {
            // Synchronous download - return the blob
            const blob = await response.blob();
            return { success: true, blob };
        } else {
            // Async task started
            return await response.json();
        }
    }
};

// Make available globally
window.patientService = patientService;
