/**
 * Main Vue Application Entry Point
 * Initializes Vue app with router and global components.
 */

const { createApp } = Vue;

// Root App Component
const AppComponent = {
    name: 'App',
    template: `
        <div id="app-root">
            <navbar></navbar>
            <router-view></router-view>
        </div>
    `,
    components: {
        'navbar': Navbar
    }
};

// Create Vue application
const app = createApp(AppComponent);

// Register global components
app.component('navbar', Navbar);
app.component('app-component', AppComponent);

// Use router
app.use(router);

// Mount application
app.mount('#app');

console.log('Hospital Management System initialized');
