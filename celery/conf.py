import logging
from datetime import timedelta

from celery.registry import tasks
from celery.loaders import settings

DEFAULT_LOG_FMT = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'

LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "WARN": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
    "FATAL": logging.FATAL,
}

_DEFAULTS = {
    "CELERY_AMQP_EXCHANGE": "celery",
    "CELERY_AMQP_PUBLISHER_ROUTING_KEY": "celery",
    "CELERY_AMQP_CONSUMER_ROUTING_KEY": "celery",
    "CELERY_AMQP_CONSUMER_QUEUE": "celery",
    "CELERY_AMQP_EXCHANGE_TYPE": "direct",
    "CELERYD_CONCURRENCY": 0, # defaults to cpu count
    "CELERYD_PID_FILE": "celeryd.pid",
    "CELERYD_DAEMON_LOG_FORMAT": DEFAULT_LOG_FMT,
    "CELERYD_DAEMON_LOG_LEVEL": "WARN",
    "CELERYD_LOG_FILE": "celeryd.log",
    "CELERY_ALWAYS_EAGER": False,
    "CELERY_TASK_RESULT_EXPIRES": timedelta(days=5),
    "CELERY_AMQP_CONNECTION_TIMEOUT": 4,
    "CELERY_AMQP_CONNECTION_RETRY": True,
    "CELERY_AMQP_CONNECTION_MAX_RETRIES": 100,
    "CELERY_TASK_SERIALIZER": "pickle",
    "CELERY_BACKEND": "database",
    "CELERY_DISABLE_RATE_LIMITS": False,
    "CELERYBEAT_PID_FILE": "celerybeat.pid",
    "CELERYBEAT_LOG_LEVEL": "INFO",
    "CELERYBEAT_LOG_FILE": "celerybeat.log",
    "CELERYBEAT_SCHEDULE_FILENAME": "celerybeat-schedule",
    "CELERYBEAT_MAX_LOOP_INTERVAL": 5 * 60, # five minutes.
    "CELERYMON_PID_FILE": "celerymon.pid",
    "CELERYMON_LOG_LEVEL": "INFO",
    "CELERYMON_LOG_FILE": "celerymon.log",
    "CELERY_SEND_EVENTS": False,
    "CELERY_STORE_ERRORS_EVEN_IF_IGNORED": False,
}

def _get(name, default=None):
    if default is None:
        default = _DEFAULTS.get(name)
    return getattr(settings, name, default)

SEND_EVENTS = _get("CELERY_SEND_EVENTS")
ALWAYS_EAGER = _get("CELERY_ALWAYS_EAGER")
CELERY_BACKEND = _get("CELERY_BACKEND")
CELERY_CACHE_BACKEND = _get("CELERY_CACHE_BACKEND")
DEFAULT_RATE_LIMIT = _get("CELERY_DEFAULT_RATE_LIMIT")
DISABLE_RATE_LIMITS = _get("CELERY_DISABLE_RATE_LIMITS")
STORE_ERRORS_EVEN_IF_IGNORED = _get("CELERY_STORE_ERRORS_EVEN_IF_IGNORED")
TASK_SERIALIZER = _get("CELERY_TASK_SERIALIZER")
TASK_RESULT_EXPIRES = _get("CELERY_TASK_RESULT_EXPIRES")
# Make sure TASK_RESULT_EXPIRES is a timedelta.
if isinstance(TASK_RESULT_EXPIRES, int):
    TASK_RESULT_EXPIRES = timedelta(seconds=TASK_RESULT_EXPIRES)
SEND_CELERY_TASK_ERROR_EMAILS = _get("SEND_CELERY_TASK_ERROR_EMAILS",
                                     not settings.DEBUG)

AMQP_EXCHANGE = _get("CELERY_AMQP_EXCHANGE")
AMQP_EXCHANGE_TYPE = _get("CELERY_AMQP_EXCHANGE_TYPE")
AMQP_PUBLISHER_ROUTING_KEY = _get("CELERY_AMQP_PUBLISHER_ROUTING_KEY")
AMQP_CONSUMER_ROUTING_KEY = _get("CELERY_AMQP_CONSUMER_ROUTING_KEY")
AMQP_CONSUMER_QUEUE = _get("CELERY_AMQP_CONSUMER_QUEUE")
DEFAULT_AMQP_CONSUMER_QUEUES = {
        AMQP_CONSUMER_QUEUE: {
            "exchange": AMQP_EXCHANGE,
            "routing_key": AMQP_CONSUMER_ROUTING_KEY,
            "exchange_type": AMQP_EXCHANGE_TYPE,
        }
}
AMQP_CONSUMER_QUEUES = _get("CELERY_AMQP_CONSUMER_QUEUES",
                            DEFAULT_AMQP_CONSUMER_QUEUES)
AMQP_CONNECTION_TIMEOUT = _get("CELERY_AMQP_CONNECTION_TIMEOUT")
AMQP_CONNECTION_RETRY = _get("CELERY_AMQP_CONNECTION_RETRY")
AMQP_CONNECTION_MAX_RETRIES = _get("CELERY_AMQP_CONNECTION_MAX_RETRIES")

LOG_FORMAT = _get("CELERYD_DAEMON_LOG_FORMAT")
DAEMON_LOG_FILE = _get("CELERYD_LOG_FILE")
DAEMON_LOG_LEVEL = _get("CELERYD_DAEMON_LOG_LEVEL")
DAEMON_LOG_LEVEL = LOG_LEVELS[DAEMON_LOG_LEVEL.upper()]
DAEMON_PID_FILE = _get("CELERYD_PID_FILE")
DAEMON_CONCURRENCY = _get("CELERYD_CONCURRENCY")

CELERYBEAT_PID_FILE = _get("CELERYBEAT_PID_FILE")
CELERYBEAT_LOG_LEVEL = _get("CELERYBEAT_LOG_LEVEL")
CELERYBEAT_LOG_FILE = _get("CELERYBEAT_LOG_FILE")
CELERYBEAT_SCHEDULE_FILENAME = _get("CELERYBEAT_SCHEDULE_FILENAME")
CELERYBEAT_MAX_LOOP_INTERVAL = _get("CELERYBEAT_MAX_LOOP_INTERVAL")

CELERYMON_PID_FILE = _get("CELERYMON_PID_FILE")
CELERYMON_LOG_LEVEL = _get("CELERYMON_LOG_LEVEL")
CELERYMON_LOG_FILE = _get("CELERYMON_LOG_FILE")
