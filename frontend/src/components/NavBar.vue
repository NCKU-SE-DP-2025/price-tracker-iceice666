<template>
    <nav class="navbar">
        <div class="title">
            <RouterLink to="/overview">價格追蹤小幫手</RouterLink>
        </div>

        <!-- Mobile menu button -->
        <button class="mobile-menu-btn" @click="toggleMobileMenu" :class="{ active: isMobileMenuOpen }">
            <span class="hamburger-line"></span>
            <span class="hamburger-line"></span>
            <span class="hamburger-line"></span>
        </button>

        <!-- Navigation menu -->
        <ul class="options" :class="{ 'mobile-open': isMobileMenuOpen, 'transition-enabled': enableTransition }">
            <li><RouterLink to="/overview" @click="closeMobileMenu">物價概覽</RouterLink></li>
            <li><RouterLink to="/trending" @click="closeMobileMenu">物價趨勢</RouterLink></li>
            <li><RouterLink to="/news" @click="closeMobileMenu">相關新聞</RouterLink></li>
            <li v-if="!isLoggedIn"><RouterLink to="/login" @click="closeMobileMenu">登入</RouterLink></li>
            <li v-else @click="logout">Hi, {{getUserName}}! 登出</li>
        </ul>
    </nav>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue';
import { useAuthStore } from '@/stores/auth';

const userStore = useAuthStore();
const isMobileMenuOpen = ref(false);
const enableTransition = ref(false);

const isLoggedIn = computed(() => userStore.isLoggedIn);
const getUserName = computed(() => userStore.getUserName);

const toggleMobileMenu = () => {
    enableTransition.value = true;
    isMobileMenuOpen.value = !isMobileMenuOpen.value;
};

const closeMobileMenu = () => {
    enableTransition.value = true;
    isMobileMenuOpen.value = false;
};

const logout = () => {
    userStore.logout();
    closeMobileMenu();
};

// Handle resize events to disable transitions during resize
let resizeTimeout;
const handleResize = () => {
    enableTransition.value = false;
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        enableTransition.value = true;
    }, 100);
};

onMounted(() => {
    window.addEventListener('resize', handleResize);
    // Enable transitions after initial mount
    setTimeout(() => {
        enableTransition.value = true;
    }, 100);
});

onUnmounted(() => {
    window.removeEventListener('resize', handleResize);
    clearTimeout(resizeTimeout);
});
</script>

<style scoped>
.navbar {
    display: flex;
    justify-content: space-between;
    background-color: #f3f3f3;
    padding: 1.5em;
    height: 4.5em;
    width: 100%;
    align-items: center;
    box-shadow: 0 0 5px #000000;
    position: relative;
}

.navbar ul {
    list-style: none;
    display: flex;
    justify-content: space-around;
    margin: 0;
    padding: 0;
}

.title > a {
    font-size: 1.4em;
    font-weight: bold;
    color: #2c3e50 !important;
}

.navbar li {
    color: #575B5D;
    margin: 0 .5em;
    font-size: 1.2em;
}

.navbar li:hover {
    cursor: pointer;
    font-weight: bold;
}

.navbar a {
    text-decoration: none;
    color: #575B5D;
}

/* Mobile menu button - hidden by default */
.mobile-menu-btn {
    display: none;
    flex-direction: column;
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
    width: 30px;
    height: 24px;
    justify-content: space-between;
}

.hamburger-line {
    width: 100%;
    height: 3px;
    background-color: #2c3e50;
    transition: all 0.3s ease;
    transform-origin: center;
}

/* Hamburger animation */
.mobile-menu-btn.active .hamburger-line:nth-child(1) {
    transform: rotate(45deg) translate(6px, 6px);
}

.mobile-menu-btn.active .hamburger-line:nth-child(2) {
    opacity: 0;
}

.mobile-menu-btn.active .hamburger-line:nth-child(3) {
    transform: rotate(-45deg) translate(6px, -6px);
}

/* Responsive styles */
@media (max-width: 768px) {
    .navbar {
        padding: 1em 1.5em;
    }

    .title > a {
        font-size: 1.2em;
    }

    .mobile-menu-btn {
        display: flex;
    }

    .options {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background-color: #f3f3f3;
        flex-direction: column;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transform: translateY(-100%);
        opacity: 0;
        visibility: hidden;
        z-index: 1000;
    }

    .options.transition-enabled {
        transition: all 0.3s ease;
    }

    .options.mobile-open {
        transform: translateY(0);
        opacity: 1;
        visibility: visible;
    }

    .options li {
        margin: 0;
        padding: 1em 1.5em;
        border-bottom: 1px solid #e0e0e0;
        text-align: left;
    }

    .options li:last-child {
        border-bottom: none;
    }

    .options li:hover {
        background-color: #e8e8e8;
    }
}

@media (max-width: 480px) {
    .navbar {
        padding: 0.8em 1em;
    }

    .title > a {
        font-size: 1em;
    }

    .options li {
        padding: 0.8em 1em;
        font-size: 1.1em;
    }
}

/* Tablet styles */
@media (min-width: 769px) and (max-width: 1024px) {
    .navbar li {
        margin: 0 0.3em;
        font-size: 1.1em;
    }

    .title > a {
        font-size: 1.3em;
    }
}
</style>