import unittest
from turbobee_app import app, models
import os, json
from mock import mock
from adsmsg import TurboBeeMsg, Status
from adsmutils import get_date
from datetime import datetime
from turbobee_app.tests.base import TestCaseDatabase
import dateutil.parser
import pdb

class TestCase(TestCaseDatabase):

    def setUp(self):
        TestCaseDatabase.setUp(self)
        #self.app = app.create_app(**{
        #    'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        #     'SQLALCHEMY_ECHO': True})
        models.Base.metadata.bind = self.app.db.session.get_bind()
        models.Base.metadata.create_all()
    
    
    def tearDown(self):
        models.Base.metadata.drop_all()
        TestCaseDatabase.tearDown(self)
        self.app.close_app()

    
    def test_set_get_pages(self):
        msg = TurboBeeMsg()
        now = datetime.utcnow()
        
        msg.created = msg.get_timestamp(now)
        msg.updated = msg.get_timestamp(now)
        msg.expires = msg.get_timestamp(now)
        msg.eol = msg.get_timestamp(now)
        msg.set_value('hello world')
        msg.ctype = msg.ContentType.html
        msg.target = 'https:///some.com'
        msg.owner = 234
        
        r = self.app.set_pages([msg])
        assert 'created' in r
        assert len(r['created']) ==1
        
        pages = list(self.app.get_pages(r['created']))
        expected = {
            'id': 1,
            'target': u'https:///some.com', 
            'content_type': u'application/html', 
            'content': 'hello world', 
            'created': get_date(now).isoformat(), 
            'updated': get_date(now).isoformat(), 
            'expires': get_date(now).isoformat(), 
            'lifetime': get_date(now).isoformat(),
            'owner': 234,
            'qid': pages[0]['qid']
            }
        assert pages[0] == expected
        
        msg.qid = pages[0]['qid']
        r = self.app.set_pages([msg])
        assert 'updated' in r
        assert len(r['updated']) ==1
        assert r['updated'][0] == expected['qid']
        
        msg.status = Status.deleted
        r = self.app.set_pages([msg])
        assert 'deleted' in r
        assert r['deleted'][0] == expected['qid']
        
        r = self.app.set_pages([msg])
        assert r['ignored-deleted'][0] == expected['qid']
        assert len(list(self.app.get_pages(expected['qid']))) == 0
        
        # insert it again
        msg.status = Status.active
        r = self.app.set_pages([msg])
        assert r['created'][0]
        assert r['created'][0] != expected['qid']
        
        l = list(self.app.get_pages(r['created'], fields=['foo', 'qid', 'content', 'created']))
        assert l[0]['qid'] == r['created'][0]
        assert l[0]['created'] == expected['created']
        assert l[0]['content'] == 'hello world'
        assert 'updated' not in l[0]
        assert 'foo' not in l[0]
        
        
        # set multiple objects at once
        msg.qid = r['created'][0]
        msg2 = msg.loads(*msg.dump())
        msg2.qid = ''
        r = self.app.set_pages([msg, msg2])
        assert r['created'][0] 
        assert r['updated'][0] == msg.qid
        
        # update one by one
        msg2.qid = r['created'][0]
        r = self.app.set_pages([msg, msg2], one_by_one=True)
        assert msg.qid in r['updated']
        assert msg2.qid in r['updated']
        
        
        r = self.app.set_pages([msg, msg2, msg, msg, msg], one_by_one=True)
        assert set(r['updated']) == set([msg.qid, msg2.qid])
        
if __name__ == '__main__':
    unittest.main()
