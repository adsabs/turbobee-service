
import unittest
from sample_application import app, models
import os, json
from mock import mock

class TestCase(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.app = app.SampleADSFlask('test', local_config=\
            {
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///',
            'SQLALCHEMY_ECHO': False
            })
        models.Base.metadata.bind = self.app.db.session.get_bind()
        models.Base.metadata.create_all()
    
    
    def tearDown(self):
        self.app.close_app()
        unittest.TestCase.tearDown(self)
        models.Base.metadata.drop_all()


    def test_date(self):
        assert self.app.get_date('2018-09-07 19:13:44.327512+00:00') == '2018-09-07 19:13:44.327512+00:00'
        


if __name__ == '__main__':
    unittest.main()