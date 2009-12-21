"""

Sending and Receiving Messages

"""

from carrot.connection import DjangoBrokerConnection, AMQPConnectionException
from carrot.messaging import Publisher, Consumer, ConsumerSet
from billiard.utils.functional import wraps

from celery import conf
from celery import signals
from celery.utils import gen_unique_id, mitemgetter, noop


MSG_OPTIONS = ("mandatory", "priority",
               "immediate", "routing_key",
               "serializer")

get_msg_options = mitemgetter(*MSG_OPTIONS)
extract_msg_options = lambda d: dict(zip(MSG_OPTIONS, get_msg_options(d)))
default_queue = conf.routing_table[conf.DEFAULT_QUEUE]


class TaskPublisher(Publisher):
    """Publish tasks."""
    exchange = default_queue["exchange"]
    exchange_type = default_queue["exchange_type"]
    routing_key = conf.DEFAULT_ROUTING_KEY
    serializer = conf.TASK_SERIALIZER

    def delay_task(self, task_name, task_args=None, task_kwargs=None,
            task_id=None, taskset_id=None, **kwargs):
        """Delay task for execution by the celery nodes."""

        task_id = task_id or gen_unique_id()
        eta = kwargs.get("eta")
        eta = eta and eta.isoformat()

        message_data = {
            "task": task_name,
            "id": task_id,
            "args": task_args or [],
            "kwargs": task_kwargs or {},
            "retries": kwargs.get("retries", 0),
            "eta": eta,
        }

        if taskset_id:
            message_data["taskset"] = taskset_id

        self.send(message_data, **extract_msg_options(kwargs))
        signals.task_sent.send(sender=task_name, **message_data)

        return task_id


class TaskConsumer(Consumer):
    """Consume tasks"""
    queue = conf.DEFAULT_QUEUE
    exchange = default_queue["exchange"]
    routing_key = default_queue["binding_key"]
    exchange_type = default_queue["exchange_type"]


class EventPublisher(Publisher):
    """Publish events"""
    exchange = "celeryevent"
    routing_key = "event"


class EventConsumer(Consumer):
    """Consume events"""
    queue = "celeryevent"
    exchange = "celeryevent"
    routing_key = "event"
    exchange_type = "direct"
    no_ack = True


class BroadcastPublisher(Publisher):
    """Publish broadcast commands"""
    exchange = "celeryctl"
    exchange_type = "fanout"
    routing_key = ""

    def send(self, type, arguments, destination=None):
        """Send broadcast command."""
        arguments["command"] = type
        arguments["destination"] = destination
        super(BroadcastPublisher, self).send({"control": arguments})


class BroadcastConsumer(Consumer):
    """Consume broadcast commands"""
    queue = "celeryctl"
    exchange = "celeryctl"
    routing_key = ""
    exchange_type = "fanout"
    no_ack = True


def establish_connection(connect_timeout=conf.BROKER_CONNECTION_TIMEOUT):
    """Establish a connection to the message broker."""
    return DjangoBrokerConnection(connect_timeout=connect_timeout)


def with_connection(fun):
    """Decorator for providing default message broker connection for functions
    supporting the ``connection`` and ``connect_timeout`` keyword
    arguments."""

    @wraps(fun)
    def _inner(*args, **kwargs):
        connection = kwargs.get("connection")
        timeout = kwargs.get("connect_timeout", conf.BROKER_CONNECTION_TIMEOUT)
        kwargs["connection"] = conn = connection or \
                establish_connection(connect_timeout=timeout)
        close_connection = not connection and conn.close or noop

        try:
            return fun(*args, **kwargs)
        finally:
            close_connection()

    return _inner


def get_consumer_set(connection, queues=None, **options):
    """Get the :class:`carrot.messaging.ConsumerSet`` for a queue
    configuration.

    Defaults to the queues in ``CELERY_QUEUES``.

    """
    queues = queues or conf.routing_table
    return ConsumerSet(connection, from_dict=queues, **options)
