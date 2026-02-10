<template>
  <div class="space-y-6">
    <!-- Header / Actions -->
    <div class="flex flex-col space-y-4">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <h2 class="text-2xl font-bold tracking-tight">消耗品</h2>
        <div class="flex items-center gap-2">
          <Button variant="outline" @click="exportData" class="h-10 px-4 bg-white text-zinc-950 border-zinc-200 hover:bg-zinc-100 gap-2 rounded-lg">
            <Download class="h-4 w-4" />
            导出数据
          </Button>
        </div>
      </div>
      
      <!-- Category Filter -->
      <div class="hidden md:flex gap-2 border-b border-zinc-200 pb-1 overflow-x-auto">
        <button
          v-for="cat in ['全部', '车', '家', '食物']"
          :key="cat"
          @click="currentFilter = cat"
          :class="[
            'px-4 py-2 text-sm font-medium border-b-2 transition-colors whitespace-nowrap',
            currentFilter === cat
              ? 'border-zinc-900 text-zinc-900'
              : 'border-transparent text-zinc-500 hover:text-zinc-700 hover:border-zinc-300'
          ]"
        >
          {{ cat }}
        </button>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="grid gap-6 md:grid-cols-12">
      <!-- Left: List -->
      <div class="md:col-span-12 lg:col-span-8 space-y-4">
        <div v-if="items.length === 0" class="flex flex-col items-center justify-center py-16 text-center text-muted-foreground border rounded-lg bg-card/50 border-dashed">
          <div class="rounded-full bg-muted/30 p-4 mb-4">
            <PackageOpen class="h-8 w-8 opacity-50" />
          </div>
          <p class="text-lg font-medium">暂无消耗品记录</p>
          <p class="text-sm mt-1">点击右上角添加新的消耗品</p>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4" v-auto-animate>
          <div 
            v-for="item in sortedItems" 
            :key="item.id" 
            @click="editItem(item)"
            class="group relative flex flex-col justify-between rounded-lg border bg-card text-card-foreground shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer"
          >
            <div class="p-4 space-y-3">
              <div class="flex items-start justify-between gap-2">
                <div class="space-y-1">
                  <h3 class="font-semibold leading-tight">{{ item.name }}</h3>
                  <div class="flex items-center gap-2 flex-wrap">
                    <Badge variant="outline" :class="getCategoryBadgeClass(item.category)">
                      {{ item.category || '其他' }}
                    </Badge>
                    <p v-if="item.category !== '车'" class="text-xs text-muted-foreground">上次更换: {{ formatDate(item.last_replaced) }}</p>
                  </div>
                  
                  <!-- Car Stats Row -->
                  <div v-if="item.category === '车'" class="flex items-center gap-2 px-1">
                    <span class="text-xs font-semibold text-purple-800">
                       {{ ((item.current_mileage && item.mileage) ? (item.current_mileage - item.mileage) : 0) }} km
                    </span>
                    <span class="text-xs text-zinc-300">|</span>
                    <span class="text-xs font-semibold text-purple-800">
                       {{ getDaysUsed(item.last_replaced) }} 天
                    </span>
                  </div>
                </div>
                <Badge :class="[getStatusClass(item), 'whitespace-nowrap']" variant="outline">
                  {{ getStatusText(item) }}
                </Badge>
              </div>

              <div class="flex items-center justify-between text-sm">
                <div class="flex flex-col">
                   <span class="text-xs text-muted-foreground">预计到期</span>
                   <span class="font-medium">{{ calculateExpiry(item.last_replaced, item.lifespan) }}</span>
                </div>
                <div class="text-right">
                   <span class="text-2xl font-bold" :class="getDaysColor(item)">
                     {{ getDaysRemaining(item) }}
                   </span>
                   <span class="text-xs text-muted-foreground ml-1">天剩余</span>
                </div>
              </div>
            </div>

            <!-- Actions Footer -->
            <div class="p-3 bg-muted/20 flex items-center justify-center rounded-b-lg border-t">
               <Button 
                 class="w-full bg-zinc-900 text-zinc-50 hover:bg-zinc-800 h-11 text-base font-medium shadow-sm" 
                 @click.stop="openReplaceDialog(item)"
               >
                 <RefreshCw class="h-5 w-5 mr-2" />
                 记录更换
               </Button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Dialog -->
    <DialogRoot v-model:open="dialogOpen">
      <DialogPortal>
        <DialogOverlay class="fixed inset-0 z-50 bg-black/80" />
        <DialogContent class="fixed left-[50%] top-[50%] z-50 grid w-[calc(100%-2rem)] max-w-2xl translate-x-[-50%] translate-y-[-50%] gap-4 border bg-white p-6 shadow-lg rounded-lg text-zinc-950 max-h-[85vh] overflow-y-auto">
          <DialogTitle class="text-lg font-semibold">
            {{ isEdit ? '编辑消耗品' : '添加消耗品' }}
          </DialogTitle>
          
          <div class="grid gap-4 py-4">
            <div class="grid gap-2">
              <label class="text-sm font-medium">分类 <span class="text-destructive">*</span></label>
              <div class="flex gap-2">
                <button
                  type="button"
                  v-for="cat in ['车', '家', '食物']"
                  :key="cat"
                  @click="form.category = cat"
                  :class="[
                    'flex-1 py-2 px-3 rounded-lg border text-sm font-medium transition-all',
                    form.category === cat 
                      ? 'bg-zinc-900 text-zinc-50 border-zinc-900 shadow-sm' 
                      : 'bg-white border-zinc-200 text-zinc-600 hover:bg-zinc-50'
                  ]"
                >
                  {{ cat }}
                </button>
              </div>
            </div>

            <div class="grid gap-2">
              <label class="text-sm font-medium">消耗品名称 <span class="text-destructive">*</span></label>
              <Input v-model="form.name" placeholder="例如：电动牙刷头" class="bg-white text-zinc-950 border-zinc-200" />
            </div>

            <div class="grid gap-2">
              <label class="text-sm font-medium">规格型号</label>
              <Input v-model="form.model_spec" placeholder="例如：HX6013" class="bg-white text-zinc-950 border-zinc-200" />
            </div>
            
            <div class="grid gap-2">
              <label class="text-sm font-medium">上次更换日期</label>
              <div 
                class="flex h-10 w-full items-center justify-between rounded-md border border-zinc-200 bg-white px-3 py-2 text-sm ring-offset-background cursor-pointer hover:bg-zinc-50"
                @click="openTimePicker(form.last_replaced, (v) => form.last_replaced = v)"
              >
                <span>{{ form.last_replaced ? formatDate(form.last_replaced) : '选择日期' }}</span>
                <CalendarIcon class="h-4 w-4 opacity-50" />
              </div>
            </div>

            <div class="grid gap-2" v-if="form.category === '车'">
              <label class="text-sm font-medium">更换时公里数 (km)</label>
              <Input type="number" v-model.number="form.mileage" class="bg-white text-zinc-950 border-zinc-200" />
            </div>
            
            <div class="grid gap-2">
              <label class="text-sm font-medium">可用天数 (天)</label>
              <Input type="number" v-model.number="form.lifespan" min="1" class="bg-white text-zinc-950 border-zinc-200" />
            </div>

            <div class="grid gap-2">
              <label class="text-sm font-medium">预计到期日期</label>
              <div 
                class="flex h-10 w-full items-center justify-between rounded-md border border-zinc-200 bg-white px-3 py-2 text-sm ring-offset-background cursor-pointer hover:bg-zinc-50"
                @click="openTimePicker(form.expiry_date, (v) => form.expiry_date = v)"
              >
                <span>{{ form.expiry_date ? formatDate(form.expiry_date) : '选择日期' }}</span>
                <CalendarIcon class="h-4 w-4 opacity-50" />
              </div>
            </div>
          </div>

          <div class="flex justify-between items-center mt-6">
            <div class="flex gap-2">
               <Button v-if="isEdit" variant="ghost" size="icon" @click="confirmDelete({...form, id: editingId})" class="h-10 w-10 text-destructive hover:bg-destructive/10 rounded-full" title="删除">
                 <Trash2 class="h-5 w-5" />
               </Button>
               <Button variant="outline" type="button" @click="resetForm" v-if="!isEdit" class="h-10 px-4 text-zinc-600 border-zinc-200 hover:bg-zinc-100">
                  重置
               </Button>
            </div>
            
            <div class="flex gap-3">
              <Button variant="outline" @click="dialogOpen = false" class="h-10 px-4 bg-white text-zinc-950 border-zinc-200 hover:bg-zinc-100">取消</Button>
              <Button @click="saveItem" class="h-10 px-4 bg-zinc-900 text-zinc-50 hover:bg-zinc-900/90">保存</Button>
            </div>
          </div>

          <DialogClose class="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground text-zinc-500 hover:text-zinc-900">
            <X class="h-4 w-4" />
            <span class="sr-only">Close</span>
          </DialogClose>
        </DialogContent>
      </DialogPortal>
    </DialogRoot>

    <!-- Replace Dialog -->
    <DialogRoot v-model:open="replaceDialogOpen">
      <DialogPortal>
        <DialogOverlay class="fixed inset-0 z-50 bg-black/80" />
        <DialogContent class="fixed left-[50%] top-[50%] z-50 grid w-[calc(100%-2rem)] max-w-xl translate-x-[-50%] translate-y-[-50%] gap-4 border bg-white p-6 shadow-lg rounded-lg text-zinc-950 max-h-[85vh] overflow-y-auto">
          <DialogTitle class="text-lg font-semibold">记录更换</DialogTitle>
          <div class="grid gap-4 py-4">
            <div class="grid gap-2">
              <label class="text-sm font-medium">更换时间</label>
              <div 
                class="flex h-10 w-full items-center justify-between rounded-md border border-zinc-200 bg-white px-3 py-2 text-sm ring-offset-background cursor-pointer hover:bg-zinc-50"
                @click="openTimePicker(replaceForm.replacedAt, (v) => replaceForm.replacedAt = v)"
              >
                <span>{{ replaceForm.replacedAt ? formatDate(replaceForm.replacedAt) : '选择日期' }}</span>
                <CalendarIcon class="h-4 w-4 opacity-50" />
              </div>
            </div>
            <div v-if="replaceForm.isCar" class="grid gap-2">
              <label class="text-sm font-medium">当前公里数 (km)</label>
              <Input type="number" v-model.number="replaceForm.mileage" min="0" class="bg-white text-zinc-950 border-zinc-200" />
            </div>
            <div class="grid gap-2">
              <label class="text-sm font-medium">备注</label>
              <Input v-model="replaceForm.note" placeholder="可选备注" class="bg-white text-zinc-950 border-zinc-200" />
            </div>
          </div>
          <div class="flex justify-end gap-3">
            <Button variant="outline" @click="replaceDialogOpen = false" class="h-10 px-4 bg-white text-zinc-950 border-zinc-200 hover:bg-zinc-100">取消</Button>
            <Button @click="confirmReplace" class="h-10 px-4 bg-zinc-900 text-zinc-50 hover:bg-zinc-900/90">确认更换</Button>
          </div>
          <DialogClose class="absolute right-4 top-4 rounded-sm opacity-70 hover:opacity-100">
            <X class="h-4 w-4" />
          </DialogClose>
        </DialogContent>
      </DialogPortal>
    </DialogRoot>

    <!-- Floating Action Button -->
    <Button 
      class="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg z-50 p-0" 
      @click="openAddDialog"
    >
      <Plus class="h-6 w-6" />
    </Button>

    <!-- Delete Alert -->
    <AlertDialog v-model:open="alertState.open">
      <AlertDialogContent class="w-[calc(100%-2rem)] max-w-lg gap-6 border bg-white p-6 shadow-lg rounded-lg md:w-full">
        <AlertDialogHeader>
          <AlertDialogTitle class="text-xl font-semibold text-center">{{ alertState.title }}</AlertDialogTitle>
          <AlertDialogDescription class="text-base text-muted-foreground text-center">
            {{ alertState.content }}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter class="flex justify-center w-full mt-2 grid grid-cols-2 gap-4">
          <AlertDialogCancel @click="alertState.open = false" class="rounded-lg font-medium bg-white text-zinc-950 border border-zinc-200 hover:bg-zinc-100 h-11 px-6 mt-0">取消</AlertDialogCancel>
          <AlertDialogAction @click="executeDelete" class="rounded-lg font-medium bg-zinc-900 text-zinc-50 hover:bg-zinc-900/90 h-11 px-6">删除</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>

    <!-- Time Picker Dialog -->
    <DialogRoot v-model:open="timePickerOpen">
      <DialogPortal>
        <DialogOverlay class="fixed inset-0 z-50 bg-black/80" />
        <DialogContent class="fixed left-[50%] top-[50%] z-50 grid w-[calc(100%-2rem)] max-w-sm translate-x-[-50%] translate-y-[-50%] gap-4 border bg-white p-6 shadow-lg sm:rounded-lg text-zinc-950">
          <DialogTitle class="text-lg font-semibold">
            选择日期
          </DialogTitle>
          
          <div class="py-4 flex justify-center">
            <DateTimeWheelPicker 
              v-model="tempTimeValue" 
              mode="date"
            />
          </div>

          <div class="flex justify-end gap-3">
            <Button variant="outline" @click="timePickerOpen = false" class="h-10 px-4 bg-white text-zinc-950 border-zinc-200 hover:bg-zinc-100">取消</Button>
            <Button @click="handleTimeConfirm" class="h-10 px-4 bg-zinc-900 text-zinc-50 hover:bg-zinc-900/90">确定</Button>
          </div>
        </DialogContent>
      </DialogPortal>
    </DialogRoot>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import { vAutoAnimate } from '@formkit/auto-animate/vue';
