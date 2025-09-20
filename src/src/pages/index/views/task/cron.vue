<template>
  <el-dialog v-model="visible" title="Quartz Cron 编辑器" width="840px">
    <div class="mb-3">
      <el-alert
        v-if="cronStr"
        type="success"
        :title="`当前规则：${cronStr}`"
        show-icon
      />
      <el-alert v-else type="info" title="尚未设置规则，请录入或粘贴 Cron 表达式" show-icon />
    </div>

    <el-form :model="form" label-width="120px" size="small">
      <el-form-item label="秒 (0-59)" :error="fieldErrors.second">
        <el-input v-model="form.second" placeholder="*, 0-59, 0/5, 0,15,30" />
      </el-form-item>

      <el-form-item label="分钟 (0-59)" :error="fieldErrors.minute">
        <el-input v-model="form.minute" placeholder="*, 0-59, */5, 0,15,30" />
      </el-form-item>

      <el-form-item label="小时 (0-23)" :error="fieldErrors.hour">
        <el-input v-model="form.hour" placeholder="*, 0-23, 0-12, */2, 8,12" />
      </el-form-item>

      <el-form-item label="日 (1-31) 支持 L/W/?" :error="fieldErrors.day">
        <el-input v-model="form.day" placeholder="*, 1-31, 15W, L, LW, 1-15, 1/2, ?, 1,15" />
      </el-form-item>

      <el-form-item label="月 (1-12 或 JAN-DEC)" :error="fieldErrors.month">
        <el-input v-model="form.month" placeholder="*, 1-12, JAN, JAN-MAR, */2, 1,3,5" />
      </el-form-item>

      <el-form-item label="周 (0-6 或 SUN-SAT) 支持 L/#/?" :error="fieldErrors.week">
        <el-input v-model="form.week" placeholder="*, 0-6, MON-FRI, 6L, 2#1, ?, SUN" />
      </el-form-item>

      <el-form-item label="年（可选，1970-2099）" :error="fieldErrors.year">
        <el-input v-model="form.year" placeholder="可选：1970-2099，或 * / 2025,2026" />
      </el-form-item>
    </el-form>

    <div class="preview" style="margin-top:16px">
      <el-alert
        v-if="!isValid"
        type="error"
        :title="`表达式不合法：${errorSummary}`"
        show-icon
      />
      <el-alert
        v-else
        type="success"
        :title="`自然语言描述：${humanText}`"
        show-icon
      />
    </div>

    <div style="margin-top:12px; display:flex; gap:8px; justify-content:flex-end">
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :disabled="!isValid" @click="onConfirm">确认</el-button>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed } from "vue";

/**
 * 完整 Quartz 风格校验与描述的 Vue3 组件
 *
 * 注意：
 *  - 日 (day-of-month) 与 周 (day-of-week) 的互斥：至少其中一个应为 '?'，否则报错（Quartz 语义）
 *  - 支持 6 或 7 段输入（如果只传 6 段，默认没有 year）
 */

const props = defineProps({
  cron: { type: String, default: "" },
});
const emit = defineEmits(["update:cron"]);

const visible = ref(false);
const cronStr = ref("");

// 表单初始
const form = reactive({
  second: "*",
  minute: "*",
  hour: "*",
  day: "?",
  month: "*",
  week: "*",
  year: "", // 可选
});

// 映射表：月份和星期英文名 -> 数字
const MONTHS = {
  JAN: 1, FEB: 2, MAR: 3, APR: 4, MAY: 5, JUN: 6,
  JUL: 7, AUG: 8, SEP: 9, OCT: 10, NOV: 11, DEC: 12
};
const DAYS = { SUN: 0, MON: 1, TUE: 2, WED: 3, THU: 4, FRI: 5, SAT: 6 };

// 字段元信息（范围与标签）
const FIELD_META = {
  second: { min: 0, max: 59, label: "秒" },
  minute: { min: 0, max: 59, label: "分" },
  hour: { min: 0, max: 23, label: "时" },
  day: { min: 1, max: 31, label: "日" },
  month: { min: 1, max: 12, label: "月" },
  week: { min: 0, max: 6, label: "周" },
  year: { min: 1970, max: 2099, label: "年" },
};

defineExpose({ show });

// show()：打开并解析 props.cron（支持 6 或 7 段）
function show() {
  visible.value = true;
  if (props.cron) parseCron(props.cron);
  else resetForm();
}

function resetForm() {
  form.second = "*";
  form.minute = "*";
  form.hour = "*";
  form.day = "*";
  form.month = "*";
  form.week = "?";
  form.year = "*";
  cronStr.value = "";
}

