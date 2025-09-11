<!--suppress CssUnusedSymbol -->
<template>
  <div class="app-task">
    <div class="task-container bg-normal">
    <!-- Tabs -->
    <div class="tabs">
      <div
        v-for="(tab, index) in tabs"
        :key="index"
        :class="['tab', { active: activeIndex === index }]"
        @click="goTo(index)"
      >
        {{ tab }}
      </div>
    </div>

    <!-- Swiper 内容区 --> <!-- 动画时长 400ms -->
    <swiper
      @swiper="onSwiper"
      :modules="[Navigation]"
      :onSlideChange="onSlideChange"
      :initial-slide="activeIndex"
      :speed="400"
      class="swiper-container"
    >
      <!-- 三份内容区 -->
      <swiper-slide class="swiper-slide-task">
        <div class="list ">
          <div v-for="(item, i) in task_config.relations" :key="i" class="list-item bg-gray-200">
            <div class="left">任务{{ i }}:</div>
            <div class="middle">动作: <span class="action">{{ item.desc }}</span></div>
            <button class="close-btn">×</button>
          </div>
        </div>
      </swiper-slide>

      <swiper-slide>
        <div class="list ">
          <div v-for="(item, i) in task_config.triggers" :key="i" class="list-item bg-gray-200">
            <div class="left">{{ item.name }}:</div>
            <div class="middle">描述: <span class="action">{{ item.desc || item.name }}</span></div>
            <button class="close-btn">×</button>
          </div>
        </div>
      </swiper-slide>

      <swiper-slide>
        <div class="list ">
          <div v-for="(item, i) in task_config.actions" :key="i" class="list-item bg-gray-200">
            <div class="left">{{ item.name }}:</div>
            <div class="middle">描述: <span class="action">{{ item.desc || item.name }}</span></div>
            <button class="close-btn">×</button>
          </div>
        </div>
      </swiper-slide>
    </swiper>
  </div>
  </div>
</template>

<script setup>
import {nextTick, ref} from "vue";
import { onMounted } from 'vue';
import { Swiper, SwiperSlide } from "swiper/vue";
import "swiper/swiper-bundle.css";
import { Navigation } from "swiper/modules";

const tabs = ["任务", "触发器", "动作"];
const activeIndex = ref(0);
const swiperInstance  = ref(null);
const task_config  = ref({
  relations:[
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
  ],
  triggers: [
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
  ],
  actions: [
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
    {name: "示例1", desc: "sdwawdaw"},
  ],
  action_type: [],
  trigger_type: []});

// 每个 tab 独立的数据
/*const items1 = [
  { trigger: "稍后执行(秒): 1", action: "修改屏幕亮度: 40" },
  { trigger: "xxx", action: "xxx" },
];
const items2 = [
  { trigger: "触发器B1", action: "动作B1" },
  { trigger: "触发器B2", action: "动作B2" },
];
const items3 = [
  { trigger: "触发器C1", action: "动作C1" },
  { trigger: "触发器C2", action: "动作C2" },
];*/

// 生命周期
onMounted(async () => {
  console.log('组件挂载完成')
  if (window && window.pywebview && window.pywebview.api) {
    task_config.value = await window.pywebview.api.task_get_config()
    console.log(task_config);
  }
})


function onSwiper(sw) {
  // sw 就是 Swiper 的实例
  swiperInstance.value = sw;
  // console.log('swiper ready', sw);
}

function goTo(index) {
  activeIndex.value = index;
  // 如果实例已就绪，直接用 slideTo；否则等待下一 tick 再尝试一次（防止首次还没初始化的情况）
  if (swiperInstance.value && typeof swiperInstance.value.slideTo === 'function') {
    swiperInstance.value.slideTo(index, 400);
  } else {
    nextTick(() => {
      swiperInstance.value?.slideTo?.(index, 400);
    });
  }
}

function onSlideChange(swiper) {
  activeIndex.value = swiper.activeIndex;
}
</script>

<style scoped>
.swiper-slide-task {
  overflow-y: auto;
}
.app-task {
  display: flex;
}
.task-container {
  width: calc(100% - 1rem);
  height: calc(100% - 1rem);
  margin-top: .5rem;
  overflow: hidden;
  margin-left: .5rem;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.tabs {
  display: flex;
  border-bottom: 1px solid #616161;
}
.tab {
  flex: 1;
  text-align: center;
  padding: 10px;
  cursor: pointer;
  transition: color 0.3s, border-color 0.3s;
}
.tab.active {
  border-bottom: 2px solid #4a56e2;
  font-weight: bold;
  color: #4a56e2;
}

/*noinspection CssOverwrittenProperties*/
.swiper-container {
  height: calc(100vh - 7rem);
  height: calc(100dvh - 7rem);
  padding-bottom: .5rem;
}

.list {
  padding: 10px;
  overflow-y: auto;
  height: 100%;
}
.list-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-radius: 10px;
  padding: 10px;
  margin: 10px 0;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}
.left {
  flex: 1;
  max-width: 30%;
}
.middle {
  flex: 1;
  text-align: right;
  max-width: 55%;
}
.action {
  color: #4a56e2;
  overflow-wrap: break-word;
}
.close-btn {
  border: none;
  background: none;
  font-size: 18px;
  cursor: pointer;
}
</style>