import * as XLSX from 'xlsx';
import api from '@/api';
import Button from '@/components/ui/button/Button.vue';
import Input from '@/components/ui/input/Input.vue';
import Badge from '@/components/ui/badge/Badge.vue';
import DateTimeWheelPicker from '@/components/DateTimeWheelPicker.vue';
import { 
  DialogRoot, 
  DialogPortal,
  DialogOverlay,
  DialogContent,
  DialogTitle,
  DialogClose,
} from 'radix-vue';
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogCancel,
  AlertDialogAction,
} from '@/components/ui/alert-dialog';
import { Plus, Download, Edit2, Trash2, X, PackageOpen, RefreshCw, Info, Calendar as CalendarIcon } from 'lucide-vue-next';

// State
const items = ref([]);
const dialogOpen = ref(false);
const typeSelectionOpen = ref(false);
const replaceDialogOpen = ref(false);
const isEdit = ref(false);
const editingId = ref(null);

// Time Picker State
const timePickerOpen = ref(false);
const tempTimeValue = ref('');
const timeConfirmCallback = ref(null);

const openTimePicker = (currentValue, callback) => {
  tempTimeValue.value = ensureDateTime(currentValue);
  timeConfirmCallback.value = callback;
  timePickerOpen.value = true;
};

const handleTimeConfirm = () => {
  if (timeConfirmCallback.value) {
    // For date mode, we typically get YYYY-MM-DD from the wheel picker if in date mode,
    // or ISO string. The DateTimeWheelPicker 'date' mode returns YYYY-MM-DD.
    // ensureDateTime returns ISO for initialization, but let's check what the picker emits.
    // The picker emits the string value.
    timeConfirmCallback.value(tempTimeValue.value.split('T')[0]); 
  }
  timePickerOpen.value = false;
};

