<!-- NavBar.vue -->
<script lang="ts">
import { defineComponent, ref, computed } from 'vue'
import axios, { AxiosError } from 'axios'
import { useRouter } from 'vue-router'
import LoginPopup from './LoginPopup.vue' // adjust path if needed

export default defineComponent({
  name: 'NavBar',
  components: { LoginPopup },
  setup() {
    const isLoginPopupVisible = ref(false)
    const successMessage = ref('')
    const showSuccessPopup = ref(false)
    const router = useRouter()

    const isLoggedIn = computed(() => {
      return localStorage.getItem('authToken') !== null
    })

    const toggleLoginPopup = () => {
      isLoginPopupVisible.value = !isLoginPopupVisible.value
    }

    const showMessage = (message: string) => {
      successMessage.value = message
      showSuccessPopup.value = true
      setTimeout(() => {
        showSuccessPopup.value = false
      }, 2000)
    }

    const handleLogin = async (credentials: { username: string; password: string; setError: (msg: string) => void; reset: () => void }) => {
      try {
        const response = await axios.post('http://localhost:5000/login', {
          username: credentials.username,
          password: credentials.password
        })

        if (response.data.token) {
          localStorage.setItem('authUsername', response.data.username)
          localStorage.setItem('authToken', response.data.token)
          showMessage('Login successful!')
          credentials.reset()
          toggleLoginPopup()
          setTimeout(() => router.go(0), 1500)
        } else {
          credentials.setError('Login failed. Please try again.')
        }
      } catch (error: unknown) {
        if (error instanceof AxiosError && error.response?.data?.message) {
          credentials.setError(error.response.data.message)
        } else {
          credentials.setError('An error occurred. Please try again later.')
        }
      }
    }

    const handleLogout = () => {
      if (confirm('Are you sure you want to log out?')) {
        showMessage('Logging out...')
        setTimeout(() => {
          localStorage.removeItem('authUsername')
          localStorage.removeItem('authToken')
          router.go(0)
        }, 1500)
      }
    }

    const userDisplayName = computed(() => localStorage.getItem('authUsername') || '')

    return {
      isLoginPopupVisible,
      toggleLoginPopup,
      handleLogin,
      handleLogout,
      isLoggedIn,
      userDisplayName,
      successMessage,
      showSuccessPopup
    }
  }
})
</script>

<template>
  <nav>
    <ul>
      <li>
        <router-link to="/" class="nav-link" exact>Home</router-link>
      </li>
      <li v-if="!isLoggedIn">
        <a href="javascript:void(0);" class="nav-link" @click="toggleLoginPopup">Login</a>
      </li>
      <li v-if="isLoggedIn">
        <span class="nav-link">Welcome, {{ userDisplayName }}</span>
      </li>
      <li v-if="isLoggedIn">
        <a href="javascript:void(0);" class="nav-link" @click="handleLogout">Logout</a>
      </li>
      <li v-if="isLoggedIn">
        <router-link to="/bookmark" class="nav-link" exact>Bookmark</router-link>
      </li>
    </ul>

    <LoginPopup :visible="isLoginPopupVisible" @login="handleLogin" @close="toggleLoginPopup" />

    <div v-if="showSuccessPopup" class="success-popup">
      <p>{{ successMessage }}</p>
    </div>
  </nav>
</template>

<style scoped>
nav {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  background-color: #333;
  padding: 1rem;
  padding-left: 2rem;
  z-index: 1000;
}

ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
  display: flex;
}

li {
  margin-right: 20px;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-size: 18px;
}

.nav-link:hover {
  text-decoration: underline;
  cursor: pointer;
}

.success-popup {
  position: fixed;
  top: 10%;
  left: 50%;
  transform: translateX(-50%);
  background-color: #4caf50;
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  font-size: 16px;
}
</style>
