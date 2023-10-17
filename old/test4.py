import time
from apscheduler.schedulers.background import BackgroundScheduler


def expiry_callback():
    print("before exc")
    raise ValueError
    print("inside job")


sched = BackgroundScheduler(daemon=True)
sched.add_job(expiry_callback,'interval', seconds=1)
sched.start()

time.sleep(100)