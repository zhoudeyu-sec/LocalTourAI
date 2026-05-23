<template>
  <div class="kb-container">
    <!-- 顶部操作栏 -->
    <el-card class="filter-card">
      <div class="header-actions">
        <el-input
          v-model="searchQuery"
          placeholder="搜索知识标题..."
          style="width: 300px"
          clearable
          @clear="fetchData"
          @keyup.enter="fetchData"
        >
          <template #append>
            <el-button :icon="Search" @click="fetchData" />
          </template>
        </el-input>
        
        <div class="button-group">
          <el-button type="primary" :icon="Plus" @click="handleAdd">新增条目</el-button>
        </div>
      </div>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card">
      <el-table :data="tableData" v-loading="loading" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="知识标题" width="200" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.category || '通用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="详细内容" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="confirmDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          layout="total, prev, pager, next"
          :total="total"
          @current-change="fetchData"
        />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="form.id ? '编辑知识' : '新增知识'"
      width="600px"
    >
      <el-form :model="form" label-width="80px" :rules="rules" ref="formRef">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入知识点标题" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category" placeholder="请选择分类" style="width: 100%">
            <el-option label="景点介绍" value="景点介绍" />
            <el-option label="交通指南" value="交通指南" />
            <el-option label="餐饮住宿" value="餐饮住宿" />
            <el-option label="通用FAQ" value="general" />
          </el-select>
        </el-form-item>
        <el-form-item label="详细内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="6"
            placeholder="请输入数字人回答的详细文本"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitLoading">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { Search, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

// 状态变量
const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref([])
const searchQuery = ref('')
const dialogVisible = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const formRef = ref(null)

const form = reactive({
  id: null,
  title: '',
  category: 'general',
  content: ''
})

const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }]
}

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/v1/kb/list', {
      params: { 
        skip: (currentPage.value - 1) * pageSize.value, 
        limit: pageSize.value,
        keyword: searchQuery.value || undefined
      }
    })
    if (res.data.code === 200) {
      tableData.value = res.data.data.items
      total.value = res.data.data.total
    }
  } catch (error) {
    ElMessage.error('获取数据失败，请确保后端服务已启动')
  } finally {
    loading.value = false
  }
}

// 新增
const handleAdd = () => {
  form.id = null
  form.title = ''
  form.content = ''
  form.category = 'general'
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  Object.assign(form, row)
  dialogVisible.value = true
}

const kbPayload = () => ({
  title: form.title,
  content: form.content,
  category: form.category,
})

// 提交表单
const submitForm = async () => {
  await formRef.value.validate()
  submitLoading.value = true
  try {
    if (form.id) {
      await axios.put(`/api/v1/kb/update/${form.id}`, kbPayload())
    } else {
      await axios.post('/api/v1/kb/add', kbPayload())
    }
    ElMessage.success('操作成功')
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    submitLoading.value = false
  }
}

// 删除确认
const confirmDelete = (row) => {
  ElMessageBox.confirm('确定要删除这条知识吗？', '提示', {
    type: 'warning',
  }).then(async () => {
    await axios.delete(`/api/v1/kb/delete/${row.id}`)
    ElMessage.success('删除成功')
    fetchData()
  }).catch(() => {})
}

onMounted(fetchData)
</script>

<style scoped>
.kb-container { padding: 10px; }
.filter-card { margin-bottom: 20px; }
.header-actions { display: flex; justify-content: space-between; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }
</style>