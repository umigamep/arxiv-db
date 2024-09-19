import time

import schedule


# 実行job関数
def job():
    print("job実行")


# 5秒毎のjob実行を登録
schedule.every(5).seconds.do(job)

# AM11:00のjob実行を登録
# schedule.every().day.at("11:00").do(job)

# jobの実行監視、指定時間になったらjob関数を実行
while True:
    schedule.run_pending()
    time.sleep(1)
