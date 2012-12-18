"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase
from cdr_mq_transfer.models import CdrTail

class CdrTestCase(TestCase):
    fixtures = ['CdrTail.json', 'CdrTail']

    def setUp(self):
        # Test definitions as before.
        call_setup_methods()

    def testInitialCdrTail(self):
        # A test that uses the fixtures.
        try:
    	    lastrow = CdrTail.objects.values('lastrow')[0]
