<template>
  <div class="relative flex h-48 w-full overflow-hidden bg-white text-zinc-900 rounded-md border border-zinc-200 touch-pan-y select-none shadow-sm">
    <!-- Selection Highlight Bar -->
    <div class="absolute top-1/2 left-2 right-2 h-10 -mt-5 bg-zinc-100/80 rounded-sm pointer-events-none z-0"></div>
    
    <!-- Columns -->
    <div 
      v-for="(col, colKey) in columns" 
      :key="colKey" 
      class="flex-1 relative z-10 h-full group"
    >
      <div 
        :ref="(el) => setContainerRef(el, colKey)"
        class="h-full overflow-y-auto snap-y snap-mandatory no-scrollbar py-[calc(6rem-1.25rem)]"
        @scroll.passive="onScroll(colKey)"
        @touchstart="onTouchStart(colKey)"
        @touchend="onTouchEnd(colKey)"
      >
        <div 
          v-for="option in getOptions(colKey)" 
          :key="option.value" 
          class="h-10 flex items-center justify-center transition-all duration-200 snap-center cursor-pointer px-1"
          :class="[
            currentValues[colKey] === option.value 
              ? 'font-semibold text-zinc-900 scale-110' 
              : 'text-zinc-400 scale-90',
            'text-[clamp(10px,3.5vw,14px)] whitespace-nowrap'
          ]"
          @click="selectOption(colKey, option.value)"
        >
          {{ option.label }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue';
import { useDebounceFn } from '@vueuse/core';

const props = defineProps({
  modelValue: {
    type: String, // ISO string or null
    default: null
  },
  mode: {
    type: String,
    default: 'datetime', // 'datetime' | 'date'
    validator: (val) => ['datetime', 'date'].includes(val)
  }
});

const emit = defineEmits(['update:modelValue']);

// Configuration
const years = computed(() => {
  const currentYear = new Date().getFullYear();
  const range = [];
  for (let i = currentYear - 5; i <= currentYear + 5; i++) {
    range.push({ label: `${i}年`, value: i });
  }
  return range;
});

const months = Array.from({ length: 12 }, (_, i) => ({ label: `${i + 1}月`, value: i + 1 }));

const hours = Array.from({ length: 24 }, (_, i) => ({ 
  label: i.toString().padStart(2, '0') + '时', 
  value: i 
}));

const minutes = [0, 15, 30, 45].map(m => ({ 
  label: m.toString().padStart(2, '0') + '分', 
  value: m 
}));

// State
const currentValues = ref({
  year: new Date().getFullYear(),
  month: new Date().getMonth() + 1,
  day: new Date().getDate(),
  hour: new Date().getHours(),
  minute: 0 // Will round to nearest step
});

// Dynamic Days based on Year/Month
const days = computed(() => {
  const { year, month } = currentValues.value;
  const daysInMonth = new Date(year, month, 0).getDate();
  return Array.from({ length: daysInMonth }, (_, i) => ({ 
    label: `${i + 1}日`, 
    value: i + 1 
  }));
});

const columns = computed(() => {
  const base = {
    year: { options: years.value },
    month: { options: months },
    day: { options: days.value }
  };
  
  if (props.mode === 'datetime') {
    base.hour = { options: hours };
    base.minute = { options: minutes };
  }
  
  return base;
});

const getOptions = (key) => columns.value[key].options;

// Scroll Handling
const containerRefs = ref({});
const isScrolling = ref({});

const setContainerRef = (el, key) => {
  if (el) containerRefs.value[key] = el;
};

// Round minute to nearest 15
const roundMinute = (m) => {
  const steps = [0, 15, 30, 45];
  return steps.reduce((prev, curr) => 
    Math.abs(curr - m) < Math.abs(prev - m) ? curr : prev
  );
};

// Initialize from props
const initFromModel = () => {
  let date;
  if (props.modelValue) {
    // Treat as local time
    if (props.modelValue.endsWith('Z')) {
        date = new Date(props.modelValue);
    } else {
        date = new Date(props.modelValue); // Browsers handle ISO mostly fine, but let's be safe
    }
  } else {
    date = new Date();
  }

  if (isNaN(date.getTime())) date = new Date();

  currentValues.value = {
    year: date.getFullYear(),
    month: date.getMonth() + 1,
    day: date.getDate(),
    hour: date.getHours(),
    minute: roundMinute(date.getMinutes())
  };

  scrollToCurrent();
};

const scrollToCurrent = () => {
  nextTick(() => {
    Object.keys(columns.value).forEach(key => {
      const container = containerRefs.value[key];
      const value = currentValues.value[key];
      const options = getOptions(key);
      const index = options.findIndex(o => o.value === value);
      
      if (container && index !== -1) {
        // Item height is 2.5rem (h-10 = 40px)
        container.scrollTop = index * 40;
      }
    });
  });
};

const updateModel = () => {
  const { year, month, day, hour, minute } = currentValues.value;
  
  // Important: ensure day doesn't exceed new month max
  const maxDay = new Date(year, month, 0).getDate();
  if (day > maxDay) {
      currentValues.value.day = maxDay;
  }
  
  const pad = n => n.toString().padStart(2, '0');
  
  if (props.mode === 'date') {
      const isoDate = `${year}-${pad(month)}-${pad(currentValues.value.day)}`;
      emit('update:modelValue', isoDate);
  } else {
      // Use local time construction
      const isoLocal = `${year}-${pad(month)}-${pad(currentValues.value.day)}T${pad(hour)}:${pad(minute)}:00`;
      emit('update:modelValue', isoLocal);
  }
};

// Scroll Event Logic
const onScroll = (key) => {
  if (isScrolling.value[key]) return;
  
  const container = containerRefs.value[key];
  if (!container) return;

  const scrollTop = container.scrollTop;
  const index = Math.round(scrollTop / 40);
  const options = getOptions(key);
  
  if (options[index]) {
    const newValue = options[index].value;
    if (currentValues.value[key] !== newValue) {
      currentValues.value[key] = newValue;
      updateModel();
    }
  }
};

const onTouchStart = (key) => {
  isScrolling.value[key] = true;
};

const onTouchEnd = (key) => {
  isScrolling.value[key] = false;
  // Trigger final alignment
  onScroll(key);
};

const selectOption = (key, value) => {
  currentValues.value[key] = value;
  scrollToCurrent();
  updateModel();
};

watch(() => props.modelValue, (newVal) => {
  // Only update if significantly different to avoid loop
  if (!newVal) return;
  
  // Simple check: if current internal state matches formatted input, ignore
  // But parsing is tricky. Let's just re-init if outside interaction changes it.
  // For now, rely on init logic or user interaction.
  // To avoid jitter during scroll updates, we might ignore updates *we* caused.
});

onMounted(() => {
  initFromModel();
});

</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