const form = ref({
  name: '',
  tag: '耗材',
  category: '家',
  last_replaced: '',
  lifespan: 30,
  expiry_date: '',
  mileage: ''
});

const replaceForm = ref({
  id: null,
  replacedAt: '',
  mileage: '',
  note: '',
  isCar: false
});

const badgeTextClass = 'inline-flex items-center px-2.5 py-0.5 text-xs font-semibold';

const alertState = ref({
  open: false,
  title: '',
  content: '',
  itemToDelete: null
});

// Load data
const fetchItems = async () => {
  try {
    const res = await api.get('/consumables/');
    items.value = res.data;
  } catch (error) {
    console.error('Failed to fetch consumables', error);
  }
};

onMounted(() => {
  fetchItems();
});

// Helpers
const calculateExpiry = (start, days) => {
  if (!start || !days) return '-';
  const date = new Date(start);
  date.setDate(date.getDate() + parseInt(days));
  return date.toISOString().split('T')[0];
};

const getDaysRemaining = (item) => {
  const expiry = new Date(calculateExpiry(item.last_replaced, item.lifespan));
  const today = new Date();
  today.setHours(0, 0, 0, 0); 
  const diffTime = expiry - today;
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24)); 
};

const getStatus = (item) => {
  if (item.status && item.status !== '正常') return 'urgent'; // Trust server status if set
  const days = getDaysRemaining(item);
  if (days <= 3) return 'urgent';
  if (days <= 7) return 'soon';
  return 'normal';
};

