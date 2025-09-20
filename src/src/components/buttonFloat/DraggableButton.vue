<template>
  <el-button
    ref="dragBtn"
    class="draggable-btn"
    :style="computedStyle"
    @click="handleClick"
  >
    <slot>
      <!-- 默认图标 -->
      <el-icon><plus /></el-icon>
    </slot>
  </el-button>
</template>

<script setup>
import { ref, onMounted, computed } from "vue"

const props = defineProps({
  width: { type: String, default: "4rem" },
  height: { type: String, default: "4rem" },
  background: { type: String, default: "#007aff" },
  coordinates: { type: Object, default: () => ({ bottom: "2rem", right: "2rem", top: null, left: null }) },
  click: { type: Function },
  iconScale: { type: Number, default: 0.4 } // 图标占按钮比例
})

const dragBtn = ref(null)
let isDragging = false
let startX = 0
let startY = 0
let offsetX = 0
let offsetY = 0
let moved = false
const DRAG_THRESHOLD = 3
let pending = false
let targetX = 0
let targetY = 0

const handleClick = () => {
  if (moved) {
    moved = false
    return
  }
  props.click && props.click()
}

// 动态生成按钮样式，同时设置 CSS 变量控制图标大小
const computedStyle = computed(() => {
  const iconSize = `calc(${props.width} * ${props.iconScale})`
  return {
    position: "fixed",
    width: props.width,
    height: props.height,
    background: props.background,
    borderRadius: "50%",
    boxShadow: "0 4px 8px rgba(0,0,0,0.2)",
    cursor: "grab",
    zIndex: 99,
    top: props.coordinates.top,
    bottom: props.coordinates.bottom,
    left: props.coordinates.left,
    right: props.coordinates.right,
    '--icon-size': iconSize // CSS 变量
  }
})

onMounted(() => {
  const btn = dragBtn.value.$el ?? dragBtn.value

  // PC 鼠标拖动
  btn.addEventListener("mousedown", (e) => {
    e.preventDefault()
    isDragging = true
    moved = false
    startX = e.clientX
    startY = e.clientY
    const rect = btn.getBoundingClientRect()
    offsetX = e.clientX - rect.left
    offsetY = e.clientY - rect.top

    const onMouseMove = (ev) => {
      ev.preventDefault()
      if (!isDragging) return
      const dx = ev.clientX - startX
      const dy = ev.clientY - startY
      if (Math.abs(dx) > DRAG_THRESHOLD || Math.abs(dy) > DRAG_THRESHOLD) moved = true
      targetX = ev.clientX - offsetX
      targetY = ev.clientY - offsetY
      if (!pending) {
        pending = true
        requestAnimationFrame(() => {
          btn.style.left = `${targetX}px`
          btn.style.top = `${targetY}px`
          btn.style.right = "auto"
          btn.style.bottom = "auto"
          pending = false
        })
      }
    }

    const onMouseUp = () => {
      isDragging = false
      document.removeEventListener("mousemove", onMouseMove)
      document.removeEventListener("mouseup", onMouseUp)
    }

    document.addEventListener("mousemove", onMouseMove)
    document.addEventListener("mouseup", onMouseUp)
  })

  // 移动端拖动
  btn.addEventListener("touchstart", (e) => {
    if (!e.touches || e.touches.length === 0) return
    isDragging = true
    moved = false
    startX = e.touches[0].clientX
    startY = e.touches[0].clientY
    const rect = btn.getBoundingClientRect()
    offsetX = startX - rect.left
    offsetY = startY - rect.top
  })

  btn.addEventListener("touchmove", (e) => {
    if (!isDragging) return
    const t = e.touches[0]
    const dx = t.clientX - startX
    const dy = t.clientY - startY
    if (Math.abs(dx) > DRAG_THRESHOLD || Math.abs(dy) > DRAG_THRESHOLD) moved = true
    btn.style.left = `${t.clientX - offsetX}px`
    btn.style.top = `${t.clientY - offsetY}px`
    btn.style.right = "auto"
    btn.style.bottom = "auto"
  })

  btn.addEventListener("touchend", () => {
    isDragging = false
  })
})
</script>

<style scoped>
.draggable-btn {
  user-select: none;
  -webkit-user-select: none;
  touch-action: none;
}
.draggable-btn:active {
  cursor: grabbing;
}

/* 通过 CSS 变量控制图标大小，动态跟随按钮 */
.draggable-btn :deep(svg) {
  width: var(--icon-size);
  height: var(--icon-size);
}
.draggable-btn :deep(.el-icon) {
  width: var(--icon-size);
  height: var(--icon-size);
}
</style>
