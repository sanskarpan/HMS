/**
 * Admin Service for Hospital Management System.
 * Provides methods for admin-specific API operations.
 * Reuses the base api object for DRY implementation.
 */

const adminService = {
    // ========================================================================
    // Dashboard
    // ========================================================================

    /**
     * Get dashboard statistics.
     */
    async getDashboardStats() {
        return await api.get('/admin/dashboard/stats');
    },

    // ========================================================================
    // Doctor Management
    // ========================================================================

    /**
     * Get all doctors with optional filters.
     */
    async getDoctors(params = {}) {
        const queryParams = new URLSearchParams();
        if (params.search) queryParams.append('search', params.search);
        if (params.department_id) queryParams.append('department_id', params.department_id);
        if (params.include_inactive) queryParams.append('include_inactive', 'true');

        const query = queryParams.toString();
        return await api.get(`/admin/doctors${query ? '?' + query : ''}`);
    },

    /**
     * Get a specific doctor by ID.
     */
    async getDoctor(doctorId) {
        return await api.get(`/admin/doctors/${doctorId}`);
    },

    /**
     * Create a new doctor.
     */
    async createDoctor(doctorData) {
        return await api.post('/admin/doctors', doctorData);
    },

    /**
     * Update a doctor.
     */
    async updateDoctor(doctorId, doctorData) {
        return await api.put(`/admin/doctors/${doctorId}`, doctorData);
    },

    /**
     * Blacklist or unblacklist a doctor.
     */
    async toggleDoctorBlacklist(doctorId, blacklist = true) {
        return await api.post(`/admin/doctors/${doctorId}/blacklist`, { blacklist });
    },

    /**
     * Delete (deactivate) a doctor.
     */
    async deleteDoctor(doctorId) {
        return await api.delete(`/admin/doctors/${doctorId}`);
    },

    // ========================================================================
    // Patient Management
    // ========================================================================

    /**
     * Get all patients with optional filters.
     */
    async getPatients(params = {}) {
        const queryParams = new URLSearchParams();
        if (params.search) queryParams.append('search', params.search);
        if (params.include_inactive) queryParams.append('include_inactive', 'true');

        const query = queryParams.toString();
        return await api.get(`/admin/patients${query ? '?' + query : ''}`);
    },

    /**
     * Get a specific patient by ID.
     */
    async getPatient(patientId) {
        return await api.get(`/admin/patients/${patientId}`);
    },

    /**
     * Update a patient.
     */
    async updatePatient(patientId, patientData) {
        return await api.put(`/admin/patients/${patientId}`, patientData);
    },

    /**
     * Blacklist or unblacklist a patient.
     */
    async togglePatientBlacklist(patientId, blacklist = true) {
        return await api.post(`/admin/patients/${patientId}/blacklist`, { blacklist });
    },

    /**
     * Get patient's appointment history.
     */
    async getPatientAppointments(patientId, params = {}) {
        const queryParams = new URLSearchParams();
        if (params.status) queryParams.append('status', params.status);
        const query = queryParams.toString();
        return await api.get(`/admin/patients/${patientId}/appointments${query ? '?' + query : ''}`);
    },

    /**
     * Get patient's treatment records.
     */
    async getPatientTreatments(patientId) {
        return await api.get(`/admin/patients/${patientId}/treatments`);
    },

    /**
     * Get a specific treatment record.
     */
    async getTreatment(treatmentId) {
        return await api.get(`/admin/treatments/${treatmentId}`);
    },

    // ========================================================================
    // Appointment Management
    // ========================================================================

    /**
     * Get all appointments with optional filters.
     */
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

    /**
     * Get a specific appointment by ID.
     */
    async getAppointment(appointmentId) {
        return await api.get(`/admin/appointments/${appointmentId}`);
    },

    /**
     * Cancel an appointment.
     */
    async cancelAppointment(appointmentId, reason = '') {
        return await api.post(`/admin/appointments/${appointmentId}/cancel`, { reason });
    },

    /**
     * Get appointment status change history.
     */
    async getAppointmentStatusHistory(appointmentId) {
        return await api.get(`/admin/appointments/${appointmentId}/status-history`);
    },

    // ========================================================================
    // Department Management
    // ========================================================================

    /**
     * Get all departments.
     */
    async getDepartments() {
        return await api.get('/admin/departments');
    },

    /**
     * Create a new department.
     */
    async createDepartment(departmentData) {
        return await api.post('/admin/departments', departmentData);
    },

    /**
     * Update a department.
     */
    async updateDepartment(departmentId, departmentData) {
        return await api.put(`/admin/departments/${departmentId}`, departmentData);
    }
};

// Make service available globally
window.adminService = adminService;
