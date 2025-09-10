<template>
  <div class="dashboard">
    <!-- 基本状态 -->
    <div class="card bg-normal">
      <h3>基本状态</h3>
      <p>计算机名: <span class="highlight">{{ info.computerName }}</span></p>
      <p>电池: <span class="highlight">{{ info.battery }}</span></p>
      <!-- 屏幕亮度 -->
      <div class="slider-group" style="display: flex;flex-wrap: wrap;">
        <label style="width: 100%; display: block;">屏幕亮度: <span class="highlight">{{ info.brightness }}%</span></label>
        <input style="margin-top: 10px;"
          type="range"
          min="0"
          max="100"
          v-model="info.brightness"
          @input="updateValue"
          @wheel.prevent="onWheel('brightness', $event)"
          class="slider brightness"
        />
      </div>

      <!-- 音量 -->
      <div class="slider-group" style="display: flex;flex-wrap: wrap;">
        <label style="width: 100%; display: block;">音量: <span class="highlight">{{ info.muted ? '静音' : parseInt(info.volume) + '%' }}</span></label>
        <input style="margin-top: 10px;"
          type="range"
          min="0"
          max="100"
          v-model="info.volume"
          @input="updateValue"
          @wheel.prevent="onWheel('volume', $event)"
          class="slider volume"
        />
        <button class="mute-btn" @click="toggleMute" style="margin-top: -16px;">
          <span v-if="info.muted">🔇</span>
          <span v-else>🔊</span>
        </button>
      </div>
    </div>

    <!-- 性能配置 -->
    <div class="card bg-normal">
      <h3>性能配置</h3>
      <p>性能模式: <span class="highlight">{{ config.mode }}</span></p>
      <p>键盘背光: <span class="highlight">{{ config.keyboardLight }}</span></p>
      <p>显卡: <span class="highlight">{{ config.gpu }}</span></p>
      <p>刷新率: <span class="highlight">
          <el-select
              class="card-select"
              size="mini"
              @change="updateRefreshRate"
              v-model="info.refresh_rate"
              placeholder="请选择">
            <el-option
              v-for="item in info.pc_get_supported_refresh_rate"
              :key="item"
              :label="item + 'Hz'"
              :value="item">
            </el-option>
          </el-select>
        </span>
      </p>
    </div>

    <!-- 定时任务 -->
    <div class="card bg-normal">
      <h3>定时任务</h3>
      <p>30分钟后: <span class="highlight">音量调节到0%</span></p>
      <p>电源断开时: <span class="highlight">刷新率60Hz</span></p>
      <p>电源插入时: <span class="highlight">刷新率120Hz</span></p>
      <p>30分钟后: <span class="highlight">使计算机休眠</span></p>
    </div>

    <!-- 宏 -->
    <div class="card bg-normal">
      <h3>宏</h3>
      <p>FN&Q: <span class="highlight">狮鹫起飞</span></p>
      <p>W|A|S|D: <span class="highlight">滚轮向下10</span></p>
      <p>鼠标侧键1: <span class="highlight">左键连续</span></p>
      <p>鼠标侧键2: <span class="highlight">F键连续</span></p>
    </div>

    <!-- 底部 -->
    <div class="card full bg-normal">
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
  refresh_rate: 60, // 刷新率
  pc_get_supported_refresh_rate:[60],
  muted: false, // 静音
})

const config = reactive({
  mode: '野兽模式',
  keyboardLight: '高亮度',
  gpu: 'NVIDIA',
})

async function updateRefreshRate(val) {
  if (!values.isPyWeb ) {
    ElMessage.success('不是PyWeb环境!')
    return
  }
  await window.pywebview.api.pc_set_refresh_rate(val)
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
  info.refresh_rate = await window.pywebview.api.pc_get_refresh_rate()
  info.pc_get_supported_refresh_rate = await window.pywebview.api.pc_get_supported_refresh_rate()
}


// 更新亮度&音量
async function updateValue() {
  if (!values.isPyWeb ) {
    ElMessage.success('不是PyWeb环境!')
    return
  }
  let setRes = await window.pywebview.api.pc_set_brightness(info.brightness)
  await window.pywebview.api.pc_set_volume(info.volume / 100)
  // if (!setRes) {
  //   ElMessage.success('亮度设置失败!')
  // }
}
// 鼠标调节滚动条
function onWheel(key, event) {
  const step = event.ctrlKey ? 5 : 1
  if (event.deltaY < 0) {
    info[key] = Math.min(100, info[key] + step)
  } else {
    info[key] = Math.max(0, info[key] - step)
  }
  updateValue()
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
.card-select {
  min-width: 100px;
  min-height: 20px;
  height: 20px;
}


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
  padding: .5rem;
  font-family: "Segoe UI", sans-serif;
}

.card {
  border: 0 solid #ddd;
  border-radius: 12px;
  padding: .5rem .5rem;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  position: relative;
  flex: 1 1 calc(33.33% - .5rem); /* 默认每行3个卡片 */
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
<style>
.card-select .el-select__wrapper {
  min-width: 100px;
  min-height: 20px;
  height: 20px;
  border-radius: 10px;
}
</style>
