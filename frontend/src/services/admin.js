// Admin service - handles admin API calls

const adminService = {
    // Dashboard
    async getDashboardStats() {
        return await api.get('/admin/dashboard/stats');
    },

    // Doctors
    async getDoctors(params = {}) {
        const queryParams = new URLSearchParams();
        if (params.search) queryParams.append('search', params.search);
        if (params.department_id) queryParams.append('department_id', params.department_id);
        if (params.include_inactive) queryParams.append('include_inactive', 'true');

        const query = queryParams.toString();
        return await api.get(`/admin/doctors${query ? '?' + query : ''}`);
    },

    async getDoctor(doctorId) {
        return await api.get(`/admin/doctors/${doctorId}`);
    },

    async createDoctor(doctorData) {
        return await api.post('/admin/doctors', doctorData);
    },

    async updateDoctor(doctorId, doctorData) {
        return await api.put(`/admin/doctors/${doctorId}`, doctorData);
    },

    async toggleDoctorBlacklist(doctorId, blacklist = true) {
        return await api.post(`/admin/doctors/${doctorId}/blacklist`, { blacklist });
    },

    async deleteDoctor(doctorId) {
        return await api.delete(`/admin/doctors/${doctorId}`);
    },

    // Patients
    async getPatients(params = {}) {
        const queryParams = new URLSearchParams();
        if (params.search) queryParams.append('search', params.search);
        if (params.include_inactive) queryParams.append('include_inactive', 'true');

        const query = queryParams.toString();
        return await api.get(`/admin/patients${query ? '?' + query : ''}`);
    },

    async getPatient(patientId) {
        return await api.get(`/admin/patients/${patientId}`);
    },

    async updatePatient(patientId, patientData) {
        return await api.put(`/admin/patients/${patientId}`, patientData);
    },

    async togglePatientBlacklist(patientId, blacklist = true) {
        return await api.post(`/admin/patients/${patientId}/blacklist`, { blacklist });
    },

    async getPatientAppointments(patientId, params = {}) {
        const queryParams = new URLSearchParams();
        if (params.status) queryParams.append('status', params.status);
        const query = queryParams.toString();
        return await api.get(`/admin/patients/${patientId}/appointments${query ? '?' + query : ''}`);
    },

    async getPatientTreatments(patientId) {
        return await api.get(`/admin/patients/${patientId}/treatments`);
    },

    async getTreatment(treatmentId) {
        return await api.get(`/admin/treatments/${treatmentId}`);
    },

    // Appointments
    async getAppointments(params = {}) {
        const queryParams = new URLSearchParams();
        if (params.status) queryParams.append('status', params.status);
        if (params.date) queryParams.append('date', params.date);
        if (params.date_from) queryParams.append('date_from', params.date_from);
        if (params.date_to) queryParams.append('date_to', params.date_to);
        if (params.doctor_id) queryParams.append('doctor_id', params.doctor_id);
        if (params.patient_id) queryParams.append('patient_id', params.patient_id);
        if (params.upcoming) queryParams.append('upcoming', 'true');

        const query = queryParams.toString();
        return await api.get(`/admin/appointments${query ? '?' + query : ''}`);
    },

    async getAppointment(appointmentId) {
        return await api.get(`/admin/appointments/${appointmentId}`);
    },

    async cancelAppointment(appointmentId, reason = '') {
        return await api.post(`/admin/appointments/${appointmentId}/cancel`, { reason });
    },

    async getAppointmentStatusHistory(appointmentId) {
        return await api.get(`/admin/appointments/${appointmentId}/status-history`);
    },

    // Departments
    async getDepartments() {
        return await api.get('/admin/departments');
    },

    async createDepartment(departmentData) {
        return await api.post('/admin/departments', departmentData);
    },

    async updateDepartment(departmentId, departmentData) {
        return await api.put(`/admin/departments/${departmentId}`, departmentData);
    },

    // Charts
    async getChartData(chartType, params = {}) {
        const queryParams = new URLSearchParams();
        if (params.days) queryParams.append('days', params.days);
        const query = queryParams.toString();
        return await api.get(`/admin/charts/${chartType}${query ? '?' + query : ''}`);
    },

    // Payments
    async getAllPayments(params = {}) {
        const queryParams = new URLSearchParams();
        if (params.status) queryParams.append('status', params.status);
        if (params.patient_id) queryParams.append('patient_id', params.patient_id);
        if (params.date_from) queryParams.append('date_from', params.date_from);
        if (params.date_to) queryParams.append('date_to', params.date_to);
        const query = queryParams.toString();
        return await api.get(`/payment/admin/all${query ? '?' + query : ''}`);
    },

    async refundPayment(paymentId, reason = '') {
        return await api.post(`/payment/admin/${paymentId}/refund`, { reason });
    },

    async getPaymentStats() {
        return await api.get('/payment/admin/stats');
    }
};

window.adminService = adminService;
window.AdminService = adminService;
