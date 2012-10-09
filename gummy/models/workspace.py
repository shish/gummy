import os
from datetime import datetime
import uuid

from .db import DBSession


class Event(object):
    def __init__(self, type=None):
        self._comments = None
        self.type = type

    @property
    def comments(self):
        if not self._comments:
            self.comments = self.get_comments()
        return self._comments


class Workspace(Event):
    def __init__(self, root):
        Event.__init__(self, "workspace")
        self.root = root

    def get_projects(self):
        from .git import GitProject
        
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


class Comment(Event):
    def __init__(self, author, message, id=None, project=None, branch=None, commit=None, file=None, line=None, timestamp=None):
        Event.__init__(self, "comment")

        if id:
            self.id = id
        else:
            self.id = uuid.uuid1()

        self.project = project
        self.branch = branch
        self.commit = commit

        self.author = author
        self.message = message
        
        self.file = file
        self.line = line
        
        if timestamp:
            if isinstance(timestamp, str):
                self.timestamp = datetime.strptime(timestamp[:19], "%Y-%m-%d %H:%M:%S")
            else:
                self.timestamp = timestamp
        else:
            self.timestamp = datetime.now()
        self.key = self.timestamp
    
    @classmethod
    def from_pairs(cls, commit, data):
        args = {
            "project": commit.branch.project,
            "branch": commit.branch,
            "commit": commit,
        }
        for line in data.split("\n"):
            try:
                k, v = line.split(": ", 2)
                args[k.lower()] = v
            except:
                pass
        return Comment(**args)

    def to_pairs(self):
        ps = []
        for k in ["id", "author", "message", "timestamp"]:
            ps.append("%s: %s" % (k.title(), getattr(self, k)))
        return "\n".join(ps)


class CommitStreak(Event):
    def __init__(self, branch):
        Event.__init__(self, "commitstreak")

        self.branch = branch
        self.commits = []

    def addCommit(self, commit):
        self.commits.append(commit)
        self.timestamp = commit.timestamp
        self.author = commit.author
        self.key = commit.key


class CommentBox(Event):
    def __init__(self, project=None, branch=None, commit=None, file=None, line=None, author=None):
        Event.__init__(self, "commentbox")

        self.author = author

        self.project = project
        self.branch = branch
        self.commit = commit
        self.file = file
        self.line = line

        self.key = "zzz"


class StatusBox(Event):
    def __init__(self, reviewed, verified):
        Event.__init__(self, "statusbox")
        
        self.reviewed = reviewed
        self.verified = verified

        self.key = "yyy"
