<template>
  <div class="container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>备忘录</span>
          <el-button class="button" type="primary" @click="openCreateDialog">添加备忘</el-button>
        </div>
      </template>
      
      <el-table :data="memos" style="width: 100%" v-loading="loading">
        <el-table-column prop="title" label="标题" width="180" />
        <el-table-column prop="content" label="内容" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button size="small" @click="openEditDialog(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑备忘' : '新建备忘'" width="30%">
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="form.content" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import api from './api';

const memos = ref([]);
const loading = ref(false);
const dialogVisible = ref(false);
const isEdit = ref(false);
const form = ref({
  id: null,
  title: '',
  content: ''
});

const fetchMemos = async () => {
  loading.value = true;
  try {
    const response = await api.get('/memos/');
    memos.value = response.data;
  } catch (error) {
    ElMessage.error('获取备忘录失败');
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleString();
};

const openCreateDialog = () => {
  isEdit.value = false;
  form.value = { title: '', content: '' };
  dialogVisible.value = true;
};

const openEditDialog = (row) => {
  isEdit.value = true;
  form.value = { ...row };
  dialogVisible.value = true;
};

const handleSubmit = async () => {
  if (!form.value.title || !form.value.content) {
    ElMessage.warning('请填写标题和内容');
    return;
  }

  try {
    if (isEdit.value) {
      await api.put(`/memos/${form.value.id}`, form.value);
      ElMessage.success('更新成功');
    } else {
      await api.post('/memos/', form.value);
      ElMessage.success('创建成功');
    }
    dialogVisible.value = false;
    fetchMemos();
  } catch (error) {
    ElMessage.error('操作失败');
    console.error(error);
  }
};

const handleDelete = (id) => {
  ElMessageBox.confirm('确定要删除这条备忘吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await api.delete(`/memos/${id}`);
      ElMessage.success('删除成功');
      fetchMemos();
    } catch (error) {
      ElMessage.error('删除失败');
    }
  }).catch(() => {});
};

onMounted(() => {
  fetchMemos();
});
</script>

<style scoped>
.container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
