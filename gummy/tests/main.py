import unittest
import transaction

from pyramid import testing

from ..models.db import DBSession


class TestMyView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        from ..models.db import Base
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with transaction.manager:
            pass
        #    model = MyModel(name='one', value=55)
        #    DBSession.add(model)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_index(self):
        from ..views.browse import index
        request = testing.DummyRequest()
        info = index(request)
        #self.assertEqual(info['events'], {})

    def test_project(self):
        from ..views.browse import project
        request = testing.DummyRequest()
        info = project(request)
        #self.assertEqual(info['events'], {})

    def test_branch(self):
        from ..views.browse import branch
        request = testing.DummyRequest()
        info = branch(request)
        #self.assertEqual(info['events'], {})
