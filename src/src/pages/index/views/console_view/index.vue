<template>
  <div class="dashboard">
    <!-- 基本状态 -->
    <div class="card">
      <h3>基本状态</h3>
      <p>计算机名: <span class="highlight">{{ info.computerName }}</span></p>
      <p>电池: <span class="highlight">{{ info.battery }}%</span></p>
      <p>屏幕亮度: <span class="highlight">{{ info.brightness }}%</span></p>
      <p>音量: <span class="highlight">{{ info.volume }}%</span></p>
    </div>

    <!-- 性能配置 -->
    <div class="card">
      <h3>性能配置</h3>
      <p>性能模式: <span class="highlight">{{ config.mode }}</span></p>
      <p>键盘背光: <span class="highlight">{{ config.keyboardLight }}</span></p>
      <p>显卡: <span class="highlight">{{ config.gpu }}</span></p>
      <p>音量: <span class="highlight">{{ info.volume }}%</span></p>
    </div>

    <!-- 定时任务 -->
    <div class="card">
      <h3>定时任务</h3>
      <p>30分钟后: <span class="highlight">音量调节到0%</span></p>
      <p>电源断开时: <span class="highlight">刷新率60Hz</span></p>
      <p>电源插入时: <span class="highlight">刷新率120Hz</span></p>
      <p>30分钟后: <span class="highlight">使计算机休眠</span></p>
    </div>

    <!-- 宏 -->
    <div class="card">
      <h3>宏</h3>
      <p>FN&Q: <span class="highlight">狮鹫起飞</span></p>
      <p>W|A|S|D: <span class="highlight">滚轮向下10</span></p>
      <p>鼠标侧键1: <span class="highlight">左键连续</span></p>
      <p>鼠标侧键2: <span class="highlight">F键连续</span></p>
    </div>

    <!-- 底部 -->
    <div class="card full">
      <p>在线服务: <span class="highlight">在线(easy-x)</span></p>
      <p>蓝牙服务: <span class="highlight">已连接(GalaxyS24)</span></p>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'

// 模拟数据，可以通过 API 更新
const info = reactive({
  computerName: 'YOGAPRO',
  battery: 100,
  brightness: 100,
  volume: 85,
})

const config = reactive({
  mode: '野兽模式',
  keyboardLight: '高亮度',
  gpu: 'NVIDIA'
})
</script>

<style scoped>
.dashboard {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 16px;
  font-family: "Segoe UI", sans-serif;
}

.card {
  border: 1px solid #ddd;
  border-radius: 12px;
  padding: 12px 16px;
  background: #fff;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

.card.full {
  grid-column: span 2;
  text-align: center;
}

h3 {
  font-size: 16px;
  margin-bottom: 8px;
}

p {
  margin: 4px 0;
  font-size: 14px;
}

.highlight {
  color: #4a56e2;
  font-weight: 500;
}
</style>
