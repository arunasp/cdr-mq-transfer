from django.conf import settings
from django import db
from django.core import exceptions
from datetime import datetime, date, timedelta
from celery.task import Task, PeriodicTask
from cdr_mq_transfer.models import Cdr
from cdr_mq_transfer.task_lock import only_one

#Ensure we have long time enough to finish task
LOCK_EXPIRE = 60 * 60 * 1  # Lock expires in 1 hours

class SendCDR(PeriodicTask):
    """
    Upload CDRs into message broker from Asterisk database
    """
    run_every = timedelta(minutes=1)

    @only_one(key="SendCDR", timeout=LOCK_EXPIRE)
    def run(self, **kwargs):
	#Grab CDRs from Asterisk backend database
	logger = self.get_logger()
	run = None
	
	try:
	    logger.info('Running task :: SendCDR')
	    cursor = db.connections['asterisk'].cursor()
	    cursor.use_debug_cursor = True
	    lastrow = 30
	    rows_count_query = settings.DATABASES['asterisk']['ROWS_COUNT']
	    cursor.execute(rows_count_query)
	    rows = cursor.fetchone()
	    logger.debug("SendCDR :: The CDR table has %d rows." % rows[0])
#	    cursor.close
#	    cursor = db.connections['asterisk'].cursor()
	    query = settings.DATABASES['asterisk']['TAIL_CDR']
	    cursor.execute(query, (int(rows[0]), lastrow))
	    result = cursor.fetchall()
#		print (var(result))
	    logger.debug("SendCDR :: Asterisk CDR backend result:")
	    for row in result:
		logger.debug("%s" % str(row))
    	    cursor.close()

	except Exception as e:
	    logger.error("SendCDR :: Failed: %s (%s, %s)" % (e.message, type(e), e))
	    return e
	return run

class GetCDR(PeriodicTask):
    """
    Download Asterisk CDRs from message broker
    """
    run_every = timedelta(minutes=1)

    @only_one(key="GetCDR", timeout=LOCK_EXPIRE)
    def run(self, **kwargs):
	logger = self.get_logger()
	run = None
	
	try:
    	    logger.info("GetCDR :: Time now: %s" % datetime.now())
    	    print("GetCDR :: Time now: %s" % datetime.now())
	except Exception as e:
	    logger.error("GetCDR :: Failed: %s (%s, %s)" % (e.message, type(e), e))
	    return e
	return run

# tasks.register(SendCDR)
