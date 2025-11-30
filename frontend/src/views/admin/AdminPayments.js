const AdminPayments = {
    template: `
        <div class="container-fluid">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2><i class="bi bi-credit-card me-2"></i>Payment Management</h2>
                <button @click="loadPayments" class="btn btn-outline-primary" :disabled="loading">
                    <i class="bi bi-arrow-clockwise me-1"></i>Refresh
                </button>
            </div>

            <!-- Stats Cards -->
            <div class="row g-3 mb-4">
                <div class="col-md-3">
                    <div class="card bg-success text-white">
                        <div class="card-body">
                            <h6 class="card-title">Total Revenue</h6>
                            <h3 class="mb-0">\${{ (stats.total_revenue && stats.total_revenue.toFixed(2)) || '0.00' }}</h3>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-primary text-white">
                        <div class="card-body">
                            <h6 class="card-title">Completed Payments</h6>
                            <h3 class="mb-0">{{ stats.completed_count || 0 }}</h3>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-warning text-dark">
                        <div class="card-body">
                            <h6 class="card-title">Pending Payments</h6>
                            <h3 class="mb-0">{{ stats.pending_count || 0 }}</h3>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-info text-white">
                        <div class="card-body">
                            <h6 class="card-title">Refunded</h6>
                            <h3 class="mb-0">{{ stats.refunded_count || 0 }}</h3>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Filters -->
            <div class="card shadow-sm mb-4">
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-3">
                            <label class="form-label">Status</label>
                            <select v-model="filters.status" @change="loadPayments" class="form-select">
                                <option value="">All Statuses</option>
                                <option value="pending">Pending</option>
                                <option value="completed">Completed</option>
                                <option value="failed">Failed</option>
                                <option value="refunded">Refunded</option>
                            </select>
                        </div>
                        <div class="col-md-3">
                            <label class="form-label">From Date</label>
                            <input type="date" v-model="filters.date_from" @change="loadPayments" class="form-control">
                        </div>
                        <div class="col-md-3">
                            <label class="form-label">To Date</label>
                            <input type="date" v-model="filters.date_to" @change="loadPayments" class="form-control">
                        </div>
                        <div class="col-md-3 d-flex align-items-end">
                            <button @click="clearFilters" class="btn btn-outline-secondary w-100">
                                <i class="bi bi-x-lg me-1"></i>Clear Filters
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>

            <div v-else-if="payments.length === 0" class="alert alert-info">
                No payments found matching your criteria.
            </div>

            <div v-else class="card shadow-sm">
                <div class="table-responsive">
                    <table class="table table-hover mb-0">
                        <thead class="table-light">
                            <tr>
                                <th>ID</th>
                                <th>Patient</th>
                                <th>Amount</th>
                                <th>Method</th>
                                <th>Date</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="payment in payments" :key="payment.id">
                                <td>#{{ payment.id }}</td>
                                <td>
                                    {{ payment.patient_name }}<br>
                                    <small class="text-muted">Appt: {{ formatDate(payment.appointment_date) }}</small>
                                </td>
                                <td>\${{ payment.amount.toFixed(2) }}</td>
                                <td>
                                    <span class="badge bg-secondary">{{ payment.payment_method }}</span>
                                    <small v-if="payment.card_last_four" class="ms-1">
                                        **** {{ payment.card_last_four }}
                                    </small>
                                </td>
                                <td>{{ formatDate(payment.paid_at || payment.created_at) }}</td>
                                <td>
                                    <span class="badge" :class="getStatusClass(payment.status)">
                                        {{ payment.status }}
                                    </span>
                                </td>
                                <td>
                                    <button v-if="payment.status === 'completed'"
                                            @click="openRefundModal(payment)"
                                            class="btn btn-sm btn-outline-warning">
                                        <i class="bi bi-arrow-return-left"></i> Refund
                                    </button>
                                    <button v-if="payment.status === 'completed'"
                                            @click="downloadReceipt(payment.id)"
                                            class="btn btn-sm btn-outline-primary ms-1">
                                        <i class="bi bi-receipt"></i>
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Refund Modal -->
            <div class="modal fade" id="refundModal" tabindex="-1" ref="refundModal">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header bg-warning text-dark">
                            <h5 class="modal-title">Refund Payment</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div v-if="selectedPayment" class="mb-3">
                                <p><strong>Payment ID:</strong> #{{ selectedPayment.id }}</p>
                                <p><strong>Patient:</strong> {{ selectedPayment.patient_name }}</p>
                                <p><strong>Amount:</strong> \${{ selectedPayment.amount.toFixed(2) }}</p>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Refund Reason</label>
                                <textarea v-model="refundReason" class="form-control" rows="3"
                                          placeholder="Enter reason for refund..."></textarea>
                            </div>
                            <div v-if="refundError" class="alert alert-danger">
                                {{ refundError }}
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                Cancel
                            </button>
                            <button type="button" class="btn btn-warning" @click="processRefund" :disabled="processing">
                                <span v-if="processing">
                                    <span class="spinner-border spinner-border-sm me-1"></span>
                                    Processing...
                                </span>
                                <span v-else>
                                    <i class="bi bi-arrow-return-left me-1"></i>Process Refund
                                </span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div v-if="error" class="alert alert-danger mt-3">
                {{ error }}
            </div>
        </div>
    `,

    data() {
        return {
            loading: false,
            error: null,
            payments: [],
            stats: {},
            filters: {
                status: '',
                date_from: '',
                date_to: ''
            },
            selectedPayment: null,
            refundReason: '',
            refundError: null,
            processing: false,
            modal: null
        };
    },

    mounted() {
        this.loadPayments();
        this.loadStats();
        this.modal = new bootstrap.Modal(this.$refs.refundModal);
    },

    methods: {
        async loadPayments() {
            this.loading = true;
            this.error = null;

            try {
                const result = await AdminService.getAllPayments(this.filters);
                this.payments = result.payments || [];
            } catch (err) {
                this.error = 'Failed to load payments: ' + (err.message || 'Unknown error');
            } finally {
                this.loading = false;
            }
        },

        async loadStats() {
            try {
                const result = await AdminService.getPaymentStats();
                this.stats = result.stats || {};
            } catch (err) {
                console.error('Failed to load payment stats:', err);
            }
        },

        formatDate(dateStr) {
            if (!dateStr) return 'N/A';
            const date = new Date(dateStr);
            return date.toLocaleDateString();
        },

        getStatusClass(status) {
            switch (status) {
                case 'completed': return 'bg-success';
                case 'pending': return 'bg-warning text-dark';
                case 'failed': return 'bg-danger';
                case 'refunded': return 'bg-info';
                default: return 'bg-secondary';
            }
        },

        clearFilters() {
            this.filters = {
                status: '',
                date_from: '',
                date_to: ''
            };
            this.loadPayments();
        },

        openRefundModal(payment) {
            this.selectedPayment = payment;
            this.refundReason = '';
            this.refundError = null;
            this.modal.show();
        },

        async processRefund() {
            this.processing = true;
            this.refundError = null;

            try {
                const result = await AdminService.refundPayment(this.selectedPayment.id, this.refundReason);

                if (result.success) {
                    this.modal.hide();
                    await this.loadPayments();
                    await this.loadStats();
                    alert('Refund processed successfully');
                } else {
                    this.refundError = result.message || 'Refund failed';
                }
            } catch (err) {
                this.refundError = err.message || 'Refund failed';
            } finally {
                this.processing = false;
            }
        },

        async downloadReceipt(paymentId) {
            try {
                const token = localStorage.getItem('access_token');
                const response = await fetch('/api/reports/patient/receipt/' + paymentId, {
                    headers: {
                        'Authorization': 'Bearer ' + token
                    }
                });

                if (!response.ok) {
                    throw new Error('Failed to generate receipt');
                }

                // Get HTML content and open in new window for printing
                const html = await response.text();
                const printWindow = window.open('', '_blank');
                printWindow.document.write(html);
                printWindow.document.close();
            } catch (err) {
                this.error = 'Failed to download receipt: ' + err.message;
            }
        }
    }
};
