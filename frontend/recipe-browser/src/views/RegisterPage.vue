<script lang="ts">
import { defineComponent, ref } from 'vue'
import { useRouter } from 'vue-router'
import axios, { AxiosError } from 'axios' // Import axios for HTTP requests

export default defineComponent({
    name: 'Register',
    setup() {
        const router = useRouter()
        const username = ref('')
        const password = ref('')
        const confirmPassword = ref('')
        const errorMessage = ref('')

        // Handle form submission
        const handleSubmit = async () => {
            if (password.value !== confirmPassword.value) {
                errorMessage.value = 'Passwords do not match!'
                return
            }

            try {
                // Send the registration data to the Flask backend
                const response = await axios.post('http://localhost:5000/register', {
                    username: username.value,
                    password: password.value
                })

                // If registration is successful, redirect to login page
                console.log(response.data.message)
                router.push('/')
            } catch (error: unknown) {
                if (error instanceof AxiosError && error.response) {
                    errorMessage.value = error.response.data.message
                } else {
                    errorMessage.value = 'An error occurred. Please try again later.'
                }
            }
        }

        return {
            username,
            password,
            confirmPassword,
            errorMessage,
            handleSubmit
        }
    }
})
</script>

<template>
    <div class="register-page">
        <h2>Register</h2>
        <form @submit.prevent="handleSubmit">
            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" id="username" v-model="username" required />
            </div>

            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" v-model="password" required />
            </div>

            <div class="form-group">
                <label for="confirmPassword">Confirm Password:</label>
                <input type="password" id="confirmPassword" v-model="confirmPassword" required />
            </div>

            <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

            <button type="submit">Register</button>
        </form>
    </div>
</template>

<style scoped>
.register-page {
    width: 300px;
    margin: 50px auto;
    padding: 20px;
    background-color: #2e373a;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

h2 {
    text-align: center;
    margin-bottom: 20px;
}

.form-group {
    margin-bottom: 15px;
}

label {
    display: block;
    margin-bottom: 5px;
}

input {
    width: 100%;
    padding: 8px;
    margin-top: 5px;
    border: 1px solid #ccc;
    border-radius: 4px;
}

button {
    width: 100%;
    padding: 10px;
    background-color: #333;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

button:hover {
    background-color: #555;
}

.error-message {
    color: red;
    font-size: 14px;
    margin-top: 10px;
    text-align: center;
}

p {
    text-align: center;
    margin-top: 10px;
}

router-link {
    text-decoration: none;
    color: #333;
}

router-link:hover {
    text-decoration: underline;
}
</style>
