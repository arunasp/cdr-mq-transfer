# Django settings for celeryproject project.
import os
import djcelery
from datetime import timedelta
from kombu import Queue
djcelery.setup_loader()

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

APPLICATION_DIR = os.path.dirname(globals()['__file__'])

MANAGERS = ADMINS

APPLICATION_DIR = os.path.dirname(globals()['__file__'])

DATABASES = {
    'default': { 
        # Add 'postgresql_psycopg2','postgresql','mysql','sqlite3','oracle'
        'ENGINE': 'django.db.backends.sqlite3',
        # Or path to database file if using sqlite3.
        'NAME': APPLICATION_DIR+'/celery.db',
        'USER': '',       # Not used with sqlite3.
        'PASSWORD': '',   # Not used with sqlite3.
        'HOST': '',     # Set to empty string for localhost.
        'PORT': '',           # Set to empty string for default.
    },
    'asterisk': { 
	'ROWS_COUNT': 'select count(calldate) from cdr',
        'TAIL_CDR': 'select * from cdr limit %s offset %s',
        # Add 'postgresql_psycopg2','postgresql','mysql','sqlite3','oracle'
        'ENGINE': 'django.db.backends.mysql',
        # Or path to database file if using sqlite3.
        'NAME': 'asterisk',
        'USER': 'root',       # Not used with sqlite3.
        'PASSWORD': '',   # Not used with sqlite3.
        'HOST': '127.0.0.1',     # Set to empty string for localhost.
        'PORT': '3306',           # Set to empty string for default.
    }
}

CACHES = {
    'default': {
        #'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        #'BACKEND': 'redis_cache.RedisCache',
        #'LOCATION': '127.0.0.1:6379',
        'LOCATION': '/var/tmp/cdr-mq',
        'TIMEOUT': '600',  # 600 secs
    }
}

#Include for cache machine : http://jbalogh.me/projects/cache-machine/
CACHE_BACKEND = 'caching.backends.filebased://'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
#TIME_ZONE = 'America/New_York'
TIME_ZONE = 'GMT'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://people.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = ''

# Make this unique, and don't share it with anybody.
SECRET_KEY = '7AMEz6mxjejHZRp2z5HFMadXasY4u41oeVXICiqS11U6YPLU2d'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'geordi.VisorMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'linaro_django_pagination.middleware.PaginationMiddleware',
    'common.filter_persist_middleware.FilterPersistMiddleware',
    #'mongodb_connection_middleware.MongodbConnectionMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates"
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(APPLICATION_DIR, 'templates'),
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    #'admin_tools',
    #'admin_tools.theming',
    'django.contrib.auth',
    #'admin_tools.dashboard',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'djcelery',
    'south',
    'cdr_mq_transfer',
)

CELERY_TIMEZONE = TIME_ZONE
CELERY_BACKEND = "database"

CDR_SENDER = True
#CDR_SENDER = False

#BROKER_HOST = "localhost"
#BROKER_PORT = 5672
#BROKER_USER = "myusername"
#BROKER_PASSWORD = "mypassword"
#BROKER_VHOST = "myvhost"
BROKER_URL="amqp://myusername:mypassword@localhost:5672/myvhost"

CELERY_DEFAULT_EXCHANGE = "cdr-mq"
CELERY_DEFAULT_EXCHANGE_TYPE = "topic"

CDR_PRODUCER_MQ = { 
    'queue': 'default',
    'binding_key': os.uname()[1]+'-tasks.#',
}

CDR_CONSUMER_MQ = { 
    'queue': 'cdr-mq-transfer',
    'binding_key': 'CDR.#'
}



CELERY_ACKS_LATE="True"
CELERYD_CONCURRENCY=1
CELERYBEAT_MAX_LOOP_INTERVAL=10

if (CDR_SENDER):
    INSTALLED_APPS += ('cdr_mq_transfer.mq_transfer',)
    CELERY_DEFAULT_QUEUE = CDR_PRODUCER_MQ['queue']
    CELERY_DEFAULT_ROUTING_KEY = CDR_PRODUCER_MQ['binding_key']
    CELERY_IMPORTS =  ("cdr_mq_transfer.mq_transfer",)
    CELERYBEAT_SCHEDULE = {
	'send-cdrs-schedule': {
    	    'task': 'cdr_mq_transfer.mq_transfer.SendCDR',
    	    'schedule': timedelta(seconds=10),
    	    'args': (),
	},
    }
    CELERY_DEFAULT_QUEUE = 'default'
else:
    INSTALLED_APPS += ('cdr_mq_transfer.mq_receiver',)
    CELERY_DEFAULT_QUEUE = CDR_CONSUMER_MQ['queue']
    CELERY_DEFAULT_ROUTING_KEY = CDR_CONSUMER_MQ['binding_key']
    CELERY_IMPORTS =  ("cdr_mq_transfer.mq_receiver",)

CELERY_ROUTES = { 'cdr_mq_transfer.mq_router.MQRouter', }
