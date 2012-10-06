import os
from subprocess import Popen, PIPE
from datetime import datetime

from .db import DBSession, Comment, Event


class GitProject(Event):
    def __init__(self, workspace, name):
        self.workspace = workspace
        self.name = name
        self.key = self.name

        if os.path.exists(os.path.join(workspace.root, name, ".git", "HEAD")):
            self.root = os.path.join(workspace.root, name, ".git")
        elif os.path.exists(os.path.join(workspace.root, name, "HEAD")):
            self.root = os.path.join(workspace.root, name)

        self.timestamp = datetime.fromtimestamp(os.path.getmtime(self.root))
        self.key = self.timestamp

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


class GitBranch(Event):
    def __init__(self, project, name, status):
        self.project = project
        self.base = "master"
        self.name = name
        c = project.repo[project.repo.ref("refs/heads/"+name)]
        self.message = c.message
        self.timestamp = datetime.fromtimestamp(c.commit_time)
        self.status = status
        self.key = (1 if self.status == "merged" else 0), self.timestamp

    def get_commits(self, squash=False):
        if squash:
            return [GitCommitSquash(self, self.name), ]
        else:
            commits = []
            cmd = "cd %s && git rev-list %s..%s" % (self.project.root, self.base, self.name)
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
        self.timestamp = datetime.fromtimestamp(c.author_time)
        self.key = self.timestamp

    @property
    def diff(self):
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


class GitCommitSquash(Event):
    def __init__(self, branch, name):
        c = branch.project.repo[branch.project.repo.ref("refs/heads/"+branch.base)]
        self.branch = branch
        self.name = name
        self.author = "Team"
        self.author_time = c.author_time
        self.committer = "Team"
        self.message = "Multiple Commits"
        self.datetime = datetime.fromtimestamp(c.author_time)
        self.key = self.datetime

    @property
    def diff(self):
        cmd = "cd %s && git diff %s..%s" % (self.branch.project.root, self.branch.base, self.name)
        diff = Popen(cmd, shell=True, stdout=PIPE).stdout.read()
        diff = diff.decode("utf8", "ignore")
        return diff


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

