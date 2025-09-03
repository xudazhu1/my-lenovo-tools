from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta


def my_job():
    print(f'定时任务执行时间: {datetime.now()}')

# 创建调度器
scheduler = BlockingScheduler()

# 添加任务 - 5秒后执行
run_time = datetime.now() + timedelta(minutes=0, seconds=5)

# 添加一次性任务，在5分钟后执行
scheduler.add_job(my_job, 'date', run_date=run_time)

# # 添加任务 - 每5分钟执行一次
# scheduler.add_job(my_job, 'interval', minutes=5)
#
# # 添加任务 - 使用 Cron 表达式（每天上午10:30执行）
scheduler.add_job(my_job, 'cron', hour=10, minute=30)
#
# 添加任务 - 使用更复杂的 Cron 表达式
scheduler.add_job(my_job, 'cron', day_of_week='mon-fri', hour=9, minute=30)

# print('定时任务已启动，按 Ctrl+C 退出')
print(f'定时任务已启动: {datetime.now()}')

try:
    # 启动调度器
    scheduler.start()
    # False 是不等待任务完成 True是等待
    scheduler.shutdown(False)
except KeyboardInterrupt:
    print('定时任务已停止')