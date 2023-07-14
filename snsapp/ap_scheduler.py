from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
from .models import User

def delete_unactive():# 任意の関数名
    # ここに定期実行したい処理を記述する
    User.objects.filter(is_active=0).delete()
    print("==Userテーブルから不要なレコードを削除==")

def time_test():
    dt_now = datetime.datetime.now()
    print("タイムスタンプ" + str(dt_now))
    #delete_unactive()

def start():
  scheduler = BackgroundScheduler()
  scheduler.add_job(delete_unactive, 'cron', hour=23, minute=59)# 毎日23時59分に実行
  scheduler.add_job(time_test, 'interval', seconds=10)
  scheduler.start()
