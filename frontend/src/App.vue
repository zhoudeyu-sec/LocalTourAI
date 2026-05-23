<template>
  <el-config-provider :locale="zhCn">
    <el-container class="layout-container">
      <!-- 顶部导航 -->
      <el-header class="app-header">
        <div class="logo">景区数字人导游管理系统</div>
      </el-header>

      <el-container>
        <!-- 左侧菜单栏 -->
        <el-aside width="220px" class="app-aside">
          <el-menu
            :default-active="$route.path"
            router
            class="el-menu-vertical"
            background-color="#304156"
            text-color="#bfcbd9"
            active-text-color="#409eff"
          >
            <el-menu-item index="/dashboard">
              <span> 数据概览</span>
            </el-menu-item>
            <el-menu-item index="/kb">
              <span> 知识库管理</span>
            </el-menu-item>
            <el-menu-item index="/config">
              <span> 数字人配置</span>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <!-- 右侧主体内容区域 -->
        <el-main class="app-main">
          <!-- 这里很关键！用来显示路由对应的页面 -->
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </el-config-provider>
</template>

<script setup>
import { ElConfigProvider } from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
</script>

<style>
body { margin: 0; padding: 0; background-color: #f0f2f5; }
.layout-container { height: 100vh; }
.app-header {
  background-color: #1890ff; color: white; display: flex;
  align-items: center; font-size: 20px; font-weight: bold;
}
.app-aside { background-color: #304156; }
.app-main { padding: 20px; }
</style>