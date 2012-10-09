from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

import datetime

from ..models.workspace import Comment


@view_config(route_name='comment', request_method="POST")
def add_comment(request):
    c = Comment(
        author = request.POST.get("author"),
        message = request.POST.get("message"),
        file = request.POST.get("file") or None,
        line = request.POST.get("line") or None,
        timestamp = datetime.datetime.now(),
    )
    return HTTPFound(request.referrer)
