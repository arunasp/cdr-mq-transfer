from django.conf import settings
from django import db
from django.core import exceptions
from datetime import datetime, date, timedelta
from celery.task import Task, PeriodicTask
from cdr_mq_transfer.models import Cdr
from cdr_mq_transfer.task_lock import only_one

#Ensure we have long time enough to finish task
LOCK_EXPIRE = 60 * 60 * 1  # Lock expires in 1 hours

class SendCDR(Task):
    """
    Upload CDRs into message broker from Asterisk database
    """
#    run_every = timedelta(minutes=1)

    @only_one(key="SendCDR", timeout=LOCK_EXPIRE)
    def run(self, **kwargs):
	#Grab CDRs from Asterisk backend database
	logger = self.get_logger()
	run = None
	
	try:
	    logger.info('Running task :: SendCDR')
	    rows_count_query = settings.DATABASES['asterisk']['ROWS_COUNT']
	    lastrow = self.DBQuery('asterisk',rows_count_query)
	    lastrow = 30
	    rows = self.DBQuery('asterisk',rows_count_query)
	    for row in rows:
		rows_count = int(row[0])
	    logger.debug("SendCDR :: The CDR table has %d rows." % rows[0])
	    query = settings.DATABASES['asterisk']['TAIL_CDR'] % (rows_count, lastrow)
	    result = self.DBQuery('asterisk',query)
	    logger.debug("SendCDR :: Asterisk CDR backend result:")
	    for row in result:
		logger.debug("%s" % str(row))

	    logger.debug("SendCDR :: Sending CDRs to MQ broker..")
	    GetCDR.delay(result)
	    #GetCDR.apply_async(result,queue="cdr-mq-transfer",countdown=1)

	except Exception as e:
	    logger.error("SendCDR :: Failed: %s (%s, %s)" % (e.message, type(e), e))
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
	    DBQuery = _cursor.fetchall()
	    _cursor.close()
	except Exception as e:
	    logger.error("DBQuery :: transaction failed: %s (%s, %s)" % (e.message, type(e), e))

	return DBQuery

class GetCDR(Task):
    """
    Download Asterisk CDRs from message broker
    """
    run_every = timedelta(minutes=1)

    @only_one(key="GetCDR", timeout=LOCK_EXPIRE)
    def run(self, CDR, **kwargs):
	logger = self.get_logger()
	run = None
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

#tasks.register(SendCDR)
