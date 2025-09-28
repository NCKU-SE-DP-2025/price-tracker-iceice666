<template>
    <div class="news-item">
        <div class="container" >
            <div class="texts" @click="showDialog">
                <h2>{{ news.title }}</h2>
                <p class="time">{{ news.time }}</p>
                <div v-if="hasDetails">
                    <p><strong>原因：</strong> {{ news.reason }}</p>
                    <p><strong>影響：</strong> {{ news.summary }}</p>
                </div>
                <div v-else>
                    <p>{{ shortContent }}</p>
                </div>
            </div>
            <i v-if="!hasDetails && !news.isSummaryLoading && isLoggedIn" class="bi bi-stars summary-btn" @click="fetchSummary"></i>
            <div v-if="!hasDetails && news.isSummaryLoading && isLoggedIn" class="loader"></div>
        </div>
        <div class="upvote-btn" @click="toggleUpvote(news.id)" v-if="'upvotes' in news">
            <i class="bi bi-fire" :class="{'fire-upvoted': news.is_upvoted}"></i>
            <span>{{ news.upvotes }}</span>
        </div>

    </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useNewsStore } from '@/stores/news';

const props = defineProps({
    news: {
        type: Object,
        required: true
    }
});

const emit = defineEmits(['show-dialog', 'fetch-summary']);

const userStore = useAuthStore();
const newsStore = useNewsStore();
const isLoading = ref(false);

const hasDetails = computed(() => props.news.reason && props.news.summary);
const shortContent = computed(() =>
    props.news.content.length > 200 ? props.news.content.substr(0, 200) + '...' : props.news.content
);
const isLoggedIn = computed(() => userStore.isLoggedIn);

const showDialog = () => {
    emit('show-dialog');
};

const fetchSummary = () => {
    if (isLoading.value) return;
    isLoading.value = true;
    emit('fetch-summary');
};

const toggleUpvote = (newsId) => {
    newsStore.toggleUpvote(newsId);
};
</script>

<style scoped>
.news-item {
    padding: 1em;
    border-radius: 0.5em;
    transition: background-color 0.2s;
}

.news-item:hover {
    background-color: rgba(0, 0, 0, 0.02);
}

.news-item h2 {
    margin: 0 0 0.5em 0;
    font-size: 1.3em;
    line-height: 1.4;
}

.news-item p {
    margin: .5em 0;
    text-align: start;
    font-size: 1em;
    line-height: 1.5;
}

.news-item .time {
    color: #888;
    font-size: 0.9em;
}

.container {
    display: flex;
    align-items: flex-start;
    gap: 1em;
}

.texts {
    flex: 1;
    padding: 0.5em;
    border-radius: .5em;
    transition: background-color 0.2s;
    cursor: pointer;
}

.texts:hover {
    background-color: rgba(0, 0, 0, 0.05);
}

/* Always show summary button on mobile, hover on desktop */
.summary-btn {
    font-size: 1.5em;
    cursor: pointer;
    padding: 0.5em;
    border-radius: 0.25em;
    transition: all 0.2s;
    color: #666;
    min-width: 44px;
    min-height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.summary-btn:hover {
    color: #f0ad4e;
    background-color: rgba(240, 173, 78, 0.1);
}

.upvote-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: .5em;
    border-radius: 1em;
    min-width: 44px;
    min-height: 44px;
    transition: background-color 0.2s;
    cursor: pointer;
    flex-shrink: 0;
}

.upvote-btn span {
    margin-left: .25em;
    font-size: 1.1em;
    color: rgba(0,0,0,0.6);
    font-weight: bold;
}

.upvote-btn:hover {
    background-color: rgba(0,0,0,0.1);
}

.upvote-btn > i {
    font-size: 1.3em;
    color: rgba(0,0,0,0.5);
}

.fire-upvoted {
    color: #f6620c !important;
}

.loader {
    width: 30px;
    padding: 8px;
    aspect-ratio: 1;
    border-radius: 50%;
    background: #20A7E8;
    --_m:
        conic-gradient(#0000 10%,#000),
        linear-gradient(#000 0 0) content-box;
    -webkit-mask: var(--_m);
    mask: var(--_m);
    -webkit-mask-composite: source-out;
    mask-composite: subtract;
    animation: l3 1s infinite linear;
}

@keyframes l3 {
    to { transform: rotate(1turn) }
}

/* Responsive Design */
@media (min-width: 768px) {
    .news-item h2 {
        font-size: 1.5em;
    }

    .news-item p {
        font-size: 1.1em;
    }

    .summary-btn {
        font-size: 2em;
        display: none;
    }

    .news-item:hover .summary-btn {
        display: flex;
    }

    .upvote-btn {
        width: 3em;
        height: 3em;
        padding: .5em 2em;
    }

    .upvote-btn span {
        font-size: 1.2em;
    }

    .upvote-btn > i {
        font-size: 1.5em;
    }

    .texts {
        padding: 1em;
        margin-right: 1em;
    }
}

@media (max-width: 767px) {
    .container {
        flex-direction: column;
        align-items: stretch;
    }

    .summary-btn {
        align-self: center;
        margin-top: 0.5em;
    }

    .upvote-btn {
        align-self: center;
        margin-top: 0.5em;
    }
}
</style>