function parseCron(s) {
  if (!s) return;
  const parts = s.trim().split(/\s+/);
  if (parts.length === 6) {
    // 秒 分 时 日 月 周
    [form.second, form.minute, form.hour, form.day, form.month, form.week] = parts;
    form.year = "";
    cronStr.value = s;
  } else if (parts.length === 7) {
    // 秒 分 时 日 月 周 年
    [form.second, form.minute, form.hour, form.day, form.month, form.week, form.year] = parts;
    cronStr.value = s;
  } else if (parts.length === 5) {
    // 兼容：如果用户传 5 段（分 时 日 月 周），按秒为 0 处理
    form.second = "0";
    [form.minute, form.hour, form.day, form.month, form.week] = parts;
    form.year = "";
    cronStr.value = `0 ${s}`;
  } else {
    // 非法长度 -> 直接填入原始
    cronStr.value = s;
  }
}

// ===== 校验逻辑（Quartz 风格） =====
// 支持 token 的形式：逗号分隔的 token，每个 token 可以是：
//  - *
//  - ?
//  - 名称（JAN..DEC / SUN..SAT）或数字
//  - 单值 e.g. 5
//  - 范围 e.g. 1-5
//  - 步进 e.g. */5, 1/2, 1-10/2
//  - 日特有： L, LW, 15W
//  - 周特有： 6L (最后一个周五), 2#1 (第一个周一)
// 校验分两部分：语法 + 数值范围 + 语义互斥（day/week 与 ?）

// 基本 token 正则： 捕获 start (数字或名称或 '* or ?'), 可选 -end, 可选 /step
const BASIC_TOKEN_RE = /^(\*|\?|\d+|[A-Z]+)(?:-(\d+|[A-Z]+))?(?:\/(\d+))?$/i;

// 校验单个 token（不含逗号）
function validateSingleToken(token, field) {
  token = token.trim();
  const meta = FIELD_META[field];

  if (!token) return { ok: false, msg: "空 token" };

  // 通配符
  if (token === "*" || token === "?") return { ok: true };

  // 日特有： L 或 LW 或 数字 + W 或 数字W (例如 15W)
  if (field === "day") {
    if (/^L$/i.test(token)) return { ok: true };
    if (/^LW$/i.test(token)) return { ok: true };
    if (/^\d+W$/i.test(token)) {
      const n = Number(token.replace(/W/i, ""));
      if (!Number.isInteger(n) || n < FIELD_META.day.min || n > FIELD_META.day.max) {
        return { ok: false, msg: `日字段: ${token} 中的数字超出范围` };
      }
      return { ok: true };
    }
  }

  // 周特有： e.g. 6L (最后一个周X), 或 N#k (第k个周N)
  if (field === "week") {
    if (/^\d+L$/i.test(token)) {
      const n = Number(token.replace(/L/i, ""));
      if (!Number.isInteger(n) || n < FIELD_META.week.min || n > FIELD_META.week.max) {
        return { ok: false, msg: `周字段: ${token} 中的数字超出范围` };
      }
      return { ok: true };
    }
    if (/^\d+#\d+$/i.test(token)) {
      const [d, k] = token.split("#").map(Number);
      if (!Number.isInteger(d) || d < FIELD_META.week.min || d > FIELD_META.week.max) {
        return { ok: false, msg: `周字段: ${token} 的星期值超出范围` };
      }
      if (!Number.isInteger(k) || k < 1 || k > 5) {
        // 第 N 个周几通常 1-5 有意义
        return { ok: false, msg: `周字段: ${token} 的序号必须为 1-5` };
      }
      return { ok: true };
    }
  }

  // 解析基本形式（可能包含英文月份/周名）
  const m = token.match(BASIC_TOKEN_RE);
  if (!m) {
    // 进一步检测 day 的 L 或 week 的 # 已在上面处理
    return { ok: false, msg: `格式非法：${token}` };
  }

  let start = m[1];
  const end = m[2];
  const step = m[3] ? Number(m[3]) : null;

  // 名称 -> 数字（支持月和周的英文缩写）
  if (/^[A-Z]+$/i.test(start)) {
    const up = start.toUpperCase();
    if (field === "month") {
      if (!(up in MONTHS)) return { ok: false, msg: `月名非法：${start}` };
      start = String(MONTHS[up]);
    } else if (field === "week") {
      if (!(up in DAYS)) return { ok: false, msg: `周名非法：${start}` };
      start = String(DAYS[up]);
    } else {
      return { ok: false, msg: `字段 ${field} 不支持名称：${start}` };
    }
  }

  // end 也可能是名称
  let endVal = null;
  if (end) {
    if (/^[A-Z]+$/i.test(end)) {
      const up = end.toUpperCase();
      if (field === "month") {
        if (!(up in MONTHS)) return { ok: false, msg: `月名非法：${end}` };
        endVal = Number(MONTHS[up]);
      } else if (field === "week") {
        if (!(up in DAYS)) return { ok: false, msg: `周名非法：${end}` };
        endVal = Number(DAYS[up]);
      } else {
        // day/hour/minute/second 不应出现名称
        return { ok: false, msg: `字段 ${field} 不支持名称：${end}` };
      }
    } else {
      endVal = Number(end);
    }
  }

  // start numeric now
  if (start === "*" || start === "?") {
    // '*' or '?' handled earlier; should not get here
  } else {
    const startNum = Number(start);
    if (!Number.isInteger(startNum)) return { ok: false, msg: `值不是整数：${start}` };
    if (startNum < meta.min || startNum > meta.max) {
      return { ok: false, msg: `值 '${startNum}' 超出 ${meta.label} 范围 ${meta.min}-${meta.max}` };
    }
    if (endVal !== null) {
      if (!Number.isInteger(endVal)) return { ok: false, msg: `区间终点不是整数：${end}` };
      if (endVal < meta.min || endVal > meta.max) {
        return { ok: false, msg: `区间终点 '${endVal}' 超出 ${meta.label} 范围 ${meta.min}-${meta.max}` };
      }
      if (startNum > endVal) return { ok: false, msg: `区间起点 ${startNum} 大于终点 ${endVal}` };
    }
  }

  if (step !== null) {
    if (!Number.isInteger(step) || step <= 0) return { ok: false, msg: `步长 '${step}' 必须为正整数` };
  }

  return { ok: true };
}

