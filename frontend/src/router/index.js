import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../components/Dashboard.vue'
import Compare from '../components/CompareAccounts.vue'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', name: 'Dashboard', component: Dashboard },
  { path: '/compare', name: 'Compare', component: Compare },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
