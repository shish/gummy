from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

import transaction

from sqlalchemy.exc import DBAPIError
from subprocess import Popen, PIPE
import os

from ..models.db import (
    DBSession,
    Comment
    )
from ..models.workspace import (
    Workspace,
    CommitStreak,
    CommentBox,
    )


appconf = {
    "project_root": os.path.expanduser("~/workspace/"),
}


@view_config(route_name='index', renderer='templates/index.jinja2')
def index(request):
    workspace = Workspace(appconf.get("project_root"))

    comments = workspace.get_comments()
    projects = workspace.get_projects()
    events = comments + projects.values()

    events = sorted(events)
    events.reverse()

    return {'events': events}


@view_config(route_name='project', renderer='templates/project.jinja2')
def project(request):
    workspace = Workspace(appconf.get("project_root"))
    project = workspace.get_project(request.matchdict["project"])

    comments = project.get_comments()
    branches = project.get_branches()
    events = comments + branches.values()

    events = sorted(events)
    events.reverse()

    return {"project": project, "events": events}


@view_config(route_name='branch', renderer='templates/branch.jinja2')
def branch(request):
    workspace = Workspace(appconf.get("project_root"))
    project = workspace.get_project(request.matchdict["project"])
    branch = project.get_branch(request.matchdict["branch"])

    #try:
    #    one = DBSession.query(MyModel).filter(MyModel.name=='one').first()
    #except DBAPIError:
    #    return Response(conn_err_msg, content_type='text/plain', status_int=500)

    squash = request.GET.get("squash", "off") == "on"

    commits = branch.get_commits(squash)
    comments = branch.get_comments()
    events = sorted(commits + comments)

    grouped = []
    for c in events:
        if not grouped:
            cs = CommitStreak(c.branch)
            cs.addCommit(c)
            grouped = [cs, ]
        elif grouped[-1].commits[0].author == c.author and grouped[-1].commits[0].type == "commit" and c.type == "commit":
            grouped[-1].addCommit(c)
        else:
            cs = CommitStreak(c.branch)
            cs.addCommit(c)
            grouped.append(cs)

    for n, g in enumerate(grouped):
        #if len(g.commits) == 1:
        if g.commits[0].type != "commit":
            grouped[n] = g.commits[0]

    grouped.append(CommentBox(project=project, branch=branch))

    return {"project": project, "branch": branch, "events": grouped}


@view_config(route_name='commit', renderer='templates/commit.jinja2')
def commit(request):
    workspace = Workspace(appconf.get("project_root"))
    project = workspace.get_project(request.matchdict["project"])
    branch = project.get_branch(request.matchdict["branch"])
    commit = branch.get_commit(request.matchdict["commit"])

    patches = [commit, ]
    comments = commit.get_comments()
    events = patches + comments

    events.append(CommentBox(project=project, branch=branch, commit=commit))

    return {"project": project, "branch": branch, "commit": commit, "events": sorted(events)}
