const AdminCharts = {
    template: `
        <div class="container-fluid">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2><i class="bi bi-bar-chart me-2"></i>Analytics Dashboard</h2>
                <div>
                    <button @click="refreshCharts" class="btn btn-outline-primary me-2" :disabled="loading">
                        <i class="bi bi-arrow-clockwise me-1"></i>Refresh
                    </button>
                    <button @click="downloadMonthlyReport" class="btn btn-primary" :disabled="downloadingReport">
                        <span v-if="downloadingReport" class="spinner-border spinner-border-sm me-1"></span>
                        <i v-else class="bi bi-file-pdf me-1"></i>Monthly Report
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
                            <h5 class="mb-0">Appointments Trend (Last 30 Days)</h5>
                        </div>
                        <div class="card-body">
                            <canvas ref="trendChart" height="300"></canvas>
                        </div>
                    </div>
                </div>

                <div class="col-lg-4">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white">
                            <h5 class="mb-0">Status Distribution</h5>
                        </div>
                        <div class="card-body">
                            <canvas ref="statusChart" height="300"></canvas>
                        </div>
                    </div>
                </div>

                <div class="col-lg-6">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white">
                            <h5 class="mb-0">Appointments by Department</h5>
                        </div>
                        <div class="card-body">
                            <canvas ref="departmentChart" height="300"></canvas>
                        </div>
                    </div>
                </div>

                <div class="col-lg-6">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white">
                            <h5 class="mb-0">Top 10 Doctors by Workload</h5>
                        </div>
                        <div class="card-body">
                            <canvas ref="workloadChart" height="300"></canvas>
                        </div>
                    </div>
                </div>

                <div class="col-lg-6">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white">
                            <h5 class="mb-0">Patient Registrations</h5>
                        </div>
                        <div class="card-body">
                            <canvas ref="registrationsChart" height="300"></canvas>
                        </div>
                    </div>
                </div>

                <div class="col-lg-6">
                    <div class="card shadow-sm">
                        <div class="card-header bg-white">
                            <h5 class="mb-0">Revenue Trend</h5>
                        </div>
                        <div class="card-body">
                            <canvas ref="revenueChart" height="300"></canvas>
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
                const [trend, status, department, workload, registrations, revenue] = await Promise.all([
                    AdminService.getChartData('appointments-trend'),
                    AdminService.getChartData('appointments-by-status'),
                    AdminService.getChartData('appointments-by-department'),
                    AdminService.getChartData('doctor-workload'),
                    AdminService.getChartData('patient-registrations'),
                    AdminService.getChartData('revenue')
                ]);

                // Set loading to false first, then wait for DOM to update
                this.loading = false;

                this.$nextTick(() => {
                    this.createTrendChart(trend.chart_data);
                    this.createStatusChart(status.chart_data);
                    this.createDepartmentChart(department.chart_data);
                    this.createWorkloadChart(workload.chart_data);
                    this.createRegistrationsChart(registrations.chart_data);
                    this.createRevenueChart(revenue.chart_data);
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

        createTrendChart(data) {
            const ctx = this.$refs.trendChart;
            if (!ctx) return;

            this.charts.trend = new Chart(ctx, {
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

        createDepartmentChart(data) {
            const ctx = this.$refs.departmentChart;
            if (!ctx) return;

            this.charts.department = new Chart(ctx, {
                type: 'pie',
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
                        legend: { position: 'right' }
                    }
                }
            });
        },

        createWorkloadChart(data) {
            const ctx = this.$refs.workloadChart;
            if (!ctx) return;

            this.charts.workload = new Chart(ctx, {
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
                    indexAxis: 'y',
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        },

        createRegistrationsChart(data) {
            const ctx = this.$refs.registrationsChart;
            if (!ctx) return;

            this.charts.registrations = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'New Patients',
                        data: data.datasets[0].data,
                        borderColor: '#198754',
                        backgroundColor: 'rgba(25, 135, 84, 0.1)',
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

        createRevenueChart(data) {
            const ctx = this.$refs.revenueChart;
            if (!ctx) return;

            this.charts.revenue = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Revenue ($)',
                        data: data.datasets[0].data,
                        borderColor: '#ffc107',
                        backgroundColor: 'rgba(255, 193, 7, 0.1)',
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

        refreshCharts() {
            this.loadCharts();
        },

        async downloadMonthlyReport() {
            this.downloadingReport = true;
            try {
                const token = localStorage.getItem('access_token');
                const response = await fetch('/api/reports/admin/monthly', {
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
