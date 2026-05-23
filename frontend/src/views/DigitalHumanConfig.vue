<template>
  <div class="config-container">
    <el-card class="box-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>数字人形象与交互配置</span>
        </div>
      </template>
      
      <el-form :model="form" label-width="120px" style="max-width: 600px">
        <el-form-item label="外观风格">
          <el-select v-model="form.avatar_style" placeholder="选择数字人形象" style="width: 100%">
            <el-option label="古风女导游 (推荐灵山)" value="古风导游" />
            <el-option label="现代职业装" value="现代职业" />
            <el-option label="卡通3D形象" value="卡通形象" />
          </el-select>
        </el-form-item>

        <el-form-item label="发音音色 (TTS)">
          <el-select v-model="form.voice_type" placeholder="选择发音风格" style="width: 100%">
            <el-option label="温柔亲切女声" value="温柔女声" />
            <el-option label="沉稳专业男声" value="沉稳男声" />
            <el-option label="活泼童声" value="活泼童声" />
          </el-select>
        </el-form-item>

        <el-form-item label="默认开场白">
          <el-input 
            v-model="form.greeting_text" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入数字人欢迎游客时的开场白"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="saveConfig" :loading="submitLoading">保存配置</el-button>
          <el-button @click="fetchConfig">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const loading = ref(false)
const submitLoading = ref(false)

const form = reactive({
  avatar_style: '',
  voice_type: '',
  greeting_text: ''
})

const fetchConfig = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/v1/config')
    if (res.data.code === 200 && res.data.data) {
      form.avatar_style = res.data.data.avatar_style
      form.voice_type = res.data.data.voice_type
      form.greeting_text = res.data.data.greeting_text
    }
  } catch (error) {
    ElMessage.error('获取配置失败')
  } finally {
    loading.value = false
  }
}

const saveConfig = async () => {
  submitLoading.value = true
  try {
    const res = await axios.post('/api/v1/config', form)
    if (res.data.code === 200) {
      ElMessage.success('配置保存成功！数字人前端将同步生效。')
    }
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  fetchConfig()
})
</script>

<style scoped>
.config-container {
  padding: 10px;
}
.box-card {
  margin-bottom: 20px;
}
.card-header {
  font-weight: bold;
  font-size: 16px;
}
</style>