const getStatusText = (item) => {
  if (item.status && item.status !== '正常') return item.status;
  const status = getStatus(item);
  if (status === 'urgent') return item.days < 0 ? '已过期' : '紧急';
  if (status === 'soon') return '即将到期';
  return '正常';
};

const getStatusClass = (item) => {
  const status = getStatus(item);
  if (status === 'urgent') return 'bg-red-100 text-red-800 border-red-200';
  if (status === 'soon') return 'bg-yellow-100 text-yellow-800 border-yellow-200';
  return 'bg-green-100 text-green-800 border-green-200';
};

const getDaysColor = (item) => {
  const status = getStatus(item);
  if (status === 'urgent') return 'text-red-600';
  if (status === 'soon') return 'text-yellow-600';
  return 'text-green-600';
};

const getDaysUsed = (dateStr) => {
  if (!dateStr) return 0;
  const start = new Date(dateStr);
  const today = new Date();
  today.setHours(0,0,0,0);
  const diff = today - start;
  return Math.floor(diff / (1000 * 60 * 60 * 24));
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  return dateStr.split('T')[0];
};

const ensureDateTime = (val) => {
  if (!val) return '';
  if (val.includes('T')) return val;
  return `${val}T00:00:00`;
};

// Date Sync Logic
watch(() => [form.value.last_replaced, form.value.lifespan], ([newDate, newLifespan]) => {
  if (newDate && newLifespan && !isSyncing.value) {
    isSyncing.value = true;
    form.value.expiry_date = calculateExpiry(newDate, newLifespan);
    isSyncing.value = false;
  }
});

