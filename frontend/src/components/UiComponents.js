/**
 * Reusable UI Components
 * Provides consistent loading states, empty states, error states, and toast notifications.
 */

// Loading Spinner Component
const LoadingSpinner = {
    name: 'LoadingSpinner',
    props: {
        size: {
            type: String,
            default: 'md', // sm, md, lg
            validator: value => ['sm', 'md', 'lg'].includes(value)
        },
        text: {
            type: String,
            default: 'Loading...'
        },
        overlay: {
            type: Boolean,
            default: false
        }
    },
    computed: {
        spinnerClass() {
            const sizeMap = {
                sm: 'spinner-border-sm',
                md: '',
                lg: 'spinner-border'
            };
            return sizeMap[this.size];
        }
    },
    template: `
        <div :class="overlay ? 'loading-overlay' : 'text-center py-4'">
            <div v-if="overlay" class="loading-spinner"></div>
            <div v-else class="spinner-border text-primary" :class="spinnerClass" role="status">
                <span class="visually-hidden">{{ text }}</span>
            </div>
            <p v-if="text && !overlay" class="mt-2 text-muted">{{ text }}</p>
            <p v-if="text && overlay" class="loading-text">{{ text }}</p>
        </div>
    `
};

// Empty State Component
const EmptyState = {
    name: 'EmptyState',
    props: {
        icon: {
            type: String,
            default: 'bi-inbox'
        },
        title: {
            type: String,
            default: 'No data found'
        },
        message: {
            type: String,
            default: ''
        },
        actionText: {
            type: String,
            default: ''
        },
        actionIcon: {
            type: String,
            default: 'bi-plus-circle'
        }
    },
    emits: ['action'],
    template: `
        <div class="empty-state">
            <div class="empty-state-icon">
                <i :class="['bi', icon]"></i>
            </div>
            <h5 class="empty-state-title">{{ title }}</h5>
            <p v-if="message" class="empty-state-text">{{ message }}</p>
            <button v-if="actionText"
                    class="btn btn-primary"
                    @click="$emit('action')">
                <i :class="['bi', actionIcon, 'me-2']"></i>
                {{ actionText }}
            </button>
        </div>
    `
};

// Error State Component
const ErrorState = {
    name: 'ErrorState',
    props: {
        title: {
            type: String,
            default: 'Something went wrong'
        },
        message: {
            type: String,
            default: 'An error occurred. Please try again.'
        },
        retryText: {
            type: String,
            default: 'Try Again'
        },
        showRetry: {
            type: Boolean,
            default: true
        }
    },
    emits: ['retry'],
    template: `
        <div class="error-state">
            <div class="error-state-icon">
                <i class="bi bi-exclamation-triangle"></i>
            </div>
            <h5 class="text-danger">{{ title }}</h5>
            <p class="text-muted">{{ message }}</p>
            <button v-if="showRetry"
                    class="btn btn-outline-primary"
                    @click="$emit('retry')">
                <i class="bi bi-arrow-clockwise me-2"></i>
                {{ retryText }}
            </button>
        </div>
    `
};

