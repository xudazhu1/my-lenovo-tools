import '@/main'
import { createApp, } from 'vue'
import { createPinia, } from 'pinia'
import App from './App.vue'
import ElementPlus from '@/plugins/element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import errorReport from '@/plugins/error-report'
import dayjs from '@/plugins/dayjs'
import router from './router'
import pageComponents from './components'
import './permission'
import '@/mock'
import './styles/index.css'
import fillEmpty from '@/components/fillEmpty/fillEmpty'

const app = createApp(App)

app.directive('fill-empty', fillEmpty)

app
  .use(router)
  .use(createPinia())
  .use(ElementPlus)
  .use(errorReport)
  .use(dayjs)
  .use(pageComponents)
  .mount('#app')
