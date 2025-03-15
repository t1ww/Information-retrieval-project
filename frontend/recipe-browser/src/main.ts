import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import NProgress from 'nprogress';
import 'nprogress/nprogress.css';  // Make sure to include the styles
import '@/style.css';

const app = createApp(App);

// Set up router navigation guards
router.beforeEach((_to, _from, next) => {
  NProgress.start();  // Start the progress bar when navigation begins
  next();
});

router.afterEach(() => {
  NProgress.done();  // Complete the progress bar when navigation finishes
});

app.use(router);

// Create a global cache object
const fallbackImageCache = new Map<string, string>();

// Function to clear the cache and force reload images
const clearFallbackImageCache = () => {
  fallbackImageCache.clear();
};

// Call to clear the cache once
clearFallbackImageCache();

// For cache busting
const forceImageReload = (imageUrl: string) => {
  // Append a unique query string to force the image to reload
  return `${imageUrl}?_=${new Date().getTime()}`;
};

// Mount app
app.mount('#app');
