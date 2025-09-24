// directives/fill-default.js
export default {
  mounted(el, binding) {
    // el 是 el-input 的根节点，需要找到内部的真实 input
    const inputEl = el.querySelector("input");
    if (!inputEl) return;

    inputEl.addEventListener("blur", () => {
      if (inputEl.value.trim() === "") {
        inputEl.value = binding.value || ""; // 设置默认值
        // 触发 input 事件，确保 v-model 更新
        inputEl.dispatchEvent(new Event("input"));
      }
    });
  },
};
