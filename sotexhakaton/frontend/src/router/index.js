import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import AnalysisPage from '../views/AnalysisPage.vue'
import SubstationMap from '../components/SubstationMap.vue'
import FeederMonitor from '../components/FeederMonitor.vue'
import FeedersAnalysis from '../components/FeedersAnalysis.vue'
import ForecastPage from '../components/ForecastPage.vue'

const routes = [
  {
    path: '/',
    name: 'Map',
    component: SubstationMap
  },
  {
   path: '/monitor',
   name: 'Monitor',
   component: FeederMonitor
  },
   {
  path: '/feeders',
  name: 'Feeders',
  component: FeedersAnalysis
},
{
  path: '/forecast',
  name: 'Forecast',
  component: ForecastPage
}
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router