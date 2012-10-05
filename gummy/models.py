from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    )

from sqlalchemy import func

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Event(object):
    def __cmp__(self, other):
        return cmp(str(self.key), str(other.key))


class Comment(Base, Event):
    __tablename__ = 'comment'

    id = Column(Integer, nullable=False, primary_key=True)
    
    project = Column(Text)
    branch = Column(Text)
    commit = Column(Text)
    file = Column(Text)
    line = Column(Integer)
    
    author = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=func.now())
    message = Column(Text, nullable=False)
    
    def __init__(self, author, message, project=None, branch=None, commit=None, file=None, line=None, timestamp=None):
        self.project = project
        self.branch = branch
        self.commit = commit
        self.file = file
        self.line = line
        
        self.author = author
        self.message = message
        if timestamp:
            self.timestamp = timestamp

    @property
    def type(self):
        return "comment"

    @property
    def key(self):
        return self.timestamp


import os
from subprocess import Popen, PIPE
from datetime import datetime


class Workspace(object):
    def __init__(self, root):
        self.root = root

    def get_projects(self):
        projects = {}
        for project in os.listdir(self.root):
            fullpath = os.path.join(self.root, project)
            if os.path.exists(os.path.join(fullpath, ".git", "HEAD")) or os.path.exists(os.path.join(fullpath, "HEAD")):
                projects[project] = GitProject(self, project)
        return projects

    def get_project(self, name):
        return self.get_projects()[name]

    def get_comments(self):
        return DBSession.query(Comment).filter(
            Comment.project==None,
            Comment.branch==None,
            Comment.commit==None
        ).all()


class GitProject(object):
    def __init__(self, workspace, name):
        self.workspace = workspace
        self.name = name
        self.key = self.name

        if os.path.exists(os.path.join(workspace.root, name, ".git", "HEAD")):
            self.root = os.path.join(workspace.root, name, ".git")
        elif os.path.exists(os.path.join(workspace.root, name, "HEAD")):
            self.root = os.path.join(workspace.root, name)

        from dulwich.repo import Repo
        self.repo = Repo(self.root)

        if os.path.exists(os.path.join(self.root, "description")):
            self.description = file(os.path.join(self.root, "description")).read()
        else:
            self.description = "No description file found"

    def _get_branches(self, nomerged=None):
        branches = []
        if nomerged:
            cmd = "cd %s && git branch --no-merged %s" % (self.root, nomerged)
        else:
            cmd = "cd %s && git branch" % self.root
        for line in Popen(cmd, shell=True, stdout=PIPE).stdout.readlines():
            branches.append(line[2:].strip())
        return branches

    def get_branches(self):
        all_branches = self._get_branches()
        main = "develop" if "develop" in all_branches else "master"
        unmerged_branches = self._get_branches(nomerged=main)

        branches = {}
        for name in all_branches:
            status = "merged"
            if name in unmerged_branches:
                status = "unmerged"
            branches[name] = GitBranch(self, name, status)

        return branches

    def get_branch(self, name):
        return self.get_branches()[name]

    def get_comments(self):
        return DBSession.query(Comment).filter(
            Comment.project==self.name,
            Comment.branch==None,
            Comment.commit==None
        ).all()

    def __str__(self):
        return "%s: %s" % (self.name, self.description)


class GitBranch(object):
    def __init__(self, project, name, status):
        self.project = project
        self.name = name
        c = project.repo[project.repo.ref("refs/heads/"+name)]
        self.message = c.message
        self.last_update = datetime.fromtimestamp(c.commit_time)
        self.status = status
        self.key = self.status, self.last_update

    def get_commits(self):
        commits = []
        cmd = "cd %s && git rev-list master..%s" % (self.project.root, self.name)
        for line in Popen(cmd, shell=True, stdout=PIPE).stdout.readlines():
            name = line.strip()
            commits.append(GitCommit(self, name))
        commits.reverse()
        return commits

    def get_commit(self, name):
        return GitCommit(self, name)

    def get_comments(self):
        return DBSession.query(Comment).filter(
            Comment.project==self.project.name,
            Comment.branch==self.name,
            Comment.commit==None
        ).all()

    def __str__(self):
        return "%s %s " % (self.name, self.last_update)


class GitCommit(Event):
    def __init__(self, branch, name):
        c = branch.project.repo[name]
        self.branch = branch
        self.name = name
        self.author = c.author
        self.author_time = c.author_time
        self.committer = c.committer
        self.message = c.message
        self.datetime = datetime.fromtimestamp(c.author_time)
        self.key = self.datetime
        
        cmd = "cd %s && git diff %s^1..%s" % (self.branch.project.root, self.name, self.name)
        self.diff = Popen(cmd, shell=True, stdout=PIPE).stdout.read()
        self.diff = self.diff.decode("utf8", "ignore")

    def get_patches(self):
        return []

    def get_comments(self):
        return DBSession.query(Comment).filter(
            Comment.project==self.branch.project.name,
            Comment.branch==self.branch.name,
            Comment.commit==self.name
        ).all()

    def __str__(self):
        return self.name + " " + self.author

