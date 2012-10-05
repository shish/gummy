import os

from .git import GitProject
from .db import DBSession, Comment, Event


class Workspace(Event):
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


