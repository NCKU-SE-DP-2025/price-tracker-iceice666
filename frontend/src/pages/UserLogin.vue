<template>
    <div class="login-page">
        <h1>使用者登入</h1>
        <div class="container">
            <form @submit.prevent="login">
                <input v-model="username" type="text" placeholder="Username" required>
                <input v-model="password" type="password" placeholder="Password" required>
                <p v-if="loginError" class="error">{{ loginError }}</p>
                <div class="ops">
                    <button type="button" id="register"><RouterLink to="/register">註冊</RouterLink></button>
                    <button type="submit" id="login">登入</button>
                </div>
            </form>
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';

const userStore = useAuthStore();

const username = ref('');
const password = ref('');

const loginError = computed(() => userStore.getLoginError);

const login = () => {
    userStore.login(username.value, password.value);
};
</script>

<style scoped>
.login-page {
    padding: 1.5em 1em;
    background: #f3f3f3;
    min-height: calc(100vh - 4.5em);
    height: calc(100% - 4.5em);
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.error {
    color: red;
    font-size: 0.9em;
    margin-top: 0.5em;
}

.container {
    margin-top: 1em;
    background: #fff;
    padding: 1.5em;
    border-radius: 1em;
    box-shadow: 0 0 10px rgba(0, 0, 0, .1);
    width: 100%;
    max-width: 400px;
    box-sizing: border-box;
}

form {
    display: flex;
    flex-direction: column;
}

form > input {
    margin: .5em 0;
    padding: .75em 1em;
    font-size: 1em;
    border: 1px solid #ccc;
    border-radius: .5em;
    box-sizing: border-box;
    min-height: 44px;
}

form > input:focus {
    outline: none;
    border-color: #5bc0de;
    box-shadow: 0 0 0 2px rgba(91, 192, 222, 0.2);
}

.ops {
    margin-top: 1em;
    display: flex;
    flex-direction: column;
    gap: 0.75em;
}

.ops > button {
    padding: .75em 1em;
    font-size: 1.1em;
    border: none;
    border-radius: .5em;
    cursor: pointer;
    min-height: 44px;
    transition: background-color 0.2s;
}

#register {
    background-color: #F3F3F3;
    border: 1px solid #ccc;
}

#register > a {
    text-decoration: none;
    color: #000;
    display: block;
    width: 100%;
    height: 100%;
}

#register:hover {
    background-color: #e8e8e8;
}

#login {
    background-color: #5bc0de;
    color: #fff;
}

#login:hover {
    background-color: #46b8da;
}

/* Responsive Design */
@media (min-width: 768px) {
    .login-page {
        padding: 2em 2em;
    }

    .container {
        margin-top: 2em;
        padding: 2em;
        max-width: 450px;
    }

    .ops {
        flex-direction: row;
        justify-content: center;
        gap: 1em;
    }

    .ops > button {
        flex: 1;
        max-width: 150px;
    }

    form > input {
        font-size: 1.1em;
    }

    .ops > button {
        font-size: 1.2em;
    }
}

@media (min-width: 1024px) {
    .login-page {
        padding: 3em 3em;
    }
}

@media (min-width: 1200px) {
    .login-page {
        padding: 3em 5em;
    }

    .container {
        max-width: 500px;
    }
}
</style>