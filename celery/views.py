"""celery.views"""
from django.http import HttpResponse, Http404

from anyjson import serialize as JSON_dump

from celery.result import AsyncResult
from celery.execute import apply_async
from celery.registry import tasks


def apply(request, task_name, *args):
    """View applying a task.

    Example:
        http://e.com/celery/apply/task_name/arg1/arg2//?kwarg1=a&kwarg2=b

    **NOTE** Use with caution, preferably not make this publicly accessible
    without ensuring your code is safe!

    """
    kwargs = request.method == "POST" and \
            request.POST.copy() or request.GET.copy()
    kwargs = dict((key.encode("utf-8"), value)
                    for key, value in kwargs.items())
    if task_name not in tasks:
        raise Http404("apply: no such task")

    task = tasks[task_name]
    result = apply_async(task, args=args, kwargs=kwargs)
    response_data = {"ok": "true", "task_id": result.task_id}
    return HttpResponse(JSON_dump(response_data), mimetype="application/json")


def is_task_successful(request, task_id):
    """Returns task execute status in JSON format."""
    response_data = {"task": {"id": task_id,
                              "executed": AsyncResult(task_id).successful()}}
    return HttpResponse(JSON_dump(response_data), mimetype="application/json")
is_task_done = is_task_successful # Backward compatible


def task_status(request, task_id):
    """Returns task status and result in JSON format."""
    async_result = AsyncResult(task_id)
    status = async_result.status
    result = async_result.result
    if status in ("FAILURE", "RETRY"):
        response_data = {
            "id": task_id,
            "status": status,
            "result": result.args[0],
            "traceback": result.traceback,
        }
    else:
        response_data = {
            "id": task_id,
            "status": status,
            "result": result,
        }
    return HttpResponse(JSON_dump({"task": response_data}),
            mimetype="application/json")
