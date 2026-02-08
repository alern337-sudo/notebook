<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue';
import * as echarts from 'echarts';
import api from '../api';

const props = defineProps({
  memoId: {
    type: Number,
    required: true
  }
});

const chartRef = ref(null);
let chartInstance = null;

const fetchStats = async () => {
  if (!props.memoId) return;
  try {
    const response = await api.get(`/memos/${props.memoId}/stats`);
    const data = response.data;
    if (data && data.length > 0) {
      initChart(data);
    } else {
        // Clear chart if no data
        if (chartInstance) {
            chartInstance.dispose();
            chartInstance = null;
        }
    }
  } catch (error) {
    console.error('Failed to fetch stats:', error);
  }
};

const initChart = (data) => {
  if (!chartRef.value) return;
  
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value);
  }
  
  const option = {
    title: {
      text: '步骤耗时分布',
      left: 'center',
      textStyle: {
        fontSize: 14
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} 小时 ({d}%)'
    },
    legend: {
      orient: 'horizontal',
      left: 'center',
      bottom: 0,
      width: '90%'
    },
    series: [
      {
        name: '耗时',
        type: 'pie',
        radius: '50%',
        center: ['50%', '45%'],
        data: data,
        avoidLabelOverlap: true,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        label: {
            show: true,
            formatter: '{b}: {c}h'
        }
      }
    ]
  };
  
  chartInstance.setOption(option);
};

onMounted(() => {
  fetchStats();
  window.addEventListener('resize', handleResize);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
  if (chartInstance) {
    chartInstance.dispose();
  }
});

const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize();
  }
};

watch(() => props.memoId, () => {
  fetchStats();
});
</script>

<template>
  <div ref="chartRef" class="w-full h-[300px]"></div>
</template>
