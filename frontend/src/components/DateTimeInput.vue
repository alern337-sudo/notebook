<template>
  <div class="w-full relative group">
    <Input
      ref="inputRef"
      v-model="displayValue"
      :class="[
        error ? 'border-red-500 focus-visible:ring-red-500' : '',
        size === 'small' ? 'h-8 text-xs' : ''
      ]"
      placeholder="placeholderText"
      @blur="handleBlur"
      @keydown.enter.prevent="handleEnter"
      @input="handleInput"
    />
    <div v-if="error" class="text-[10px] text-red-500 mt-0.5 absolute -bottom-4 left-0 whitespace-nowrap bg-white px-1 z-10 shadow-sm border rounded border-red-100">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue';
import Input from '@/components/ui/input/Input.vue';

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'default'
  },
  type: {
    type: String,
    default: 'datetime', // 'datetime' or 'date'
    validator: (value) => ['datetime', 'date'].includes(value)
  }
});

const emit = defineEmits(['update:modelValue']);

const displayValue = ref('');
const error = ref('');
const inputRef = ref(null);

const placeholderText = computed(() => {
  return props.type === 'date' ? 'YYYYMMDD' : 'YYYYMMDDHHmm';
});

// Format: YYYYMMDDHHmm (12 digits)
const FORMAT_DATETIME_REGEX = /^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})$/;
// Format: YYYYMMDD (8 digits)
const FORMAT_DATE_REGEX = /^(\d{4})(\d{2})(\d{2})$/;

// Rounding logic: 00, 15, 30, 45. Midpoint (7, 8) rounds up.
// Remainder >= 7 rounds up.
const roundMinutes = (minutes) => {
  const remainder = minutes % 15;
  if (remainder === 0) return minutes;
  
  if (remainder >= 7) {
    return minutes + (15 - remainder);
  } else {
    return minutes - remainder;
  }
};

const parseAndFormat = (input) => {
  if (!input) return null;
  
  let y, m, d, h, min;
  
  if (props.type === 'date') {
    const match = input.match(FORMAT_DATE_REGEX);
    if (!match) {
      return { valid: false, error: '格式应为 YYYYMMDD' };
    }
    [_, y, m, d] = match.map(Number);
    h = 0;
    min = 0;
  } else {
    const match = input.match(FORMAT_DATETIME_REGEX);
    if (!match) {
      return { valid: false, error: '格式应为 YYYYMMDDHHmm' };
    }
    [_, y, m, d, h, min] = match.map(Number);
  }
  
  // Date Validity Check
  const date = new Date(y, m - 1, d, h, min);
  if (
    date.getFullYear() !== y ||
    date.getMonth() !== m - 1 ||
    date.getDate() !== d ||
    date.getHours() !== h ||
    date.getMinutes() !== min
  ) {
     return { valid: false, error: '日期或时间数值无效' };
  }

  let roundedMin = min;
  
  // Only round minutes for datetime type
  if (props.type === 'datetime') {
    // Round Minutes
    roundedMin = roundMinutes(min);
    
    // Handle overflow (e.g. 53 -> 60 -> next hour)
    if (roundedMin === 60) {
      roundedMin = 0;
      date.setHours(date.getHours() + 1);
      // Re-check overflow (e.g. 23:53 -> 00:00 next day)
      y = date.getFullYear();
      m = date.getMonth() + 1;
      d = date.getDate();
      h = date.getHours();
    }
  }
  
  // Format Back to String
  const pad = (n) => String(n).padStart(2, '0');
  let formatted;
  if (props.type === 'date') {
    formatted = `${y}${pad(m)}${pad(d)}`;
  } else {
    formatted = `${y}${pad(m)}${pad(d)}${pad(h)}${pad(roundedMin)}`;
  }
  
  const iso = `${y}-${pad(m)}-${pad(d)}T${pad(h)}:${pad(roundedMin)}:00`;
  
  return { valid: true, formatted, iso };
};

// Convert ISO (from model) to Display
const isoToDisplay = (iso) => {
  if (!iso) return '';
  const date = new Date(iso);
  if (isNaN(date.getTime())) return '';
  
  const pad = (n) => String(n).padStart(2, '0');
  
  if (props.type === 'date') {
    return `${date.getFullYear()}${pad(date.getMonth() + 1)}${pad(date.getDate())}`;
  }
  
  return `${date.getFullYear()}${pad(date.getMonth() + 1)}${pad(date.getDate())}${pad(date.getHours())}${pad(date.getMinutes())}`;
};

watch(() => props.modelValue, (val) => {
  // Only update if display value is empty or significantly different (to avoid cursor jumps if we were typing, but here we update on blur mainly)
  // Actually, for two-way binding, we should update display if model changes externally.
  // But if user is typing, we shouldn't overwrite.
  // Simple approach: if valid ISO, update display.
  // We can check if the current display parses to the same ISO.
  if (!val) {
    if (!displayValue.value) return; // already empty
    // If model cleared externally, clear display?
    // Maybe.
  } else {
    const formatted = isoToDisplay(val);
    if (formatted !== displayValue.value) {
       // Only overwrite if not focused? Or if logic dictates.
       // Standard pattern: Sync model -> view
       displayValue.value = formatted;
    }
  }
}, { immediate: true });

const handleBlur = () => {
  processInput();
};

const handleEnter = () => {
  processInput();
  inputRef.value?.$el.querySelector('input')?.blur(); // Remove focus to confirm visual state
};

const handleInput = () => {
  if (error.value) error.value = ''; // Clear error on typing
};

const processInput = () => {
  if (!displayValue.value.trim()) {
    error.value = '';
    emit('update:modelValue', '');
    return;
  }

  const result = parseAndFormat(displayValue.value);
  if (!result.valid) {
    error.value = result.error;
    // Do not emit invalid value, or emit null?
    // User requirement: "block submission". 
    // If we don't emit, parent model stays old value.
    // But visual shows invalid string.
    return;
  }

  // Valid
  error.value = '';
  displayValue.value = result.formatted; // Echo back formatted/rounded
  emit('update:modelValue', result.iso);
};
</script>
