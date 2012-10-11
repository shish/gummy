from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

import datetime
import os
import uuid

from ..models.workspace import Workspace, Comment


@view_config(route_name='comment', request_method="POST")
def add_comment(request):
    w = Workspace(os.path.expanduser("~/workspace/"))
    p = w.get_project(request.POST.get("project"))
    b = p.get_branch(request.POST.get("branch"))
    if request.POST.get("commit"):
        target = b.get_commit(request.POST.get("commit"))
    else:
        #target = b  # comment on the branch itself
        target = b.get_commits()[-1]  # most recent commit
    
    target.add_comment(Comment(
        id = request.POST.get("id") or None,
        author = request.POST.get("author"),
        message = request.POST.get("message"),
        project = request.POST.get("project"),
        branch = request.POST.get("branch"),
        commit = request.POST.get("commit"),
        file = request.POST.get("file") or None,
        line = request.POST.get("line") or None,
        review = request.POST.get("review") or None,
        verify = request.POST.get("verify") or None,
        timestamp = datetime.datetime.now(),
    ))
    
    return HTTPFound(request.referrer)
