<template>
    <div class="wrapper">
        <h1>相關新聞</h1>
        <div class="search-bar">
            <input v-model="prompt" placeholder="輸入你的搜尋prompt，讓AI幫你找相關的新聞吧！例如：「我想獲取雞蛋價格的資訊」" class="search-input"/>
            <i class="bi bi-search" @click="searchNewsBasedOnPrompt"></i>
        </div>
        <div class="content">
            <div v-if="isLoading">loading...</div>
            <div v-else>
                <NewsItem v-for="(news, index) in newsList" :key="news.id" :news="news" 
                    @show-dialog="showDialog(news)" @fetch-summary="fetchSummary(news.content, index)"/>
                <div v-if="isEmpty">
                    <p>找不到相關新聞！</p>
                </div>
            </div>
        </div>
        <NewsDialog :news="selectedNews" v-model:visible="isDialogVisible" />
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useNewsStore } from '@/stores/news';
import NewsItem from '@/components/NewsItem.vue';
import NewsDialog from '@/components/NewsDialog.vue';

const newsStore = useNewsStore();

const prompt = ref('');
const selectedNews = ref(null);
const isDialogVisible = ref(false);

const newsList = computed(() => newsStore.getNews);
const isLoading = computed(() => newsStore.isLoading);
const isEmpty = computed(() => newsStore.newsList.length === 0);

const searchNewsBasedOnPrompt = () => {
    if (prompt.value.trim()) {
        newsStore.promptSearchNews(prompt.value);
        prompt.value = '';
    }
};

const showDialog = (news) => {
    selectedNews.value = news;
    isDialogVisible.value = true;
};

const fetchSummary = (content, index) => {
    newsStore.fetchNewsSummary(content, index);
};

onMounted(() => {
    newsStore.fetchNews();
});
</script>

<style scoped>
.wrapper {
    padding: 1.5em 1em;
    background: #f3f3f3;
    min-height: calc(100vh - 4.5em);
    height: calc(100% - 4.5em);
    box-sizing: border-box;
    width: 100%;
}

.content {
    background-color: white;
    margin-top: 1em;
    border-radius: 1em;
    padding: 1em;
}

.news-item {
    border-bottom: #aaaaaa 1px solid;
}

.news-item:last-child {
    border-bottom: none;
}

.search-bar {
    background-color: white;
    display: flex;
    border-radius: .5em;
    box-sizing: border-box;
    text-align: start;
    margin-top: 1em;
    padding: 1em;
    width: 100%;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.search-bar input {
    border: none;
    outline: none;
    font-size: 0.9em;
    box-sizing: border-box;
    flex-grow: 1;
    margin-right: 1em;
    min-width: 0;
}

.search-bar input::placeholder {
    font-size: 0.8em;
    color: #999;
}

.search-bar i {
    cursor: pointer;
    padding: 0.5em;
    border-radius: 0.25em;
    transition: background-color 0.2s;
    min-width: 44px;
    min-height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.search-bar i:hover {
    background-color: rgba(0,0,0,0.1);
}

.search-bar button:hover {
    cursor: pointer;
}

/* Responsive Design */
@media (min-width: 768px) {
    .wrapper {
        padding: 2em 2em;
    }

    .content {
        padding: 1em 2em;
    }

    .search-bar {
        width: 80%;
        max-width: 600px;
    }

    .search-bar input {
        font-size: 0.9em;
    }

    .search-bar input::placeholder {
        font-size: 0.9em;
    }
}

@media (min-width: 1024px) {
    .wrapper {
        padding: 3em 3em;
    }

    .content {
        padding: 1em 3em;
    }
}

@media (min-width: 1200px) {
    .wrapper {
        padding: 3em 5em;
    }
}
</style>