// Patient service - handles patient API calls

const patientService = {
    // Dashboard & Profile
    async getDashboardStats() {
        return await api.get('/patient/dashboard/stats');
    },

    async getProfile() {
        return await api.get('/patient/profile');
    },

    async updateProfile(profileData) {
        return await api.put('/patient/profile', profileData);
    },

    // Departments & Doctors
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

    // Appointments
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

    // History & Treatments
    async getAppointmentHistory() {
        return await api.get('/patient/history');
    },

    async getTreatments() {
        return await api.get('/patient/treatments');
    },

    async getTreatmentDetails(treatmentId) {
        return await api.get(`/patient/treatments/${treatmentId}`);
    },

    // CSV Export
    async triggerExport(mode = 'email') {
        return await api.post('/patient/export-history', { mode });
    },

    async getExportStatus(taskId) {
        return await api.get(`/patient/export-status/${taskId}`);
    },

    getExportDownloadUrl(fileId) {
        return `/api/patient/download-export/${fileId}`;
    },

    async downloadExportDirect() {
        const token = localStorage.getItem('access_token');
        const response = await fetch('/api/patient/export-history', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ mode: 'download' })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Export failed');
        }

        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('text/csv')) {
            const blob = await response.blob();
            return { success: true, blob };
        } else {
            return await response.json();
        }
    },

    async exportViaEmail() {
        return await api.post('/patient/export-history', { mode: 'email' });
    },

    // Payments
    async getPendingPayments() {
        return await api.get('/payment/pending');
    },

    async getPaymentHistory() {
        return await api.get('/payment/history');
    },

    async initiatePayment(appointmentId) {
        return await api.post('/payment/initiate', { appointment_id: appointmentId });
    },

    async processPayment(paymentData) {
        return await api.post('/payment/process', paymentData);
    }
};

window.patientService = patientService;
window.PatientService = patientService;
