<template>
    <div class="category-price-wrapper">
        <h2>{{ categoryName }}</h2>
        <div v-if="isLoading" class="loading">Loading...</div>
        <div v-if="errorMessage" class="error">{{ errorMessage }}</div>
        <div v-if="!isLoading && !errorMessage" class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>商品名稱</th>
                        <th>規格</th>
                        <th>{{latestDataTime}} 最新價格</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="data in priceData" :key="data.編號">
                        <td>{{ data.產品名稱 }}</td>
                        <td>{{ data.規格 }}</td>
                        <td>{{ latestPrice(data.統計值) }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue';
import Categories from '@/constants/categories';

const props = defineProps({
    category: {
        type: String,
        required: true
    },
    priceData: {
        type: Array,
        required: true
    },
    isLoading: {
        type: Boolean,
        required: true
    },
    errorMessage: {
        type: String,
        required: false
    },
});

const categoryName = computed(() => Categories[props.category]);

const latestDataTime = computed(() => {
    let timeTmp = props.priceData[0].時間終點.split('-');
    return timeTmp[0] + '.' + timeTmp[1];
});

const latestPrice = (prices_str) => {
    let number = prices_str.split(',').map(Number);
    let i = number.length - 1;
    while (i >= 0 && number[i] == 0) {
        i--;
    }
    return i == -1 ? "-" : number[i];
};
</script>

<style scoped>
.error {
    color: red;
    padding: 1em;
    text-align: center;
}

.category-price-wrapper {
    background-color: white;
    border-radius: 1em;
    padding: 1em;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    overflow: hidden;
}

h2 {
    margin-bottom: .5em;
    font-size: 1.2em;
    font-weight: bold;
    text-align: center;
}

/* Table container with horizontal scroll for mobile */
.table-container {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    border-radius: 0.5em;
    margin-top: 1em;
}

table {
    width: 100%;
    min-width: 300px;
    border-collapse: collapse;
    background-color: white;
}

th, td {
    border: 1px solid #ddd;
    text-align: center;
    padding: .5em .75em;
    white-space: nowrap;
    font-size: 0.9em;
}

th {
    background-color: #355f81;
    color: white;
    font-weight: bold;
    position: sticky;
    top: 0;
    z-index: 10;
}

td {
    min-width: 80px;
}

/* Responsive Design */
@media (min-width: 768px) {
    .category-price-wrapper {
        padding: 1.5em;
    }

    h2 {
        font-size: 1.4em;
    }

    th, td {
        padding: .75em 1em;
        font-size: 1em;
    }

    table {
        min-width: 400px;
    }
}

@media (min-width: 1024px) {
    .category-price-wrapper {
        padding: 2em;
    }

    h2 {
        font-size: 1.5em;
    }

    .table-container {
        overflow-x: visible;
    }

    table {
        min-width: auto;
    }
}

/* Loading and error states */
.loading, .error {
    padding: 2em;
    text-align: center;
    font-size: 1.1em;
}

.loading {
    color: #666;
}
</style>
