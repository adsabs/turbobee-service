from flask_testing import TestCase
from flask import url_for, request
import unittest
import sys
sys.path.append('../')
from turbobee_app.models import Base, Pages
from turbobee_app import app
from mock import mock
from adsmsg import TurboBeeMsg
import datetime as dt
import dateutil.parser
from dateutil.tz import tzutc
from StringIO import StringIO
import pytz
import base64
from adsmutils import get_date

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

    def test_store_post(self):
        msg = TurboBeeMsg()
        now = dt.datetime.utcnow()
        msg.created = msg.get_timestamp(now)
        msg.updated = msg.get_timestamp(now)
        msg.expires = msg.get_timestamp(now)
        msg.eol = msg.get_timestamp(now)
        msg.set_value('hello world')
        msg.ctype = msg.ContentType.html
        msg.target = 'https:///some.com'
        msg.owner = 234
        my_data = {'file_field': (StringIO(msg.dump()[1]), 'turbobee_msg.proto') }

        r = self.client.post(
            url_for('turbobee_app.store', qid='asdf'), 
            content_type='multipart/form-data',
            data=my_data)

        self.assertEqual(r.status_code, 200)
        assert len(r.json['created']) == 1
        
        msg2 = msg.loads(*msg.dump())
        msg.qid = r.json['created'][0]
        r = self.client.post(
            url_for('turbobee_app.store'), 
            content_type='multipart/form-data',
            data={
                'foo': (StringIO(msg.dump()[1]), 'turbobee_msg.proto'),
                'bar': (StringIO(msg2.dump()[1]), 'turbobee_msg.proto'),
            })
        self.assertEqual(r.status_code, 200)
        assert len(r.json['created']) == 1
        assert len(r.json['updated']) == 1
    
        
        r = self.client.get(url_for('turbobee_app.store_get', qid=msg.qid))
        self.assertEqual(r.status_code, 200)
        r = self.client.head(url_for('turbobee_app.store_get', qid=msg.qid))
        self.assertEqual(r.status_code, 200)
        
        r = self.client.get(url_for('turbobee_app.store_get', qid='foo'))
        self.assertEqual(r.status_code, 404)
        r = self.client.head(url_for('turbobee_app.store_get', qid='foo'))
        self.assertEqual(r.status_code, 404)
        
    
    def test_files_form_post(self):
        """Check we can send data through both channels."""
        msg = TurboBeeMsg(value=u'\u6789'.encode('utf8'))
        msg2 = TurboBeeMsg(value=u'\u6789'.encode('utf8'))
        r = self.client.post(
            url_for('turbobee_app.store'), 
            content_type='multipart/form-data',
            data={
                'foo': base64.encodestring(msg.dump()[1]),
                'bar': (StringIO(msg2.dump()[1]), 'turbobee_msg.proto'),
            })
        assert len(r.json['created']) == 2
        msgs = list(self.app.get_pages(r.json['created']))
        for m in msgs:
            m['content'].decode('utf8') == u'\u6789'
        
    
    def test_proto_empty(self):
        msg = TurboBeeMsg()
        my_data = {'file_field': (StringIO(msg.dump()[1]), 'turbobee_msg.proto') }

        r = self.client.post(
            url_for('turbobee_app.store', qid='asdf'), 
            content_type='multipart/form-data',
            data=my_data)

        self.assertEqual(r.status_code, 200)
        
        with self.app.session_scope() as session:
            assert len(session.query(Pages).all()) == 1


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

<<<<<<< HEAD
        begin = get_date(dt.datetime.utcnow()) - dt.timedelta(hours=1)
        end = get_date(dt.datetime.utcnow()) + dt.timedelta(hours=1)
=======
        begin = dt.datetime.now(pytz.utc) - dt.timedelta(hours=1)
        end = dt.datetime.now(pytz.utc) + dt.timedelta(hours=1)
>>>>>>> 160f380610a5e9268f83c927897d396ae62c3e1a

        # url_for translates to: 
        # '/search?begin=2018-12-26T18%3A27%3A02.367394%2B00%3A00&rows=1&end=2018-12-26T20%3A27%3A02.367412%2B00%3A00'
        r = self.client.get(
            url_for('turbobee_app.search', begin=begin.isoformat(), end=end.isoformat(), rows=1))
        
        first_page = r.json[0]
        created = get_date(first_page['created'])

<<<<<<< HEAD
=======
        first_page = r.json[0]
        created = dateutil.parser.parse(first_page['created'])

>>>>>>> 160f380610a5e9268f83c927897d396ae62c3e1a
        self.assertLess(begin, created) 
        self.assertGreater(end, created)
        self.assertEqual(r.status_code, 200)

        
if __name__ == '__main__':
  unittest.main()