// 校验整字段（允许逗号分隔多个 token）
function validateField(field, value) {
  value = value.trim();
  if (!value) return { ok: false, msg: "空值" };

  // 逗号分隔的 tokens
  const tokens = value.split(",").map(t => t.trim()).filter(Boolean);
  if (tokens.length === 0) return { ok: false, msg: "空值" };

  // 特殊情况：day 或 week 允许 '?'（取代 * 的语义）
  // 但如果字段包含 '?'，它应该是单独 token 并且不与其它 token 组合
  if (tokens.includes("?")) {
    if (tokens.length > 1) return { ok: false, msg: "'?' 不能与其他 token 组合" };
    return { ok: true }; // 语义互斥另处处理
  }

  // 对每个 token 单独校验
  for (const t of tokens) {
    const r = validateSingleToken(t, field);
    if (!r.ok) return { ok: false, msg: r.msg };
  }

  return { ok: true };
}

// 返回每个字段的错误消息（null 表示通过）
const fieldErrors = computed(() => {
  const errs = {};
  for (const k of Object.keys(FIELD_META)) {
    // year 是可选的：为空视为通过
    if (k === "year" && (!form.year || form.year.trim() === "")) {
      errs[k] = null;
      continue;
    }
    const res = validateField(k, form[k] ?? "");
    errs[k] = res.ok ? null : res.msg;
  }

  // 语义互斥：日 与 周 必须满足 Quartz 的互斥规则
  // 要求：day 或 week 中至少有一个为 '?'（因为 Quartz 中一个字段应被 '?' 表示“未指定”，另一个才可指定）
  // 如果两者都不是 '?'，报错
  const dayHasQ = (form.day || "").trim() === "?";
  const weekHasQ = (form.week || "").trim() === "?";
  if (!dayHasQ && !weekHasQ) {
    // 如果两者都不是 '?'，并且都不是 '*'（完全通配），强烈提示要求使用 '?' 进行互斥
    errs.day = errs.day || "日/周 字段必须有一个为 '?'（Quartz 语义互斥）";
    errs.week = errs.week || "日/周 字段必须有一个为 '?'（Quartz 语义互斥）";
  }

  return errs;
});

// 是否整体合法
const isValid = computed(() => {
  const e = fieldErrors.value;
  return Object.values(e).every(v => v === null);
});

// 错误摘要
const errorSummary = computed(() => {
  const arr = [];
  for (const k of Object.keys(fieldErrors.value)) {
    if (fieldErrors.value[k]) arr.push(`${FIELD_META[k].label}: ${fieldErrors.value[k]}`);
  }
  return arr.join("； ");
});

