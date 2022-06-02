from celery import Celery
from decouple import config

app = Celery('task', broker=config('CELERY_BROKER'))

@app.task
def send_otp_to_user():
    pass