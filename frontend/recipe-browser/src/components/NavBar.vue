<script lang="ts">
import { defineComponent, ref, computed } from 'vue'
import axios, { AxiosError } from 'axios' // Import axios for HTTP requests
import { useRouter } from 'vue-router' // Import Vue Router for navigation

export default defineComponent({
  name: 'NavBar',
  setup() {
    const isLoginPopupVisible = ref(false)  // To control visibility of the login popup
    const username = ref('') // Binding for username input
    const password = ref('') // Binding for password input
    const errorMessage = ref('') // To hold any error messages

    const router = useRouter()

    // Check if user is logged in by checking if the token exists
    const isLoggedIn = computed(() => {
      return localStorage.getItem('authToken') !== null
    })

    // Get the username from localStorage if logged in
    const toggleLoginPopup = () => {
      isLoginPopupVisible.value = !isLoginPopupVisible.value
    }

    const handleLogin = async () => {
      try {
        const response = await axios.post('http://localhost:5000/login', {
          username: username.value,
          password: password.value
        })

        if (response.data.token) {
          // Set the values to localStorage
          localStorage.setItem('authUsername', response.data.username)
          localStorage.setItem('authToken', response.data.token)

          // Update the `username` ref to reflect the new logged-in username
          username.value = response.data.username

          // Redirect to the homepage
          router.push('/')
        } else {
          errorMessage.value = 'Login failed. Please try again.'
        }

        toggleLoginPopup() // Close the login popup
      } catch (error: unknown) {
        if (error instanceof AxiosError && error.response?.data?.message) {
          errorMessage.value = error.response.data.message
        } else {
          errorMessage.value = 'An error occurred. Please try again later.'
        }
      }
    }

    const handleLogout = () => {
      localStorage.removeItem('authUsername')
      localStorage.removeItem('authToken')
      router.push('/') // Redirect to homepage after logout
    }
    const userDisplayName = computed(() => {
      return localStorage.getItem('authUsername') || ''
    })


    return {
      isLoginPopupVisible,
      username,
      password,
      errorMessage,
      toggleLoginPopup,
      handleLogin,
      handleLogout,
      isLoggedIn,
      userDisplayName
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

      <!-- Show 'Login' link if the user is not logged in -->
      <li v-if="!isLoggedIn">
        <a href="javascript:void(0);" class="nav-link" @click="toggleLoginPopup">Login</a>
      </li>

      <!-- Show username and 'Logout' if the user is logged in -->
      <li v-if="isLoggedIn">
        <span class="nav-link">Welcome, {{ userDisplayName }}</span>
        <a href="javascript:void(0);" class="nav-link" @click="handleLogout">Logout</a>
      </li>
    </ul>

    <!-- Login Popup -->
    <div v-if="isLoginPopupVisible" class="login-popup">
      <div class="popup-content">
        <h3>Login</h3>
        <form @submit.prevent="handleLogin">
          <label for="username">Username:</label>
          <input type="text" id="username" v-model="username" required />

          <label for="password">Password:</label>
          <input type="password" id="password" v-model="password" required />

          <button type="submit">Login</button>
        </form>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
        <p>Don't have an account? <router-link to="/register">Register here</router-link></p>
        <button @click="toggleLoginPopup" class="close-btn">Close</button>
      </div>
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

/* Login Popup Styles */
.login-popup {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  /* Overlay */
  display: flex;
  justify-content: center;
  align-items: center;
}

.popup-content {
  background-color: rgb(43, 46, 47);
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  width: 300px;
}

.popup-content h3 {
  margin-bottom: 1rem;
}

.popup-content label {
  display: block;
  margin-bottom: 0.5rem;
}

.popup-content input {
  width: 100%;
  padding: 0.5rem;
  margin-bottom: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.popup-content button {
  width: 100%;
  padding: 0.7rem;
  background-color: #333;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.popup-content button:hover {
  background-color: #555;
}

.close-btn {
  margin-top: 1rem;
  background-color: #f44336;
  color: white;
  border: none;
  padding: 0.5rem;
  cursor: pointer;
}

.close-btn:hover {
  background-color: #d32f2f;
}

.error-message {
  color: red;
  font-size: 14px;
  margin-top: 10px;
  text-align: center;
}
</style>
