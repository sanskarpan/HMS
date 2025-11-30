const DoctorCharts = {
    template: `
        <div class="container-fluid">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2><i class="bi bi-bar-chart me-2"></i>My Analytics</h2>
                <div>
                    <button @click="refreshCharts" class="btn btn-outline-primary me-2" :disabled="loading">
                        <i class="bi bi-arrow-clockwise me-1"></i>Refresh
                    </button>
                    <button @click="downloadActivityReport" class="btn btn-primary" :disabled="downloadingReport">
                        <span v-if="downloadingReport" class="spinner-border spinner-border-sm me-1"></span>
                        <i v-else class="bi bi-file-pdf me-1"></i>Activity Report
                    </button>
                </div>
            </div>

            <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2 text-muted">Loading analytics data...</p>
            </div>

            <div v-else class="row g-4">
                <div class="col-lg-8">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white">
                            <h5 class="mb-0">Weekly Appointments Trend</h5>
                        </div>
                        <div class="card-body">
                            <canvas ref="weeklyChart" height="300"></canvas>
                        </div>
                    </div>
                </div>

                <div class="col-lg-4">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white">
                            <h5 class="mb-0">Appointment Status</h5>
                        </div>
                        <div class="card-body">
                            <canvas ref="statusChart" height="300"></canvas>
                        </div>
                    </div>
                </div>

                <div class="col-lg-6">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white">
                            <h5 class="mb-0">Top Patients by Visits</h5>
                        </div>
                        <div class="card-body">
                            <canvas ref="patientsChart" height="300"></canvas>
                        </div>
                    </div>
                </div>

                <div class="col-lg-6">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white">
                            <h5 class="mb-0">Monthly Summary</h5>
                        </div>
                        <div class="card-body">
                            <canvas ref="monthlyChart" height="300"></canvas>
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
            charts: {},
            downloadingReport: false
        };
    },

    mounted() {
        this.loadCharts();
    },

    beforeUnmount() {
        this.destroyCharts();
    },

    methods: {
        async loadCharts() {
            this.loading = true;
            this.error = null;
            this.destroyCharts();

            try {
                const [weekly, status, patients, monthly] = await Promise.all([
                    DoctorService.getChartData('weekly-appointments'),
                    DoctorService.getChartData('appointments-by-status'),
                    DoctorService.getChartData('patient-visits'),
                    DoctorService.getChartData('monthly-summary')
                ]);

                // Set loading to false first, then wait for DOM to update
                this.loading = false;

                this.$nextTick(() => {
                    this.createWeeklyChart(weekly.chart_data);
                    this.createStatusChart(status.chart_data);
                    this.createPatientsChart(patients.chart_data);
                    this.createMonthlyChart(monthly.chart_data);
                });
            } catch (err) {
                this.error = 'Failed to load chart data: ' + (err.message || 'Unknown error');
                this.loading = false;
            }
        },

        destroyCharts() {
            Object.values(this.charts).forEach(chart => {
                if (chart) chart.destroy();
            });
            this.charts = {};
        },

        createWeeklyChart(data) {
            const ctx = this.$refs.weeklyChart;
            if (!ctx) return;

            this.charts.weekly = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Appointments',
                        data: data.datasets[0].data,
                        borderColor: '#0d6efd',
                        backgroundColor: 'rgba(13, 110, 253, 0.1)',
                        fill: true,
                        tension: 0.3
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        },

        createStatusChart(data) {
            const ctx = this.$refs.statusChart;
            if (!ctx) return;

            this.charts.status = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.datasets[0].data,
                        backgroundColor: data.datasets[0].backgroundColor
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'bottom' }
                    }
                }
            });
        },

        createPatientsChart(data) {
            const ctx = this.$refs.patientsChart;
            if (!ctx) return;

            this.charts.patients = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Visits',
                        data: data.datasets[0].data,
                        backgroundColor: '#198754'
                    }]
                },
                options: {
                    responsive: true,
                    indexAxis: 'y',
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        },

        createMonthlyChart(data) {
            const ctx = this.$refs.monthlyChart;
            if (!ctx) return;

            this.charts.monthly = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Appointments',
                        data: data.datasets[0].data,
                        backgroundColor: '#0d6efd'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        },

        refreshCharts() {
            this.loadCharts();
        },

        async downloadActivityReport() {
            this.downloadingReport = true;
            try {
                const token = localStorage.getItem('access_token');
                const response = await fetch('/api/reports/doctor/activity', {
                    headers: {
                        'Authorization': 'Bearer ' + token
                    }
                });

                if (!response.ok) {
                    throw new Error('Failed to generate report');
                }

                // Get HTML content and open in new window for printing
                const html = await response.text();
                const printWindow = window.open('', '_blank');
                printWindow.document.write(html);
                printWindow.document.close();
            } catch (err) {
                this.error = 'Failed to generate report: ' + err.message;
            } finally {
                this.downloadingReport = false;
            }
        }
    }
};
