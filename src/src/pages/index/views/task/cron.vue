<template>
  <el-dialog v-model="visible" title="Cron 表达式编辑器" width="800px">
    <div class="cron-editor">
      <el-form label-width="80px" size="small">
        <el-form-item label="秒">
          <el-input v-fill-empty="'*'" v-model="form.second" placeholder="0-59, * / -"></el-input>
        </el-form-item>
        <el-form-item label="分">
          <el-input v-fill-empty="'*'" v-model="form.minute" placeholder="0-59, * / -"></el-input>
        </el-form-item>
        <el-form-item label="时">
          <el-input v-fill-empty="'*'" v-model="form.hour" placeholder="0-23, * / -"></el-input>
        </el-form-item>
        <el-form-item label="日">
          <el-input v-fill-empty="'*'" v-model="form.day" @keyup="(e) => {changeCron('day', e)}" placeholder="1-31, * / - L W ?"></el-input>
        </el-form-item>
        <el-form-item label="月">
          <el-input v-fill-empty="'*'" v-model="form.month" placeholder="1-12, JAN-DEC, * / -"></el-input>
        </el-form-item>
        <el-form-item label="周">
          <el-input v-fill-empty="'*'" v-model="form.week" @keyup="(e) => {changeCron('week', e)}" placeholder="0-7, SUN-SAT, * / - L # ?"></el-input>
        </el-form-item>
        <el-form-item label="年">
          <el-input v-fill-empty="'*'" v-model="form.year" placeholder="空或 1970-2099, * / -"></el-input>
        </el-form-item>
        <el-form-item label="生成的 Cron：">
          <el-input v-fill-empty="'*'" v-model="cronString" placeholder="空或 1970-2099, * / -"></el-input>
        </el-form-item>
      </el-form>
    </div>

    <div class="preview" :style="{ color: isValid ? '#333' : 'red' }">
      <strong>自然语言预览：</strong> {{ humanText }}
    </div>
    <div class="cron-string">
      <strong>生成的 Cron：</strong> {{cronString}}
    </div>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="onConfirm" :disabled="!isValid">确认</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { reactive, ref, computed } from "vue";
import { ElMessage } from "element-plus";

const visible = ref(false);
const resolveFn = ref(null);

const form = reactive({
  second: "*",
  minute: "*",
  hour: "*",
  day: "*",
  month: "*",
  week: "?",
  year: "*",
});

function handleBlur(e) {
  console.log(e);
}

function resetForm() {
  form.second = "*";
  form.minute = "*";
  form.hour = "*";
  form.day = "*";
  form.month = "*";
  form.week = "?";
  form.year = "*";
}

// 外部调用 show 方法
function show(cronString) {
  resetForm();
  if (cronString) {
    const parts = cronString.trim().split(/\s+/);
    if (parts.length >= 6) {
      [form.second, form.minute, form.hour, form.day, form.month, form.week] =
        parts;
      if (parts[6]) form.year = parts[6];
    }
  }
  visible.value = true;
  return new Promise((resolve) => {
    resolveFn.value = resolve;
  });
}

// Cron 组装
const cronString = computed(() => {
  return [
    form.second || "*",
    form.minute || "*",
    form.hour || "*",
    form.day || "*",
    form.month || "*",
    form.week || "?",
    form.year || "*",
  ]
    .filter(Boolean)
    .join(" ");
});

function changeCron(type, value) {
  console.log(`type:${type}; value:${value}`)
  if ( type === 'day') {
    form.week = '?'
  }
  if ( type === 'week') {
    form.day = '?'
  }
  if ( form.day === '?' && form.week === '?') {
    ElMessage.error("天和周 不能同时指定值也不能同时不指定值！");
    form[type] = '*'
  }
}

