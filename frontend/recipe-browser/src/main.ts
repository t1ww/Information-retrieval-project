import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

// Import nProgress
import NProgress from 'nprogress';
import 'nprogress/nprogress.css';  // Make sure to include the styles
import '@/style.css'

const app = createApp(App);

// Set up router navigation guards
router.beforeEach((_to, _from, next) => {
  NProgress.start();  // Start the progress bar when navigation begins
  next();
});

router.afterEach(() => {
  NProgress.done();  // Complete the progress bar when navigation finishes
});

app.use(router).mount('#app');
