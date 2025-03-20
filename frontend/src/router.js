import { createRouter, createWebHistory } from 'vue-router'
import { session } from './data/session'
import { userResource } from '@/data/user'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/pages/Home.vue'),
  },
  {
    name: 'Login',
    path: '/account/login',
    component: () => import('@/pages/Login.vue'),
  },
  {
    name: 'Register',
    path: '/register',
    component: () => import('@/pages/register.vue'),
  },
  {
    name: 'signin',
    path: '/signin',
    component: () => import('@/pages/signin.vue'),
  },
  {
    name: 'main',
    path: '/main',
    component: () => import('@/pages/main.vue'),
  },
  {
    name: 'filecode',
    path: '/filecode/:uuid',  // Added UUID parameter
    component: () => import('@/pages/filecode.vue'),
    props: true  // Enable props for route params
  },

  {
    name: 'filee',
    path: '/filee',
    component: () => import('@/pages/filee.vue'),
  },

  {
    name: 'likect',
    path: '/likect',
    component: () => import('@/pages/likect.vue'),
  },

  {
    name: 'member',
    path: '/member/:courseId',
    component: () => import('@/pages/member.vue'),
  },

  {
    name: 'owner',
    path: '/owner/:courseId',
    component: () => import('@/pages/owner.vue'),
  },

  {
    name: 'courses',
    path: '/courses',
    component: () => import('@/pages/courses.vue'),
  },
]

let router = createRouter({
  history: createWebHistory('/frontend'),
  routes,
})

router.beforeEach(async (to, from, next) => {
  let isLoggedIn = session.isLoggedIn
  try {
    await userResource.promise
  } catch (error) {
    isLoggedIn = false
  }
  
  if (to.name === 'Login' && isLoggedIn) {
    next({ name: 'Home' })
  } else if (to.name !== 'Login' && !isLoggedIn) {
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router