// 校验正则
function validateField(val, type) {
  if (!val) return true;
  const patterns = {
    second: /^([0-5]?\d)(\/[0-5]?\d)?([,-]([0-5]?\d)(\/[0-5]?\d)?)*$|^\*$/,
    minute: /^([0-5]?\d)(\/[0-5]?\d)?([,-]([0-5]?\d)(\/[0-5]?\d)?)*$|^\*$/,
    hour: /^([01]?\d|2[0-3])(\/([01]?\d|2[0-3]))?([,-]([01]?\d|2[0-3])(\/([01]?\d|2[0-3]))?)*$|^\*$/,
    day: /^(\*|\?|L|LW|([1-9]|[12]\d|3[01])(W)?)([,-]([1-9]|[12]\d|3[01])(W)?)*$/,
    month:
      /^(\*|([1-9]|1[0-2]|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC))([,-\/]([1-9]|1[0-2]|JAN|FEB|...|DEC))*$/,
    week:
      /^(\*|\?|([1-7]|SUN|MON|TUE|WED|THU|FRI|SAT)(L|\#[1-5])?)([,-]([1-7]|SUN|MON|TUE|WED|THU|FRI|SAT)(L|\#[1-5])?)*$/,
    year: /^(\*|([1-9]\d{3})(\/\d+)?)([,-]([1-9]\d{3})(\/\d+)?)*$/,
  };
  return patterns[type]?.test(val);
}

const isValidText = ref('');

const isValid = computed(() => {
  const baseValid =
    validateField(form.second, "second") &&
    validateField(form.minute, "minute") &&
    validateField(form.hour, "hour") &&
    validateField(form.day, "day") &&
    validateField(form.month, "month") &&
    validateField(form.week, "week") &&
    validateField(form.year, "year");

  if (!baseValid) return false;

  // 新增规则：日和周必须有一个是 ?
  const day = form.day.trim();
  const week = form.week.trim();

  if (day !== "?" && week !== "?") {
    isValidText.value = '日和周不能同时指定值!';
    return false;
  }

  return true;
});


function describeField(val, type) {
  const map = {
      second: "秒",
      minute: "分",
      hour: "时",
      day: "天",
      month: "月",
      week: "周",
      year: "年",
    };
  if (!val || val === "*") {
    return '每' + map[type];
  }

  // 通用分隔符处理
  if (val.includes(",")) {
    return val
      .split(",")
      .map((v) => describeField(v, type))
      .join("，");
  }

  // 区间
  if (val.includes("-")) {
    const [start, end] = val.split("-");
    return `${translateSingle(start, type)}${map[type]}到${translateSingle(end, type)}${map[type]}`;
  }

  // 步长
  if (val.includes("/")) {
    const [base, step] = val.split("/");
    if (base === "*") {
      return `每${step}${unitName(type)}`;
    }
    return `从${translateSingle(base, type)}${map[type]}开始每${step}${unitName(type)}`;
  }

  // 特殊处理 day
  if (type === "day") {
    if (val === "L") return "最后一天";
    if (val === "LW") return "最后一个工作日";
    if (val.endsWith("W")) {
      return `最接近${val.replace("W", "")}号的工作日`;
    }
  }

  // 特殊处理 week
  if (type === "week") {
    if (val === "L") return "最后一个周";
    if (val.includes("#")) {
      const [day, nth] = val.split("#");
      return `本月第${nth}个${translateSingle(day, type)}`;
    }
    return translateSingle(val, type);
  }

  // 其他默认
  return translateSingle(val, type) + map[type];
}

function translateSingle(v, type) {
  const weekMap = {

    0: "周一",
    1: "周二",
    2: "周三",
    3: "周四",
    4: "周五",
    5: "周六",
    6: "周日",
    SUN: "周日",
    MON: "周一",
    TUE: "周二",
    WED: "周三",
    THU: "周四",
    FRI: "周五",
    SAT: "周六",
  };
  const monthMap = {
    1: "1",
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: "6",
    7: "7",
    8: "8",
    9: "9",
    10: "10",
    11: "11",
    12: "12",
    JAN: "1",
    FEB: "2",
    MAR: "3",
    APR: "4",
    MAY: "5",
    JUN: "6",
    JUL: "7",
    AUG: "8",
    SEP: "9",
    OCT: "10",
    NOV: "11",
    DEC: "12",
  };

  if (type === "week") return weekMap[v] || v;
  if (type === "month") return monthMap[v] || v;

  return v;
}

function unitName(type) {
  const map = {
    second: "秒",
    minute: "分",
    hour: "时",
    day: "天",
    month: "月",
    week: "周",
    year: "年",
  };
  return map[type];
}


// 拼接自然语言
const humanText = computed(() => {
  if (!isValid.value) return "表达式不合法;" + isValidText.value;

  const sec = describeField(form.second, "second");
  const min = describeField(form.minute, "minute");
  const hr = describeField(form.hour, "hour");
  const day = describeField(form.day, "day");
  const mon = describeField(form.month, "month");
  const wk = describeField(form.week, "week");
  const yr = form.year ? describeField(form.year, "year") : "*";

  if ( wk === '?' ) {
    return `在 [${yr}] 的 [${mon}] 的 [${day}] 的 [${hr}] 的 [${min}] 的 [${sec}]`.replace(
      /\s+/g,
      " "
    );
  } else {
    return `在 [${yr}] 的 [${mon}] 的 [${wk}] 的 [${hr}] 的 [${min}] 的 [${sec}]`.replace(
      /\s+/g,
      " "
    );
  }


});

function onConfirm() {
  if (!isValid.value) {
    ElMessage.error("表达式不合法，请检查输入！");
    return;
  }
  resolveFn.value && resolveFn.value(cronString.value);
  visible.value = false;
}

defineExpose({ show });
</script>

<style scoped>
.cron-editor {
  max-height: 400px;
  overflow-y: auto;
}
.preview {
  margin: 10px 0;
}
</style>
