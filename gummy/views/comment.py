from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

import datetime
import os

from ..models.workspace import Workspace, Comment


@view_config(route_name='comment', request_method="POST")
def add_comment(request):
    w = Workspace(os.path.expanduser(request.registry.settings['project_root']))
    p = w.get_project(request.POST.get("project"))
    b = p.get_branch(request.POST.get("branch"))
    if request.POST.get("commit"):
        target = b.get_commit(request.POST.get("commit"))
    else:
        #target = b  # comment on the branch itself
        target = b.get_commits()[-1]  # most recent commit

    d = {}
    d["id"] = request.POST.get("id") or None
    d["author"] = request.POST.get("author") or None
    d["message"] = request.POST.get("message") or None
    d["project"] = request.POST.get("project") or None
    d["branch"] = request.POST.get("branch") or None
    d["commit"] = request.POST.get("commit") or None
    d["file"] = request.POST.get("file") or None
    d["line"] = request.POST.get("line") or None

    if request.POST.get("review") not in ["0", "", None]:
        d["review"] = request.POST.get("review")
    if request.POST.get("verify") not in ["0", "", None]:
        d["verify"] = request.POST.get("verify")

    d["timestamp"] = datetime.datetime.now()

    if not d["author"]:
        return "Author is needed!"

    target.add_comment(Comment(**d))
    
    return HTTPFound(request.referrer or "/")
