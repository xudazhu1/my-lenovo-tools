<template>
  <div class="dashboard">
    <!-- 基本状态 -->
    <div class="card">
      <h3>定时任务</h3>
      <p>计算机名: <span class="highlight">{{ info.computerName }}</span></p>
      <p>电池: <span class="highlight">{{ info.battery }}</span></p>
      <p>启动任务: <span class="highlight">
        <el-button round size="mini" @click="startTask">启动</el-button>
      </span></p>
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
import { reactive, ref, onMounted } from 'vue'
import {ElMessage} from "element-plus";

// 模拟数据，可以通过 API 更新
const values = reactive({
  isPyWeb: false,
})

// 模拟数据，可以通过 API 更新
const info = reactive({
  computerName: 'UNKOWN', // 计算机名
  battery: "0", // 电池
  brightness: 0, // 屏幕亮度
  volume: 0, // 音量
  muted: false, // 静音
})

const config = reactive({
  mode: '野兽模式',
  keyboardLight: '高亮度',
  gpu: 'NVIDIA',
})

function startTask() {
  if (!values.isPyWeb ) {
    ElMessage.success('不是PyWeb环境!')
    return
  }
  window.pywebview.api.task_restart()
}

async function refreshComputerInfo() {
  if (!values.isPyWeb ) {
    ElMessage.success('不是PyWeb环境!')
    return
  }
  info.computerName = await window.pywebview.api.pc_get_computer_name()
  let batteryInfo = await window.pywebview.api.pc_get_battery()
  console.log(batteryInfo)
  if (batteryInfo.exist) {
    info.battery = batteryInfo.percent + "%"
  } else {
    info.battery = "No battery detected"
  }
  info.brightness = await window.pywebview.api.pc_get_brightness()
  info.volume = await window.pywebview.api.pc_get_volume() * 100
  info.muted = await window.pywebview.api.pc_is_muted()
}


// 更新亮度
async function updateBrightness() {
  if (!values.isPyWeb ) {
    ElMessage.success('不是PyWeb环境!')
    return
  }
  await window.pywebview.api.pc_set_brightness(info.brightness)
}

// 更新音量
async function updateVolume() {
  if (!values.isPyWeb ) {
    ElMessage.success('不是PyWeb环境!')
    return
  }
  await window.pywebview.api.pc_set_volume(info.volume / 100)
}

// 切换静音
async function toggleMute() {
  if (!values.isPyWeb ) {
    ElMessage.success('不是PyWeb环境!')
    return
  }
  if (info.muted) {
    await window.pywebview.api.pc_mute(false)
    info.muted = false
  } else {
    await window.pywebview.api.pc_mute(true)
    info.muted = true
  }
}


// 生命周期
onMounted(() => {
  console.log('组件挂载完成')
  if ( window && window.pywebview && window.pywebview.api) {
    values.isPyWeb = true
  }
  refreshComputerInfo()
})

</script>

<style scoped>
.mute-btn {
  width: 23px;
}


.volume-line2 {
  display: flex;          /* 开启弹性布局 */
  align-items: center;    /* 垂直居中对齐 */
  gap: 8px;               /* 控制滑块和按钮之间的间距，可根据需要调整 */
}

.slider.volume {
  flex: 1;                /* 滑块占满剩余空间 */
}

.highlight {
  font-weight: bold;
  color: #0078d7; /* Windows蓝 */
}

.slider-group {
  margin: 12px 0;
}


.mute-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  margin-right: 8px;
}

.slider {
  flex: 1;
  height: 6px;
  border-radius: 5px;
  background: #ddd;
  outline: none;
}
.slider.brightness::-webkit-slider-thumb {
  background: #facc15; /* 黄色代表亮度 */
}
.slider.volume::-webkit-slider-thumb {
  background: #3b82f6; /* 蓝色代表音量 */
}


.dashboard {
  /*display: grid;*/
  /*grid-template-columns: repeat(2, 1fr);*/
  display: flex;
  flex-wrap: wrap;
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
  position: relative;
  flex: 1 1 calc(33.33% - 16px); /* 默认每行3个卡片 */
  min-width: 220px;
}
/* 小屏幕时，每行只显示一个卡片 */
@media (max-width: 600px) {
  .card {
    flex: 1 1 100%;
  }
}


.card span {
  position: absolute;
  right: 15px;
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
