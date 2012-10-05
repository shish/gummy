from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

import transaction

from sqlalchemy.exc import DBAPIError
from subprocess import Popen, PIPE
import os

from ..models import (
    DBSession,
    Workspace,
    Comment
    )

@view_config(route_name='comment', request_method="POST")
def add_comment(request):
    with transaction.manager:
        model = Comment(
            project = request.POST.get("project"),
            branch = request.POST.get("branch"),
            commit = request.POST.get("commit"),
            file = request.POST.get("file"),
            line = request.POST.get("line"),
            author = request.POST.get("author"),
            message = request.POST.get("message"),
        )
        DBSession.add(model)
    return HTTPFound(request.url)