const isSyncing = ref(false);

watch(() => form.value.expiry_date, (newExpiry) => {
  if (newExpiry && form.value.last_replaced && !isSyncing.value) {
    isSyncing.value = true;
    const start = new Date(form.value.last_replaced);
    const end = new Date(newExpiry);
    const diffTime = end - start;
    const days = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    form.value.lifespan = days > 0 ? days : 0; 
    isSyncing.value = false;
  }
});

const props = defineProps({
  activeFilter: {
    type: String,
    default: '全部'
  }
});

const currentFilter = ref('全部');

// Sync prop to local state
watch(() => props.activeFilter, (newVal) => {
  if (newVal) {
    currentFilter.value = newVal;
  }
}, { immediate: true });

const searchQuery = ref('');

// Helper functions
const getCategoryBadgeClass = (category) => {
  switch (category) {
    case '家': return 'bg-blue-100 text-blue-800 border-blue-200';
    case '车': return 'bg-purple-100 text-purple-800 border-purple-200';
    case '食物': return 'bg-orange-100 text-orange-800 border-orange-200';
    default: return 'bg-zinc-100 text-zinc-800 border-zinc-200';
  }
};

// Computed
const filteredItems = computed(() => {
  let result = items.value;
  
  // Filter by category
  if (currentFilter.value !== '全部') {
    result = result.filter(item => item.category === currentFilter.value);
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(item => 
      item.name.toLowerCase().includes(query)
    );
  }
  return result;
});

const sortedItems = computed(() => {
  return [...filteredItems.value].sort((a, b) => {
    return getDaysRemaining(a) - getDaysRemaining(b);
  });
});

// Actions
const openAddDialog = () => {
  isEdit.value = false;
  editingId.value = null;
  resetForm();
  dialogOpen.value = true;
};

