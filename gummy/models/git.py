import os
from subprocess import Popen, PIPE
from datetime import datetime
import re
import tempfile

from .workspace import Comment, Event


def nometa(text):
    text = re.sub("git-svn-id: .*", "", text)
    return text


class GitProject(Event):
    def __init__(self, workspace, name):
        self.type = "project"
        self._comments = None

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
        
        r = self.repo
        try:
            self._notes_tree = r[r[r.ref("refs/notes/commits")].tree]
        except KeyError:
            self._notes_tree = []
        try:
            self._reviews_tree = r[r[r.ref("refs/notes/review")].tree]
        except KeyError:
            self._reviews_tree = []

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
        base = "develop" if "develop" in all_branches else "master"
        unmerged_branches = self._get_branches(nomerged=base)

        branches = {}
        for name in all_branches:
            status = "merged"
            if name in unmerged_branches:
                status = "unmerged"
            branches[name] = GitBranch(self, name, base, status)

        return branches

    def get_branch(self, name):
        return self.get_branches()[name]

    def __str__(self):
        return "%s: %s" % (self.name, self.description)


class GitBranch(Event):
    def __init__(self, project, name, base, status):
        self.type = "branch"
        self._comments = None

        self.project = project
        self.base = base
        self.name = name
        c = project.repo[project.repo.ref("refs/heads/"+name)]
        self.message = nometa(c.message)
        self.timestamp = datetime.fromtimestamp(c.commit_time)
        self.status = status
        self.author = c.author
        self.key = (0 if self.status == "merged" else 1), self.timestamp

    def get_commits(self, squash=False):
        commits = []
        cmd = "cd %s && git rev-list %s..%s" % (self.project.root, self.base, self.name)
        for line in Popen(cmd, shell=True, stdout=PIPE).stdout.readlines():
            name = line.strip()
            commits.append(GitCommit(self, name))
        commits.reverse()
        return commits

    def get_commit(self, name):
        return GitCommit(self, name)

    def get_comments(self, recurse=False):
        if recurse:
            cs = []
            for commit in self.get_commits():
                cs.extend(commit.get_comments())
            return cs
        else:
            return []
            #cmd = "cd %s && git notes list %s" % (self.project.root, self.name)
            #note_sha = Popen(cmd, shell=True, stdout=PIPE).stdout.read()
            #return Comment.from_json(self.project.repo[note_sha])

    def get_participants(self):
        return list(set([x.author for x in self.get_commits() + self.get_comments(recurse=True)]))

    def __str__(self):
        return "%s %s " % (self.name, self.last_update)


class GitCommit(Event):
    def __init__(self, branch, name):
        self.type = "commit"

        c = branch.project.repo[name]
        self.branch = branch
        self.name = name
        self.author = c.author
        self.author_time = c.author_time
        self.committer = c.committer
        self.message = nometa(c.message)
        self.timestamp = datetime.fromtimestamp(c.author_time)
        self.key = self.timestamp

    @property
    def diff(self):
        cmd = "cd %s && git diff %s^1..%s" % (self.branch.project.root, self.name, self.name)
        diff = Popen(cmd, shell=True, stdout=PIPE).stdout.read()
        diff = diff.decode("utf8", "ignore")

        from pygments import highlight
        from pygments.lexers import DiffLexer
        from pygments.formatters import HtmlFormatter
        from jinja2 import Markup

        return Markup(highlight(diff, DiffLexer(), HtmlFormatter()))

    def get_patches(self):
        return []

    def get_comments(self):
        if self.name in self.branch.project._notes_tree:
            _note_mode, note_sha = self.branch.project._notes_tree[self.name]
            note_data = str(self.branch.project.repo[note_sha])
            return [Comment.from_pairs(self, d) for d in note_data.split("\n\n") if d.strip() != ""]
        else:
            return []
    
    def add_comment(self, comment):
        cmd = "cd %s && git notes append -F - %s" % (self.branch.project.root, self.name)
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE)
        p.communicate(comment.to_pairs())

    def __str__(self):
        return self.name + " " + self.author
