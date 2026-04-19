import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import AnalysisPage from '../views/AnalysisPage.vue'
import SubstationMap from '../components/SubstationMap.vue'

const routes = [
  {
    path: '/',
    name: 'Map',
    component: SubstationMap
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router