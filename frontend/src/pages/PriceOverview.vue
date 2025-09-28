<template>
    <div class="wrapper">
        <h1 class="main-title">各類商品物價概覽</h1>
        <h3 v-if="!isLoading" class="subtitle">資料更新時間：{{updateTime}}</h3>
        <div class="prices">
            <CategoryPrice class="category" v-for="category in categoryList" :key="category"
                :category="category" :isLoading="isLoading" :errorMessage="errorMessage" :priceData="getPriceData(category)"></CategoryPrice>
        </div>
    </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import CategoryPrice from '@/components/CategoryPrice.vue';
import Categories from '@/constants/categories';
import { usePricesStore } from '@/stores/prices';

const store = usePricesStore();

const categoryList = computed(() => Object.keys(Categories));
const isLoading = computed(() => store.isLoading);
const errorMessage = computed(() => store.errorMessage);
const updateTime = computed(() => store.updatedTime);

const getPriceData = (category) => {
    return store.getPricesByCategory(category);
};

onMounted(() => {
    store.fetchPrices();
});
</script>

<style scoped>
.wrapper {
    padding: 1.5em 1em;
    background: #f3f3f3;
    min-height: calc(100vh - 4.5em);
    height: calc(100% - 4.5em);
    box-sizing: border-box;
}

.main-title {
    font-size: 1.8em;
    margin-bottom: 0.5em;
}

.prices {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1em;
    margin-top: 1em;
}

.category {
    width: 100%;
}

.subtitle {
    font-weight: normal;
    margin-top: .5em;
    font-size: 0.9em;
}

/* Responsive Design */
@media (min-width: 768px) {
    .wrapper {
        padding: 2em 2em;
    }

    .main-title {
        font-size: 2.2em;
    }

    .prices {
        grid-template-columns: repeat(2, 1fr);
        gap: 1.5em;
    }

    .subtitle {
        font-size: 1em;
    }
}

@media (min-width: 1024px) {
    .wrapper {
        padding: 3em 3em;
    }

    .prices {
        grid-template-columns: repeat(3, 1fr);
    }
}

@media (min-width: 1200px) {
    .wrapper {
        padding: 3em 5em;
    }

    .prices {
        grid-template-columns: repeat(4, 1fr);
        gap: 2em;
    }
}
</style>