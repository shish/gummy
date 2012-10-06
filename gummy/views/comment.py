from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

import transaction

from sqlalchemy.exc import DBAPIError
from subprocess import Popen, PIPE
import os
import datetime

from ..models.db import (
    DBSession,
    Comment
    )
from ..models.workspace import (
    Workspace,
    )

@view_config(route_name='comment', request_method="POST")
def add_comment(request):
    with transaction.manager:
        model = Comment(
            project = request.POST.get("project") or None,
            branch = request.POST.get("branch") or None,
            commit = request.POST.get("commit") or None,
            file = request.POST.get("file") or None,
            line = request.POST.get("line") or None,
            author = request.POST.get("author"),
            message = request.POST.get("message"),
            timestamp = datetime.datetime.now(),
        )
        DBSession.add(model)
    return HTTPFound(request.referrer)
