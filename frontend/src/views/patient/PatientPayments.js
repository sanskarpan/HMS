const PatientPayments = {
    template: `
        <div class="container-fluid">
            <h2 class="mb-4"><i class="bi bi-credit-card me-2"></i>Payments</h2>

            <ul class="nav nav-tabs mb-4">
                <li class="nav-item">
                    <a class="nav-link" :class="{ active: activeTab === 'pending' }"
                       href="#" @click.prevent="activeTab = 'pending'">
                        Pending Payments
                        <span v-if="pendingPayments.length" class="badge bg-warning ms-1">
                            {{ pendingPayments.length }}
                        </span>
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" :class="{ active: activeTab === 'history' }"
                       href="#" @click.prevent="activeTab = 'history'">
                        Payment History
                    </a>
                </li>
            </ul>

            <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>

            <div v-else-if="activeTab === 'pending'">
                <div v-if="pendingPayments.length === 0" class="alert alert-success">
                    <i class="bi bi-check-circle me-2"></i>
                    No pending payments. All your appointments are paid.
                </div>

                <div v-else class="row g-4">
                    <div v-for="payment in pendingPayments" :key="payment.id" class="col-md-6">
                        <div class="card shadow-sm">
                            <div class="card-header bg-warning text-dark">
                                <strong>Payment Due</strong>
                            </div>
                            <div class="card-body">
                                <h5 class="card-title">\${{ payment.amount.toFixed(2) }}</h5>
                                <p class="text-muted mb-2">
                                    <i class="bi bi-calendar me-1"></i>
                                    {{ formatDate(payment.appointment && payment.appointment.date ? payment.appointment.date : '') }} at {{ payment.appointment && payment.appointment.time ? payment.appointment.time : '' }}
                                </p>
                                <p class="text-muted mb-3">
                                    <i class="bi bi-person me-1"></i>
                                    Dr. {{ payment.appointment && payment.appointment.doctor_name ? payment.appointment.doctor_name : 'N/A' }}
                                </p>
                                <button class="btn btn-success w-100"
                                        @click="openPaymentModal(payment)">
                                    <i class="bi bi-credit-card me-1"></i>Pay Now
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div v-else-if="activeTab === 'history'">
                <div v-if="paymentHistory.length === 0" class="alert alert-info">
                    No payment history found.
                </div>

                <div v-else class="table-responsive">
                    <table class="table table-hover">
                        <thead class="table-light">
                            <tr>
                                <th>Date</th>
                                <th>Appointment</th>
                                <th>Amount</th>
                                <th>Method</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="payment in paymentHistory" :key="payment.id">
                                <td>{{ formatDate(payment.paid_at || payment.created_at) }}</td>
                                <td>
                                    {{ formatDate(payment.appointment && payment.appointment.date ? payment.appointment.date : '') }}<br>
                                    <small class="text-muted">Dr. {{ payment.appointment && payment.appointment.doctor_name ? payment.appointment.doctor_name : 'N/A' }}</small>
                                </td>
                                <td>\${{ payment.amount.toFixed(2) }}</td>
                                <td>
                                    <span class="badge bg-secondary">{{ payment.payment_method }}</span>
                                    <small v-if="payment.card_last_four" class="ms-1">
                                        **** {{ payment.card_last_four }}
                                    </small>
                                </td>
                                <td>
                                    <span class="badge" :class="getStatusClass(payment.status)">
                                        {{ payment.status }}
                                    </span>
                                </td>
                                <td>
                                    <button v-if="payment.status === 'completed'"
                                            @click="downloadReceipt(payment.id)"
                                            class="btn btn-sm btn-outline-primary">
                                        <i class="bi bi-receipt"></i> Receipt
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="modal fade" id="paymentModal" tabindex="-1" ref="paymentModal">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header bg-primary text-white">
                            <h5 class="modal-title">Make Payment</h5>
                            <button type="button" class="btn-close btn-close-white"
                                    data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div v-if="selectedPayment" class="mb-4">
                                <div class="d-flex justify-content-between mb-2">
                                    <span>Amount Due:</span>
                                    <strong class="text-primary">\${{ selectedPayment && selectedPayment.amount ? selectedPayment.amount.toFixed(2) : '0.00' }}</strong>
                                </div>
                                <div class="d-flex justify-content-between mb-2">
                                    <span>Appointment:</span>
                                    <span>{{ formatDate(selectedPayment.appointment && selectedPayment.appointment.date ? selectedPayment.appointment.date : '') }}</span>
                                </div>
                                <div class="d-flex justify-content-between">
                                    <span>Doctor:</span>
                                    <span>Dr. {{ selectedPayment.appointment && selectedPayment.appointment.doctor_name ? selectedPayment.appointment.doctor_name : 'N/A' }}</span>
                                </div>
                            </div>

                            <hr>

                            <div class="mb-3">
                                <label class="form-label">Payment Method</label>
                                <select v-model="paymentForm.method" class="form-select">
                                    <option value="card">Credit/Debit Card</option>
                                    <option value="cash">Cash (Pay at Reception)</option>
                                    <option value="insurance">Insurance</option>
                                </select>
                            </div>

                            <div v-if="paymentForm.method === 'card'">
                                <div class="mb-3">
                                    <label class="form-label">Card Number</label>
                                    <input type="text" v-model="paymentForm.cardNumber"
                                           class="form-control" placeholder="4111 1111 1111 1111"
                                           maxlength="19" @input="formatCardNumber">
                                </div>
                                <div class="row">
                                    <div class="col-6 mb-3">
                                        <label class="form-label">Expiry</label>
                                        <input type="text" v-model="paymentForm.expiry"
                                               class="form-control" placeholder="MM/YY"
                                               maxlength="5">
                                    </div>
                                    <div class="col-6 mb-3">
                                        <label class="form-label">CVV</label>
                                        <input type="text" v-model="paymentForm.cvv"
                                               class="form-control" placeholder="123"
                                               maxlength="4">
                                    </div>
                                </div>
                                <div class="alert alert-info small">
                                    <i class="bi bi-info-circle me-1"></i>
                                    This is a demo payment system. Use any valid-format card number.
                                </div>
                            </div>

                            <div v-if="paymentForm.method === 'insurance'">
                                <div class="mb-3">
                                    <label class="form-label">Insurance Provider ID</label>
                                    <input type="text" v-model="paymentForm.insuranceId"
                                           class="form-control" placeholder="INS-12345">
                                </div>
                            </div>

                            <div v-if="paymentForm.method === 'cash'" class="alert alert-warning">
                                <i class="bi bi-exclamation-triangle me-1"></i>
                                Please pay at the reception desk before your appointment.
                            </div>

                            <div v-if="paymentError" class="alert alert-danger">
                                {{ paymentError }}
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                Cancel
                            </button>
                            <button type="button" class="btn btn-success"
                                    @click="processPayment" :disabled="processing">
                                <span v-if="processing">
                                    <span class="spinner-border spinner-border-sm me-1"></span>
                                    Processing...
                                </span>
                                <span v-else>
                                    <i class="bi bi-check-lg me-1"></i>Pay \${{ selectedPayment && selectedPayment.amount ? selectedPayment.amount.toFixed(2) : '0.00' }}
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
            activeTab: 'pending',
            pendingPayments: [],
            paymentHistory: [],
            selectedPayment: null,
            paymentForm: {
                method: 'card',
                cardNumber: '',
                expiry: '',
                cvv: '',
                insuranceId: ''
            },
            processing: false,
            paymentError: null,
            modal: null
        };
    },

    mounted() {
        this.loadPayments();
        this.modal = new bootstrap.Modal(this.$refs.paymentModal);
    },

    methods: {
        async loadPayments() {
            this.loading = true;
            this.error = null;

            try {
                const [pending, history] = await Promise.all([
                    PatientService.getPendingPayments(),
                    PatientService.getPaymentHistory()
                ]);

                this.pendingPayments = pending.payments || [];
                this.paymentHistory = history.payments || [];
            } catch (err) {
                this.error = 'Failed to load payments: ' + (err.message || 'Unknown error');
            } finally {
                this.loading = false;
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

        openPaymentModal(payment) {
            this.selectedPayment = payment;
            this.paymentForm = {
                method: 'card',
                cardNumber: '',
                expiry: '',
                cvv: '',
                insuranceId: ''
            };
            this.paymentError = null;
            this.modal.show();
        },

        formatCardNumber(e) {
            let value = e.target.value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
            let formatted = '';
            for (let i = 0; i < value.length; i++) {
                if (i > 0 && i % 4 === 0) formatted += ' ';
                formatted += value[i];
            }
            this.paymentForm.cardNumber = formatted;
        },

        async processPayment() {
            this.processing = true;
            this.paymentError = null;

            try {
                const payload = {
                    payment_id: this.selectedPayment.id,
                    payment_method: this.paymentForm.method
                };

                if (this.paymentForm.method === 'card') {
                    if (!this.paymentForm.cardNumber || this.paymentForm.cardNumber.replace(/\s/g, '').length < 13) {
                        throw new Error('Please enter a valid card number');
                    }
                    payload.card_number = this.paymentForm.cardNumber.replace(/\s/g, '');
                }

                if (this.paymentForm.method === 'insurance') {
                    payload.insurance_id = this.paymentForm.insuranceId;
                }

                const result = await PatientService.processPayment(payload);

                if (result.success) {
                    this.modal.hide();
                    await this.loadPayments();
                    alert('Payment successful! Transaction ID: ' + ((result.payment && result.payment.transaction_id) || 'N/A'));
                } else {
                    this.paymentError = result.message || 'Payment failed';
                }
            } catch (err) {
                this.paymentError = err.message || 'Payment failed';
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
