from apscheduler.schedulers.background import BackgroundScheduler
from analyzer import analyze_and_store
import time

def start_scheduler():
    sched = BackgroundScheduler()
    sched.add_job(analyze_and_store, "interval", minutes=10, jitter=30)  # roda a cada ~10min
    sched.start()
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        sched.shutdown()

if __name__ == "__main__":
    start_scheduler()
