from flask_testing import TestCase
from flask import url_for, request
import unittest
from models import Base
import app
import json
import os
from mock import mock
import httpretty
from adsmsg import TurboBeeMsg
import datetime as dt

class TestServices(TestCase):
    '''Tests that each route is an http response'''

    def create_app(self):
        '''Start the wsgi application'''
        a = app.create_app(**{
               'SQLALCHEMY_DATABASE_URI': 'sqlite:///turbobee_cache',
               'SQLALCHEMY_ECHO': False,
               'SQLALCHEMY_TRACK_MODIFICATIONS': False,
               'TESTING': True,
               'PROPAGATE_EXCEPTIONS': True,
               'TRAP_BAD_REQUEST_ERRORS': True
            })
        Base.metadata.bind = a.db.session.get_bind()
        Base.metadata.create_all()
        return a


    def tearDown(self):
        unittest.TestCase.tearDown(self)
        Base.metadata.drop_all()
        self.app.db = None


    def test_date(self):
        # if you want to know the urls: print self.app.url_map
        r = self.client.post(url_for('turbobee_app.date', date='2018-09-10 20:15:57'))
        self.assertEqual(r.status_code,200)
        assert r.json == {u'date': u'2018-09-10T20:15:57+00:00'}
    
        r = self.client.get(url_for('turbobee_app.date', date='2018-09-10 20:15:57'))
        self.assertEqual(r.status_code,200)
        assert r.json == {u'date': u'2018-09-10T20:15:57+00:00'}
    
        r = self.client.get(url_for('turbobee_app.date'))
        self.assertEqual(r.status_code,200)
        assert 'date' in r.json

    def test_proto(self):
        msg = TurboBeeMsg()
        msg.created = msg.get_timestamp(dt.datetime.utcnow())
        msg.set_value('hello world')
        # my_data = { 'file_field': (msg, 'turbobee_msg.proto') }
        my_data = {
            'q': '*:*',
            'fl': 'bibcode',
            'fq': '{!bitset}',
            'file_field': (msg, 'turbobee_msg.proto')
        }

        r = self.client.post(
            url_for('turbobee_app.store', bibcode='asdf'), 
            content_type='multipart/form-data',
            data=my_data)

        self.assertEqual(r.status_code, 200)
        
if __name__ == '__main__':
  unittest.main()
