import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import KnowledgeBase from '../views/KnowledgeBase.vue'
import DigitalHumanConfig from '../views/DigitalHumanConfig.vue'

const routes =[
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', name: 'Dashboard', component: Dashboard, meta: { title: '数据概览' } },
  { path: '/kb', name: 'KnowledgeBase', component: KnowledgeBase, meta: { title: '知识库管理' } },
  { path: '/config', name: 'Config', component: DigitalHumanConfig, meta: { title: '数字人配置' } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router