from django.conf import settings
from django import db
from datetime import date, timedelta
from celery.task import Task, PeriodicTask
from cdr_mq_transfer.models import Cdr

class SendCDR(PeriodicTask):
    run_every = timedelta(minutes=1)

    def run(self, **kwargs):
        self.get_logger().info("Time now: " + datetime.now())
        print("Time now: " + datetime.now())

class GetCDR(PeriodicTask):
    run_every = timedelta(minutes=1)

    def run(self, **kwargs):
        self.get_logger().info("Time now: " + datetime.now())
        print("Time now: " + datetime.now())

# tasks.register(SendCDR)
