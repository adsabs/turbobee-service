
import unittest
from turbobee_app import app, models
import os, json
from mock import mock

class TestCase(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.app = app.create_app(local_config=\
            {'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
             'SQLALCHEMY_ECHO': False})
        models.Base.metadata.bind = self.app.db.session.get_bind()
        models.Base.metadata.create_all()
    
    
    def tearDown(self):
        self.app.close_app()
        unittest.TestCase.tearDown(self)
        models.Base.metadata.drop_all()




if __name__ == '__main__':
    unittest.main()
