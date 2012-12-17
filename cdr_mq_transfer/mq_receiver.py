from django.conf import settings
from django import db
from django.core import exceptions
from datetime import datetime, date, timedelta
from celery.task import Task, PeriodicTask
from cdr_mq_transfer.models import Cdr
from cdr_mq_transfer.task_lock import only_one

#Ensure we have long time enough to finish task
LOCK_EXPIRE = 60 * 60 * 1  # Lock expires in 1 hours

class GetCDR(Task):
    """
    Download Asterisk CDRs from message broker
    """
    run_every = timedelta(minutes=1)

    @only_one(key="GetCDR", timeout=LOCK_EXPIRE)
    def run(self, *args, **kwargs):
        logger = self.get_logger()
        run = None
        CDR = args

        try:
            logger.info('Running task :: GetCDR')
            logger.debug("GetCDR :: Received CDR entries:")
            for entry in CDR:
                row = str(entry)
                logger.debug(row)

        except Exception as e:
            logger.error("GetCDR :: Failed: %s (%s, %s)" % (e.message, type(e), e))
            return e
        return run

