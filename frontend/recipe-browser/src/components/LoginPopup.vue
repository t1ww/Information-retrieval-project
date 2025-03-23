<!-- LoginPopup.vue -->
<template>
  <div v-if="visible" class="login-popup">
    <div class="popup-content">
      <h3>Login</h3>
      <form @submit.prevent="login">
        <label for="username">Username:</label>
        <input type="text" id="username" v-model="localUsername" required />

        <label for="password">Password:</label>
        <input type="password" id="password" v-model="localPassword" required />

        <button type="submit">Login</button>
      </form>
      <p v-if="error" class="error-message">{{ error }}</p>
      <p>
        Don't have an account?
        <router-link to="/register">Register here</router-link>
      </p>
      <button @click="close" class="close-btn">Close</button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue'

export default defineComponent({
  name: 'LoginPopup',
  props: {
    visible: {
      type: Boolean,
      required: true
    }
  },
  emits: ['login', 'close'],
  setup(props, { emit }) {
    const localUsername = ref('')
    const localPassword = ref('')
    const error = ref('')

    const login = () => {
      emit('login', {
        username: localUsername.value,
        password: localPassword.value,
        setError: (msg: string) => (error.value = msg),
        reset: () => {
          localUsername.value = ''
          localPassword.value = ''
          error.value = ''
        }
      })
    }

    const close = () => {
      error.value = ''
      emit('close')
    }

    // Reset fields when popup is hidden
    watch(() => props.visible, (visible) => {
      if (!visible) {
        localUsername.value = ''
        localPassword.value = ''
        error.value = ''
      }
    })

    return { localUsername, localPassword, error, login, close }
  }
})
</script>

<style scoped>
.login-popup {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
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