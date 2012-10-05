from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

import transaction

from sqlalchemy.exc import DBAPIError
from subprocess import Popen, PIPE
import os

from .models import (
    DBSession,
    Workspace,
    Comment
    )


appconf = {
    "project_root": "/home/shish/workspace/",
}


@view_config(route_name='index', renderer='templates/index.jinja2')
def index(request):
    workspace = Workspace(appconf.get("project_root"))
    
    comments = workspace.get_comments()
    projects = workspace.get_projects()
    events = comments + projects.values()

    return {'events': events}


@view_config(route_name='project', renderer='templates/project.jinja2')
def project(request):
    workspace = Workspace(appconf.get("project_root"))
    project = workspace.get_project(request.matchdict["project"])
    
    comments = project.get_comments()
    branches = project.get_branches()
    events = comments + branches.values()

    return {"project": project, "events": sorted(events)}


@view_config(route_name='branch', renderer='templates/branch.jinja2')
def branch(request):
    workspace = Workspace(appconf.get("project_root"))
    project = workspace.get_project(request.matchdict["project"])
    branch = project.get_branch(request.matchdict["branch"])

    #try:
    #    one = DBSession.query(MyModel).filter(MyModel.name=='one').first()
    #except DBAPIError:
    #    return Response(conn_err_msg, content_type='text/plain', status_int=500)

    commits = branch.get_commits()
    comments = branch.get_comments()
    events = commits + comments

    return {"project": project, "branch": branch, "events": sorted(events)}


@view_config(route_name='commit', renderer='templates/commit.jinja2')
def commit(request):
    workspace = Workspace(appconf.get("project_root"))
    project = workspace.get_project(request.matchdict["project"])
    branch = project.get_branch(request.matchdict["branch"])
    commit = branch.get_commit(request.matchdict["commit"])

    patches = [commit, ]
    comments = commit.get_comments()
    events = patches + comments

    return {"project": project, "branch": branch, "commit": commit, "events": sorted(events)}


@view_config(route_name='add_comment')
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


conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_gummy_db" script
    to initialize your database tables.  Check your virtual 
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""