// Toast Notification Component
const ToastNotification = {
    name: 'ToastNotification',
    props: {
        show: {
            type: Boolean,
            default: false
        },
        message: {
            type: String,
            default: ''
        },
        type: {
            type: String,
            default: 'success',
            validator: value => ['success', 'error', 'warning', 'info'].includes(value)
        },
        duration: {
            type: Number,
            default: 3000
        },
        position: {
            type: String,
            default: 'bottom-right',
            validator: value => ['top-right', 'top-left', 'bottom-right', 'bottom-left'].includes(value)
        }
    },
    emits: ['close'],
    computed: {
        toastClass() {
            const typeMap = {
                success: 'bg-success',
                error: 'bg-danger',
                warning: 'bg-warning text-dark',
                info: 'bg-info text-dark'
            };
            return typeMap[this.type];
        },
        iconClass() {
            const iconMap = {
                success: 'bi-check-circle-fill',
                error: 'bi-x-circle-fill',
                warning: 'bi-exclamation-triangle-fill',
                info: 'bi-info-circle-fill'
            };
            return iconMap[this.type];
        },
        positionClass() {
            const positionMap = {
                'top-right': 'top-0 end-0',
                'top-left': 'top-0 start-0',
                'bottom-right': 'bottom-0 end-0',
                'bottom-left': 'bottom-0 start-0'
            };
            return positionMap[this.position];
        }
    },
    watch: {
        show(newVal) {
            if (newVal && this.duration > 0) {
                setTimeout(() => {
                    this.$emit('close');
                }, this.duration);
            }
        }
    },
    template: `
        <div class="position-fixed p-3" :class="positionClass" style="z-index: 1100">
            <div class="toast align-items-center text-white border-0"
                 :class="[toastClass, {'show': show}]"
                 role="alert"
                 aria-live="assertive"
                 aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body d-flex align-items-center">
                        <i :class="['bi', iconClass, 'me-2']"></i>
                        {{ message }}
                    </div>
                    <button type="button"
                            class="btn-close btn-close-white me-2 m-auto"
                            @click="$emit('close')"
                            aria-label="Close"></button>
                </div>
            </div>
        </div>
    `
};

// Confirm Dialog Component
const ConfirmDialog = {
    name: 'ConfirmDialog',
    props: {
        show: {
            type: Boolean,
            default: false
        },
        title: {
            type: String,
            default: 'Confirm Action'
        },
        message: {
            type: String,
            default: 'Are you sure you want to proceed?'
        },
        confirmText: {
            type: String,
            default: 'Confirm'
        },
        cancelText: {
            type: String,
            default: 'Cancel'
        },
        confirmClass: {
            type: String,
            default: 'btn-primary'
        },
        danger: {
            type: Boolean,
            default: false
        }
    },
    emits: ['confirm', 'cancel'],
    computed: {
        buttonClass() {
            return this.danger ? 'btn-danger' : this.confirmClass;
        }
    },
    template: `
        <div class="modal fade" :class="{'show d-block': show}" tabindex="-1" v-if="show">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i v-if="danger" class="bi bi-exclamation-triangle text-danger me-2"></i>
                            {{ title }}
                        </h5>
                        <button type="button"
                                class="btn-close"
                                @click="$emit('cancel')"
                                aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <p class="mb-0">{{ message }}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button"
                                class="btn btn-secondary"
                                @click="$emit('cancel')">
                            {{ cancelText }}
                        </button>
                        <button type="button"
                                class="btn"
                                :class="buttonClass"
                                @click="$emit('confirm')">
                            {{ confirmText }}
                        </button>
                    </div>
                </div>
            </div>
        </div>
        <div class="modal-backdrop fade show" v-if="show"></div>
    `
};

// Status Badge Component
const StatusBadge = {
    name: 'StatusBadge',
    props: {
        status: {
            type: String,
            required: true
        },
        size: {
            type: String,
            default: 'md',
            validator: value => ['sm', 'md', 'lg'].includes(value)
        }
    },
    computed: {
        badgeClass() {
            const statusMap = {
                'booked': 'bg-primary',
                'completed': 'bg-success',
                'cancelled': 'bg-danger',
                'no_show': 'bg-secondary',
                'active': 'bg-success',
                'inactive': 'bg-secondary',
                'blacklisted': 'bg-danger',
                'pending': 'bg-warning text-dark',
                'approved': 'bg-success',
                'rejected': 'bg-danger'
            };
            return statusMap[this.status.toLowerCase()] || 'bg-secondary';
        },
        sizeClass() {
            const sizeMap = {
                sm: 'badge-sm',
                md: '',
                lg: 'badge-lg'
            };
            return sizeMap[this.size];
        },
        displayStatus() {
            return this.status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        }
    },
    template: `
        <span class="badge" :class="[badgeClass, sizeClass]">
            {{ displayStatus }}
        </span>
    `
};

