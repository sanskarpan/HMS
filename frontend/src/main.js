// Main Vue app setup

const { createApp } = Vue;

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

const app = createApp(AppComponent);

app.component('navbar', Navbar);
app.component('app-component', AppComponent);

app.use(router);
app.mount('#app');

console.log('Hospital Management System initialized');
