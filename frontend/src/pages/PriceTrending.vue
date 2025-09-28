<template>
    <div class="wrapper">
        <h1>物價趨勢</h1>
        <div class="content">
            <div class="selects">

                <select v-model="selectedCategory">
                    <option disabled value="">請選擇商品類別</option>
                    <option v-for="category in categoryKeys" :key="category" :value="category">{{
                        categoryName(category)}}</option>
                </select>
                <select v-model="selectedProduct">
                    <option disabled value="">請選擇商品</option>
                    <option v-for="product in products" :key="product.產品名稱" :value="product">{{ product.產品名稱 }}</option>
                </select>
            </div>
            <div v-if="selectedProduct" class="visualize">
                <TrendingChart v-if="selectedProduct" :data="selectedProduct"></TrendingChart>
                <TrendingTable v-if="selectedProduct" :data="selectedProduct"></TrendingTable>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { usePricesStore } from '@/stores/prices';
import Categories from '@/constants/categories';
import TrendingTable from '@/components/TrendingTable.vue';
import TrendingChart from '@/components/TrendingChart.vue';

const store = usePricesStore();

const selectedCategory = ref('');
const selectedProduct = ref('');
const productList = ref([]);

const categoryKeys = computed(() => Object.keys(Categories));
const products = computed(() =>
    selectedCategory.value ? store.getPricesByCategory(selectedCategory.value) : []
);

const categoryName = (category) => {
    return Categories[category];
};

watch(selectedCategory, () => {
    selectedProduct.value = '';
    productList.value = store.getProductList(selectedCategory.value);
});

watch(selectedProduct, () => {
    console.log(selectedProduct.value);
});

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
    width: 100%;
}

.content {
    margin-top: 1em;
    background-color: #fff;
    border-radius: 1em;
    padding: 1em;
    width: 100%;
    box-sizing: border-box;
}

.selects {
    display: flex;
    flex-direction: column;
    gap: 1em;
}

.selects > select {
    padding: 0.75em;
    font-size: 1em;
    border-radius: .5em;
    border: 1px solid #ccc;
    outline: none;
    cursor: pointer;
    appearance: auto !important;
    width: 100%;
    box-sizing: border-box;
}

.visualize {
    margin-top: 2em;
    display: flex;
    flex-direction: column;
    gap: 1em;
}

.visualize > * {
    width: 100%;
    box-sizing: border-box;
    padding: 0;
}

/* Responsive Design */
@media (min-width: 768px) {
    .wrapper {
        padding: 2em 2em;
    }

    .content {
        margin-top: 2em;
        padding: 1.5em;
    }

    .selects {
        flex-direction: row;
        gap: 1em;
    }

    .selects > select {
        flex: 1;
        min-width: 200px;
    }

    .visualize {
        flex-direction: row;
    }

    .visualize > * {
        flex: 1 1 50%;
        padding: 1em;
    }
}

@media (min-width: 1024px) {
    .wrapper {
        padding: 3em 3em;
    }

    .content {
        padding: 2em;
    }

    .selects > select {
        font-size: 1.1em;
    }
}

@media (min-width: 1200px) {
    .wrapper {
        padding: 3em 5em;
    }
}
</style>