// ===== 自然语言生成 =====
// 将单个 token 翻译为中文描述（简洁可读）
// 兼容 L,W,#,? 等
function tokenToText(token, field) {
  token = token.trim();
  if (!token) return "";

  if (token === "*") return `每${FIELD_META[field].label}`;
  if (token === "?") return `未指定`;

  // 日专用
  if (field === "day") {
    if (/^L$/i.test(token)) return "当月最后一天";
    if (/^LW$/i.test(token)) return "当月最后的工作日";
    if (/^\d+W$/i.test(token)) {
      const n = token.replace(/W/i, "");
      return `每月 ${n} 日最近的工作日`;
    }
  }
  // 周专用
  if (field === "week") {
    if (/^\d+L$/i.test(token)) {
      const d = Number(token.replace(/L/i, ""));
      return `本月最后一个周${["日","一","二","三","四","五","六"][d]}`;
    }
    if (/^\d+#\d+$/i.test(token)) {
      const [d, num] = token.split("#").map(Number);
      return `每月第${num}个周${["日","一","二","三","四","五","六"][d]}`;
    }
  }

  // 名称处理（JAN,MON 等）
  if (/^[A-Z]+$/i.test(token)) {
    const up = token.toUpperCase();
    if (FIELD_META[field].label === "月") {
      if (MONTHS[up]) return `${up}（${MONTHS[up]}月）`;
    }
    if (FIELD_META[field].label === "周") {
      if (DAYS[up] !== undefined) return `${up}（周${["日","一","二","三","四","五","六"][DAYS[up]]}）`;
    }
  }

  // 范围或步进
  const m = token.match(/^(\*|\d+)(?:-(\d+))?(?:\/(\d+))?$/);
  if (m) {
    const start = m[1], end = m[2], step = m[3];
    if (start === "*") {
      if (step) return `每隔 ${step} ${FIELD_META[field].label}`;
      return `每${FIELD_META[field].label}`;
    }
    if (end && step) return `${start} 到 ${end}${FIELD_META[field].label}，每 ${step} ${FIELD_META[field].label}`;
    if (end) return `${start} 到 ${end}${FIELD_META[field].label}`;
    if (step) return `从 ${start}${FIELD_META[field].label} 开始每 ${step}${FIELD_META[field].label}`;
    return `${start}${FIELD_META[field].label}`;
  }

  // 逗号列表会在上层处理
  return token;
}

function describeField(value, field) {
  const tokens = value.split(",").map(t => t.trim()).filter(Boolean);
  const parts = tokens.map(t => tokenToText(t, field));
  return parts.join("、");
}

const humanText = computed(() => {
  if (!isValid.value) return "表达式不合法，请查看上方错误信息。";

  const sec = describeField(form.second, "second");
  const min = describeField(form.minute, "minute");
  const hr  = describeField(form.hour, "hour");
  const day = describeField(form.day, "day");
  const mon = describeField(form.month, "month");
  const wk  = describeField(form.week, "week");
  const yr  = form.year ? describeField(form.year, "year") : "";

  let parts = [];

  // 年
  if (yr) parts.push(`${yr}`);

  // 月
  if (mon) parts.push(`的 ${mon}`);

  // 日或周
  if (day && day !== "每天" && day !== "未指定" && day !== "*")
    parts.push(`的 ${day}`);
  if (wk && wk !== "未指定" && wk !== "*")
    parts.push(`的 ${wk}`);

  // 时间
  if (hr) {
    if ( hr !== "每时" )
      parts.push(`${hr}时`);
    else
      parts.push(`${hr}`);
  }
  if (min) {
    if ( min === "每分" )
      parts.push(`${min}`);
    else
      parts.push(`${min}分`);
  }
  if (sec) {
    if ( sec === "每秒" )
      parts.push(`的${sec}`);
    else
      parts.push(`的${sec}`);
  }

  // 全部 * 的特例
  if (
    form.second === "*" &&
    form.minute === "*" &&
    form.hour === "*" &&
    form.day === "*" &&
    form.month === "*" &&
    (form.week === "*" || form.week === "?") &&
    (!form.year || form.year === "*" )
  ) {
    return "每秒执行一次";
  }

  return "在 " + parts.filter(Boolean).join(" ");
});

// 确认生成 cron 字符串并回传
function onConfirm() {
  if (!isValid.value) return;
  const parts = [form.second, form.minute, form.hour, form.day, form.month, form.week];
  if (form.year && form.year.trim() !== "") parts.push(form.year.trim());
  const c = parts.join(" ");
  cronStr.value = c;
  emit("update:cron", c);
  visible.value = false;
}
</script>

<style scoped>
.mb-3 {
  margin-bottom: 12px;
}
.preview {
  margin-top: 12px;
}
</style>
