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
    def __init__(self):
        self._comments = None

    @property
    def comments(self):
        if not self._comments:
            self.comments = self.get_comments()
        return self._comments


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
        Event.__init__(self)

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
