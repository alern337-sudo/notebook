<template>
  <div class="flex gap-2 w-full">
    <el-date-picker
      v-model="date"
      type="date"
      placeholder="选择日期"
      class="flex-1"
      value-format="YYYY-MM-DD"
      :size="size"
      :clearable="false"
      :teleported="false"
      @change="updateValue"
    />
    <el-time-select
      v-model="time"
      start="00:00"
      step="00:15"
      end="23:45"
      placeholder="选择时间"
      class="w-[140px]"
      :size="size"
      :clearable="false"
      :teleported="false"
      @change="updateValue"
    />
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { ElDatePicker, ElTimeSelect } from 'element-plus';

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'default'
  }
});

const emit = defineEmits(['update:modelValue']);

const date = ref('');
const time = ref('');

const parseValue = (val) => {
  if (!val) {
    date.value = '';
    time.value = '';
    return;
  }
  const [d, t] = val.split('T');
  date.value = d || '';
  time.value = t ? t.slice(0, 5) : ''; // HH:mm
};

watch(() => props.modelValue, (val) => {
  parseValue(val);
}, { immediate: true });

const updateValue = () => {
  if (date.value && time.value) {
    emit('update:modelValue', `${date.value}T${time.value}`);
  } else if (date.value) {
    // If only date is selected, maybe default to 00:00 or keep it partial?
    // Native datetime-local requires both.
    // Let's assume 00:00 if time is missing but date is present?
    // Or just emit what we have if we want partial support, but for strict datetime-local replacement:
    emit('update:modelValue', `${date.value}T${time.value || '00:00'}`);
    if (!time.value) time.value = '00:00';
  } else {
    emit('update:modelValue', '');
  }
};
</script>