// Pagination Component
const Pagination = {
    name: 'Pagination',
    props: {
        currentPage: {
            type: Number,
            required: true
        },
        totalPages: {
            type: Number,
            required: true
        },
        maxVisiblePages: {
            type: Number,
            default: 5
        }
    },
    emits: ['page-change'],
    computed: {
        visiblePages() {
            const pages = [];
            const half = Math.floor(this.maxVisiblePages / 2);
            let start = Math.max(1, this.currentPage - half);
            let end = Math.min(this.totalPages, start + this.maxVisiblePages - 1);

            if (end - start + 1 < this.maxVisiblePages) {
                start = Math.max(1, end - this.maxVisiblePages + 1);
            }

            for (let i = start; i <= end; i++) {
                pages.push(i);
            }

            return pages;
        }
    },
    methods: {
        goToPage(page) {
            if (page >= 1 && page <= this.totalPages && page !== this.currentPage) {
                this.$emit('page-change', page);
            }
        }
    },
    template: `
        <nav aria-label="Page navigation" v-if="totalPages > 1">
            <ul class="pagination justify-content-center mb-0">
                <li class="page-item" :class="{'disabled': currentPage === 1}">
                    <a class="page-link" href="#" @click.prevent="goToPage(1)" aria-label="First">
                        <i class="bi bi-chevron-double-left"></i>
                    </a>
                </li>
                <li class="page-item" :class="{'disabled': currentPage === 1}">
                    <a class="page-link" href="#" @click.prevent="goToPage(currentPage - 1)" aria-label="Previous">
                        <i class="bi bi-chevron-left"></i>
                    </a>
                </li>
                <li v-for="page in visiblePages"
                    :key="page"
                    class="page-item"
                    :class="{'active': page === currentPage}">
                    <a class="page-link" href="#" @click.prevent="goToPage(page)">
                        {{ page }}
                    </a>
                </li>
                <li class="page-item" :class="{'disabled': currentPage === totalPages}">
                    <a class="page-link" href="#" @click.prevent="goToPage(currentPage + 1)" aria-label="Next">
                        <i class="bi bi-chevron-right"></i>
                    </a>
                </li>
                <li class="page-item" :class="{'disabled': currentPage === totalPages}">
                    <a class="page-link" href="#" @click.prevent="goToPage(totalPages)" aria-label="Last">
                        <i class="bi bi-chevron-double-right"></i>
                    </a>
                </li>
            </ul>
        </nav>
    `
};

// Search Input Component
const SearchInput = {
    name: 'SearchInput',
    props: {
        modelValue: {
            type: String,
            default: ''
        },
        placeholder: {
            type: String,
            default: 'Search...'
        },
        debounce: {
            type: Number,
            default: 300
        }
    },
    emits: ['update:modelValue', 'search'],
    data() {
        return {
            localValue: this.modelValue,
            debounceTimer: null
        };
    },
    watch: {
        modelValue(newVal) {
            this.localValue = newVal;
        },
        localValue(newVal) {
            clearTimeout(this.debounceTimer);
            this.debounceTimer = setTimeout(() => {
                this.$emit('update:modelValue', newVal);
                this.$emit('search', newVal);
            }, this.debounce);
        }
    },
    methods: {
        clear() {
            this.localValue = '';
            this.$emit('update:modelValue', '');
            this.$emit('search', '');
        }
    },
    template: `
        <div class="input-group">
            <span class="input-group-text bg-white">
                <i class="bi bi-search text-muted"></i>
            </span>
            <input type="text"
                   class="form-control border-start-0"
                   :placeholder="placeholder"
                   v-model="localValue"
                   aria-label="Search">
            <button v-if="localValue"
                    class="btn btn-outline-secondary"
                    type="button"
                    @click="clear"
                    aria-label="Clear search">
                <i class="bi bi-x-lg"></i>
            </button>
        </div>
    `
};

// Export all components
window.LoadingSpinner = LoadingSpinner;
window.EmptyState = EmptyState;
window.ErrorState = ErrorState;
window.ToastNotification = ToastNotification;
window.ConfirmDialog = ConfirmDialog;
window.StatusBadge = StatusBadge;
window.Pagination = Pagination;
window.SearchInput = SearchInput;
