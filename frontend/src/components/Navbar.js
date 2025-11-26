/**
 * Navbar Component
 * Displays navigation bar with user info and logout button when authenticated.
 */

const Navbar = {
    name: 'Navbar',

    

    computed: {
        isAuthenticated() {
            return authService.isAuthenticated();
        },
        isAdmin() {
            return authService.isAdmin();
        },
        isDoctor() {
            return authService.isDoctor();
        },
        isPatient() {
            return authService.isPatient();
        },
        user() {
            return authService.getUser();
        },
        userName() {
            return this.user ? this.user.username : '';
        },
        userRole() {
            return this.user ? this.user.role : '';
        },
        profileRoute() {
            const role = authService.getRole();
            return `/${role}/profile`;
        }
    },

    methods: {
        async logout() {
            await authService.logout();
            this.$router.push('/login');
        }
    }
};

// Make component available globally
window.Navbar = Navbar;
