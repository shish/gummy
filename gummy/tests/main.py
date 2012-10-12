import unittest
import transaction
import os

from pyramid import testing

from ..models.db import DBSession


class TestBrowse(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.add_settings(project_root="../")
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        from ..models.db import Base
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with transaction.manager:
            pass
        #    model = MyModel(name='one', value=55)
        #    DBSession.add(model)
        
        self.project = os.path.basename(os.getcwd())

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_index(self):
        from ..views.browse import index
        request = testing.DummyRequest()
        info = index(request)
        self.assertEqual(type(info['events']), list)

    def test_project(self):
        from ..views.browse import project
        request = testing.DummyRequest(matchdict={
            "project": self.project,
        })
        info = project(request)
        self.assertEqual(type(info['events']), list)

    def test_branch(self):
        from ..views.browse import branch
        request = testing.DummyRequest(matchdict={
            "project": self.project,
            "branch": "develop",
        })
        info = branch(request)
        self.assertEqual(type(info['events']), list)

    def test_commit(self):
        from ..views.browse import branch
        request = testing.DummyRequest(matchdict={
            "project": self.project,
            "branch": "develop",
            "commit": "29e5d5631cc84f25427b52689e015687018c288f",
        })
        info = branch(request)
        self.assertEqual(type(info['events']), list)
