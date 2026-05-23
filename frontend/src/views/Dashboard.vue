<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card shadow="hover" class="data-card">
          <div class="title">知识库总数</div>
          <div class="value">{{ stats.total_kb_count }} <span class="unit">条</span></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="data-card">
          <div class="title">累计对话人次</div>
          <div class="value">{{ stats.total_chat_count }} <span class="unit">次</span></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="data-card">
          <div class="title">平均响应时间</div>
          <div class="value">{{ stats.avg_response_time }} <span class="unit">ms</span></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- ECharts 图表区域 -->
    <el-row style="margin-top: 20px;">
      <el-col :span="24">
        <el-card shadow="always">
          <div ref="chartRef" style="width: 100%; height: 400px;"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

const stats = ref({
  total_kb_count: 0,
  total_chat_count: 0,
  avg_response_time: 0
})
const chartRef = ref(null)

const fetchStats = async () => {
  try {
    const res = await axios.get('/api/v1/stats/overview')
    if (res.data.code === 200) {
      stats.value = res.data.data
    }
  } catch (error) {
    console.error("获取统计数据失败", error)
  }
}

const initChart = () => {
  const myChart = echarts.init(chartRef.value)
  // 模拟数据，实际可从后端获取真实统计数据
  const option = {
    title: { text: '近七日对话量趋势' },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    },
    yAxis: { type: 'value' },
    series: [
      {
        data: [120, 132, 101, 134, 390, 830, 920],
        type: 'line',
        smooth: true,
        areaStyle: { color: 'rgba(24,144,255,0.2)' },
        itemStyle: { color: '#1890ff' }
      }
    ]
  }
  myChart.setOption(option)
  window.addEventListener('resize', () => myChart.resize())
}

onMounted(async () => {
  await fetchStats()
  if (chartRef.value) {
    initChart()
  }
})
</script>

<style scoped>
.data-card {
  text-align: center;
  padding: 20px 0;
}
.data-card .title {
  font-size: 16px;
  color: #909399;
  margin-bottom: 10px;
}
.data-card .value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
}
.data-card .unit {
  font-size: 14px;
  font-weight: normal;
  color: #909399;
}
</style>