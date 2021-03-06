from django.conf import settings
from django import db
from django.core import exceptions
from datetime import datetime, date, timedelta
from celery.execute import send_task
from celery.task import Task, PeriodicTask
from cdr_mq_transfer.models import CdrTail
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
	    from cdr_mq_transfer.mq_receiver import GetCDR
	    logger.info('Running task :: SendCDR')
	    rows_count_query = settings.DATABASES['asterisk']['ROWS_COUNT']
	    row = CdrTail.objects.get(pk=1)
	    savedrow = row.lastrow
	    logger.debug("SendCDR :: last saved row in CDR database: %d" % (savedrow))
	    rows = self.DBQuery('asterisk',rows_count_query)
	    rows_count = int(rows[1][0])
	    logger.debug("SendCDR :: The CDR table has %d rows." % rows_count)
	    if (savedrow < rows_count):
		query = settings.DATABASES['asterisk']['TAIL_CDR'] % (rows_count, savedrow)
		result = self.DBQuery('asterisk',query)
		logger.debug("SendCDR :: Asterisk CDR backend result:")
		for row in result:
		    logger.debug("%s" % str(row))

		logger.debug("SendCDR :: Sending CDRs to MQ broker..")
		CDRresult = GetCDR.apply_async(queue="cdr-mq-transfer",countdown=1,args=result)
		run = "New CDRs sent: %d" % (rows_count - savedrow + 1)
		row = CdrTail(pk=1, lastrow = rows_count)
		row.save()
	    else:
		logger.debug("SendCDR :: No new CDRs found")

	except Exception as e:
	    logger.error("SendCDR :: Failed: %s (%s, %s)" % (e.message, type(e), e))
#	    self.update_state(state=states.FAILURE)
	    return e

	return run

    def DBQuery(self,_db='default',_query=''):
	# Query backend database and return results
	logger = self.get_logger()
	logger.debug('Running DBQuery :: (DB: "%s", QUERY: "%s")' % (_db,_query))
	DBQuery = None
	try:
	    _cursor = db.connections[_db].cursor()
	    _cursor.execute(_query)
	    DBQuery = _cursor.description + _cursor.fetchall()
	    _cursor.close()
	except Exception as e:
	    logger.error("DBQuery :: transaction failed: %s (%s, %s)" % (e.message, type(e), e))
	    raise

	return DBQuery