const resetForm = () => {
  const today = new Date().toISOString().split('T')[0];
  const expiry = new Date();
  expiry.setDate(expiry.getDate() + 30);
  
  form.value = {
    name: '',
    tag: '耗材', // Default/Hidden
    category: '家',
    model_spec: '',
    last_replaced: today,
    lifespan: 30,
    expiry_date: expiry.toISOString().split('T')[0],
    mileage: ''
  };
};

const editItem = (item) => {
  isEdit.value = true;
  editingId.value = item.id;
  
  let expiry = item.expiry_date;
  if (!expiry && item.last_replaced && item.lifespan) {
    expiry = calculateExpiry(item.last_replaced, item.lifespan);
  }
  
  form.value = { 
    ...item, 
    expiry_date: expiry,
    model_spec: item.model_spec || '',
    mileage: item.mileage || ''
  };
  dialogOpen.value = true;
};

const saveItem = async () => {
  await nextTick(); // Ensure any blur events have fired
  if (!form.value.name.trim()) return alert('请输入消耗品名称');
  if (!form.value.last_replaced) return alert('请选择上次更换日期');
  if (form.value.lifespan <= 0) return alert('可用天数必须为正整数');

  // Prepare payload
  const payload = { ...form.value };
  if (payload.mileage === '') {
    payload.mileage = null;
  }

  try {
    if (isEdit.value) {
      await api.put(`/consumables/${editingId.value}`, payload);
    } else {
      await api.post('/consumables/', payload);
    }
    await fetchItems();
    dialogOpen.value = false;
  } catch (error) {
    console.error(error);
    alert('保存失败');
  }
};

const confirmDelete = (item) => {
  alertState.value = {
    open: true,
    title: '确认删除',
    content: `确定要删除 "${item.name}" 吗？此操作无法撤销。`,
    itemToDelete: item
  };
};

const executeDelete = async () => {
  if (alertState.value.itemToDelete) {
    try {
      await api.delete(`/consumables/${alertState.value.itemToDelete.id}`);
      await fetchItems();
    } catch (error) {
      console.error(error);
      alert('删除失败');
    }
  }
  alertState.value.open = false;
};

// Replace Logic
const openReplaceDialog = (item) => {
  replaceForm.value = {
    id: item.id,
    replacedAt: new Date().toISOString().split('T')[0],
    mileage: item.mileage || '',
    note: '',
    isCar: item.category === '车'
  };
  replaceDialogOpen.value = true;
};

const confirmReplace = async () => {
  await nextTick(); // Ensure any blur events have fired
  if (replaceForm.value.isCar && !replaceForm.value.mileage) {
    return alert('请输入当前公里数');
  }
  try {
    await api.post(`/consumables/${replaceForm.value.id}/replace`, {
      replaced_at: replaceForm.value.replacedAt,
      mileage: replaceForm.value.mileage || null,
      note: replaceForm.value.note
    });
    await fetchItems();
    replaceDialogOpen.value = false;
    alert('更换记录已保存');
  } catch (error) {
    console.error(error);
    alert('操作失败');
  }
};

const exportData = () => {
  try {
    const dataToExport = items.value.map(item => ({
      '名称': item.name,
      '类型': item.tag || '耗材',
      '分类': item.tag === '耗材' ? (item.category || '家') : '-',
      '上次更换公里数': (item.tag === '耗材' && item.category === '车' && item.mileage) ? item.mileage : '-',
      '当前公里数': (item.tag === '耗材' && item.category === '车' && item.current_mileage) ? item.current_mileage : '-',
      '上次更换日期': formatDate(item.last_replaced),
      '可用天数': item.lifespan,
      '预计到期日期': calculateExpiry(item.last_replaced, item.lifespan),
      '剩余天数': getDaysRemaining(item),
      '状态': getStatusText(item)
    }));

    const ws = XLSX.utils.json_to_sheet(dataToExport);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "消耗品清单");
    XLSX.writeFile(wb, `消耗品清单_${new Date().toISOString().split('T')[0]}.xlsx`);
  } catch (error) {
    console.error('Export failed:', error);
    alert('导出失败，请重试');
  }
};
</script>
