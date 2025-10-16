<template>
    <div class="trending-table">
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th rowspan="2" class="year-header">年份</th>
                        <th v-for="month in months" :key="month" class="month-header">{{ month }}</th>
                    </tr>
                </thead>
                <tbody>
                    <template v-for="year in years" :key="year">
                        <tr>
                            <td class="year-cell">{{ year }}</td>
                            <template v-for="(value, monthIndex) in getYearData(year)" :key="year + '-month-' + monthIndex">
                                <td class="value-cell">{{ valueDisplay(value) }}</td>
                            </template>
                        </tr>
                    </template>
                </tbody>
            </table>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';

const props = defineProps({
    data: {
        type: Object,
        required: true
    }
});

const yearData = ref({});

const months = computed(() => ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']);

const years = computed(() => {
    const startYear = new Date(props.data.時間起點).getFullYear();
    const endYear = new Date(props.data.時間終點).getFullYear();
    let years = [];
    for (let year = startYear; year <= endYear; year++) {
        years.push(year);
    }
    return years;
});

const getYearData = (year) => {
    return yearData.value[year];
};

const processInitData = () => {
    const startMonth = new Date(props.data.時間起點).getMonth() + 1;
    const endMonth = new Date(props.data.時間終點).getMonth() + 1;
    const startYear = new Date(props.data.時間起點).getFullYear();
    const endYear = new Date(props.data.時間終點).getFullYear();
    yearData.value = {};
    for (let year = startYear; year <= endYear; year++) {
        let yearPrices = [];
        for (let month = 1; month <= 12; month++) {
            if (year === startYear && month < startMonth) {
                yearPrices.push('0');
            } else if (year === endYear && month > endMonth) {
                yearPrices.push('0');
            } else {
                yearPrices.push(props.data.統計值.split(',')[month + (year - startYear) * 12 - startMonth]);
            }
        }
        yearData.value[year] = yearPrices;
    }
};

const valueDisplay = (value) => {
    return value === '0' ? '-' : value;
};

watch(() => props.data, (newVal) => {
    if (newVal) {
        processInitData();
    }
}, { deep: true });

onMounted(() => {
    processInitData();
});
</script>

<style scoped>
.trending-table {
    margin-top: 1em;
    overflow: hidden;
    border-radius: 0.5em;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.table-container {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}

table {
    width: 100%;
    min-width: 600px;
    border-collapse: collapse;
    background-color: white;
}

th, td {
    border: 1px solid #ddd;
    padding: 0.3em;
    text-align: center;
    font-size: 0.8em;
    white-space: nowrap;
}

th {
    background-color: #355f81;
    color: white;
    font-weight: bold;
    position: sticky;
    top: 0;
    z-index: 10;
}

.year-header, .year-cell {
    background-color: #4a6fa5;
    color: white;
    font-weight: bold;
    position: sticky;
    left: 0;
    z-index: 20;
    min-width: 60px;
}

.year-cell {
    background-color: #5a7fb5;
}

.month-header {
    min-width: 50px;
}

.value-cell {
    min-width: 50px;
}

/* Responsive Design */
@media (min-width: 768px) {
    .trending-table {
        margin-top: 2em;
    }

    table {
        min-width: 800px;
    }

    th, td {
        padding: 0.5em;
        font-size: 0.9em;
    }

    .year-header, .year-cell {
        min-width: 80px;
    }

    .month-header, .value-cell {
        min-width: 60px;
    }
}

@media (min-width: 1024px) {
    table {
        min-width: 1000px;
    }

    th, td {
        padding: 0.5em;
        font-size: 1em;
    }

    .year-header, .year-cell {
        min-width: 100px;
    }

    .month-header, .value-cell {
        min-width: 70px;
    }
}

@media (min-width: 1200px) {
    .table-container {
        overflow-x: visible;
    }

    table {
        min-width: auto;
    }
}

/* Scroll indicators for mobile */
@media (max-width: 767px) {
    .table-container::after {
        content: '← 滑動查看更多 →';
        display: block;
        text-align: center;
        padding: 0.5em;
        background-color: #f8f9fa;
        font-size: 0.8em;
        color: #666;
        border-top: 1px solid #ddd;
    }
}
</style>