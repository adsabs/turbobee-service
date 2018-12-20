from flask_testing import TestCase
from flask import url_for, request
import unittest
from turbobee_app.models import Base, Pages
from turbobee_app import app
from mock import mock
from adsmsg import TurboBeeMsg
import datetime as dt
from StringIO import StringIO

class TestServices(TestCase):
    '''Tests that each route is an http response'''

    def create_app(self):
        '''Start the wsgi application'''
        a = app.create_app(**{
               'SQLALCHEMY_DATABASE_URI': 'sqlite:///',
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



    def test_proto_msg(self):
        msg = TurboBeeMsg()
        msg.created = msg.get_timestamp(dt.datetime.utcnow())
        msg.set_value('hello world')
        my_data = {'file_field': (StringIO(msg.dump()[1]), 'turbobee_msg.proto') }

        r = self.client.post(
            url_for('turbobee_app.store', qid='asdf'), 
            content_type='multipart/form-data',
            data=my_data)

        self.assertEqual(r.status_code, 200)

    def test_proto_empty(self):
        msg = TurboBeeMsg()
        my_data = {'file_field': (StringIO(msg.dump()[1]), 'turbobee_msg.proto') }

        r = self.client.post(
            url_for('turbobee_app.store', qid='asdf'), 
            content_type='multipart/form-data',
            data=my_data)

        self.assertEqual(r.status_code, 200)

    # delete an existing page
    def test_proto_delete(self):
        with self.app.session_scope() as session:
            session.add(Pages(qid='wxyz'))
            session.commit()
        r = self.client.delete(url_for('turbobee_app.store', qid='wxyz'))
        self.assertEqual(r.status_code, 200)

    # delete a page that does not exist
    def test_proto_delete_ne(self):
        r = self.client.delete(url_for('turbobee_app.store', qid='does_not_exist'))
        self.assertEqual(r.status_code, 404)

    # search for pages with specified timestamp
    def test_search_get_range_at(self):
        at = dt.datetime.utcnow()

        page = Pages(qid='wxyz', content='hi', created=at)
        self.app.db.session.add(page)
        self.app.db.session.commit()


        r = self.client.get(
            url_for('turbobee_app.search', at=at))

        self.assertEqual(r.status_code, 200)

    # search for pages within timestamp range, when pages exist
    def test_search_get_range(self):
        page = Pages(qid='wxyz', content='hi')
        page2 = Pages(qid='wxyz2', content='hi 2')
        self.app.db.session.add(page)
        self.app.db.session.add(page2)
        self.app.db.session.commit()

        begin = dt.datetime.utcnow() - dt.timedelta(days=30)
        end = dt.datetime.utcnow() + dt.timedelta(days=30)

        r = self.client.get(
            url_for('turbobee_app.search', begin=begin, end=end))

        self.assertEqual(r.status_code, 200)

    # search for pages within timestamp range, when pages exist, with rows
    def test_search_get_range_rows(self):
        page = Pages(qid='wxyz', content='hi')
        page2 = Pages(qid='wxyz2', content='hi 2')
        self.app.db.session.add(page)
        self.app.db.session.add(page2)
        self.app.db.session.commit()

        begin = dt.datetime.utcnow() - dt.timedelta(days=30)
        end = dt.datetime.utcnow() + dt.timedelta(days=30)

        r = self.client.get(
            url_for('turbobee_app.search', begin=begin, end=end, rows=1))

        self.assertEqual(r.status_code, 200)

    # get a page that exists
    def test_proto_get(self):
        page = Pages(qid='wxyz', content='hi')
        self.app.db.session.add(page)
        self.app.db.session.commit()
        r = self.client.get(
            url_for('turbobee_app.store', qid='wxyz'))

        self.assertEqual(r.status_code, 200)

    # get a page that doesn't exist
    def test_proto_get_dne(self):
        r = self.client.get(
            url_for('turbobee_app.store', qid='does_not_exist'))

        self.assertEqual(r.status_code, 404)


        
if __name__ == '__main__':
  unittest.main()
