import os
import sys
import transaction
from datetime import datetime

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models.db import (
    DBSession,
    Base,
    Comment,
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        model = Comment(
            author="Shish <shish@shishnet.org>",
            message="global comment",
            timestamp=datetime(2012, 10, 04, 23, 03, 35))
        DBSession.add(model)

        model = Comment(
            project="gummy",
            author="Shish <shish@shishnet.org>",
            message="project comment",
            timestamp=datetime(2012, 10, 04, 23, 03, 35))
        DBSession.add(model)

        model = Comment(
            project="gummy",
            branch="templates",
            author="Shish <shish@shishnet.org>",
            message="branch comment",
            timestamp=datetime(2012, 10, 04, 19, 20, 28))
        DBSession.add(model)
        
        model = Comment(
            project="gummy",
            branch="templates",
            commit="b8e4447d1cd7e729bd23668df416cb7fd23aaae5",
            author="Shish <shish@shishnet.org>",
            message="commit comment",
            timestamp=datetime(2012, 10, 04, 23, 03, 35))
        DBSession.add(model)

        model = Comment(
            project="gummy",
            branch="templates",
            commit="b8e4447d1cd7e729bd23668df416cb7fd23aaae5",
            file="Makefile",
            line=6,
            author="Shish <shish@shishnet.org>",
            message="file comment",
            timestamp=datetime(2012, 10, 04, 23, 03, 35))
        DBSession.add(model)
