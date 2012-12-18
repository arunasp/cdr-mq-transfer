from django.conf import settings

class MQRouter(object):
    """
    Send CDRs into different MQ broker queue
    """
    def route_for_task(self, task, args=None, kwargs=None):
        if task == 'cdr_mq_transfer.mq_receiver.GetCDR':
            return settings.CDR_REMOTE_MQ
        if task == 'cdr_mq_transfer.mq_transfer.SendCDR':
            return settings.CDR_LOCAL_MQ

        return None
