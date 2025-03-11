import { createRouter, createWebHistory } from 'vue-router';
import type { RouteLocationNormalized, NavigationGuardNext } from 'vue-router';

// Import your components (views)
import HomePage from '@/views/HomePage.vue';
import SearchPage from '@/views/SearchPage.vue';
import RecipePage from '@/views/RecipePage.vue';
import RegisterPage from '@/views/RegisterPage.vue';


// Define routes
const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterPage,
  },
  {
    path: '/recipe/:id',
    name: 'Recipe',
    component: RecipePage,
  },
  {
    path: '/search',
    name: 'Search',
    component: SearchPage,
    beforeEnter: (to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
      if (!to.query.query && !to.query.q) {
        next({ path: '/search', query: { query: '' } }); // Default query if no query exists
      } else {
        next();
      }
    },
  },
];

// Create the router instance
const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Export the router
export default router;
