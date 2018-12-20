#!/usr/bin/python
# -*- coding: utf-8 -*-

from adsmutils import ADSFlask, get_date
from views import bp
from flask import Response
from turbobee_app.models import Pages
from sqlalchemy.orm import load_only
from uuid import uuid4
from sqlalchemy.exc import IntegrityError
from adsmsg import TurboBeeMsg, Status

def create_app(**config):
    """
    Create the application and return it to the user
    :return: flask.Flask application
    """

    app = TurboBeeADSFlask('turbobee', local_config=config)
    app.url_map.strict_slashes = False    
    app.register_blueprint(bp)
    return app

# ctypes as saved by the TurboBeeMsg protobuf
ctypes = { 
    0:'octet-stream', # unknown
    1:'html',
    2:'text',
    3:'json',
    4:'octet-stream', # binary
    5:'png'}

class TurboBeeADSFlask(ADSFlask):
    
    def __init__(self, *args, **kwargs):
        ADSFlask.__init__(self, *args, **kwargs)
        
        # HTTP client is provided by requests module; it handles connection pooling
        # here we just set some headers we always want to use while sending a request
        self.client.headers.update({'Authorization': 'Bearer {}'.format(self.config.get("API_TOKEN", ''))})
        
        
        
    def guess_ctype(self, msg):
        """Based on the contents of the protobuf, returns the 
        content-type that will be saved into a database.
        
        @param msg: TurboBeeMsg protobuf
        @return: (string)
        """
        if not msg.ctype:
            return 'application/octet-stream'
        return 'application/' + ctypes[msg.ctype]
    
    def wrap_response(self, page_obj):
        """Prepares a flask response object with appropriate 
        headers.
        
        @param page_obj: instance of the models.Page
        @return: Flask Response.
        """ 
        # by default, it is always there - but just in case...
        ctype = page_obj.content_type or 'application/octet-stream'
        return Response(page_obj.content, content_type=ctype)


    def get_pages(self, qids, fields=None):
        """Utility method to retrieve bunch of pages.
        
        @param qids: list of qids
        @param fields: list of fields to load (optional)
        @return: list of dicts"""
        
        out = []
        with self.session_scope() as session:
            q = session.query(Pages).filter(Pages.qid.in_(qids))
            
            fields_to_load = []
            if fields:
                fields_to_load = list(set(fields) & Pages.valid_fields)
                q = q.options(load_only(*fields_to_load))
            
            for page in q.yield_per(100):
                if fields_to_load:
                    yield page.toJSON(fields=fields_to_load)
                else:
                    yield page.toJSON()
    
    def set_pages(self, msgs, fail_fast=False, one_by_one=False):
        """Utility method to insert into the db bunch of 
        messages
        
        @param msgs: list of TurboBeeMsg instances
        @return: dict with qids of 'created', 'updated',
            'errors'
        """
        
        with self.session_scope() as session:
            out = {}
            for msg in msgs:
                op = 'updated'
                page = None
                # object may already be there, we are updating it...
                if msg.qid:
                    page = session.query(Pages).filter_by(qid=msg.qid).first()
                    
                if msg.status == Status.deleted and page is None:
                    if 'ignored' not in out:
                        out['ignored-deleted'] = []
                    out['ignored-deleted'].append(msg.qid)
                    continue
                            
                if page is None:
                    op = 'created'
                    page = Pages(qid=uuid4().hex)
                    session.add(page)
                
                if msg.status == Status.deleted:
                    op = 'deleted'
                    session.delete(page)
                else:
                    now = get_date()
                    page.target = msg.target or page.target # transfer the old defaults
                    page.content = msg.get_value()
                    
                    # timestamps in msgs are datetime naive, make sure we apply timezone
                    page.created = msg.created.seconds and get_date(msg.get_datetime(msg.created)) or now 
                    page.content_type = self.guess_ctype(msg)
                    page.updated = msg.updated.seconds and get_date(msg.get_datetime(msg.updated)) or now
                    # should we provide defaults if not set?
                    page.expires = msg.expires.seconds and get_date(msg.get_datetime(msg.expires)) or None 
                    page.lifetime = msg.eol.seconds and get_date(msg.get_datetime(msg.eol)) or None
                    page.owner = msg.owner
                
                # keep the qid for later use (when session is expunged)
                qid = page.qid
                
                # insert one by one
                if one_by_one:
                    try:
                        session.commit()
                    except Exception as e:
                        self.logger.error('Error inserting %s into db. Message=%s', msg, e.message)
                        session.rollback()
                        if fail_fast:
                            raise e
                        else:
                            if 'errors' not in out:
                                out['errors'] = []
                            out['errors'].append({'qid': qid, 'msg': e.message})
                
                if op not in out:
                    out[op] = []
                out[op].append(qid)
                
            if not one_by_one:
                try:
                    session.commit()
                except IntegrityError as e:
                    self.logger.error('Error inserting data into db. Message=%s', e.message)
                    session.rollback()
                    if fail_fast:
                        raise e
                    else:
                        if 'errors' not in out:
                            out['errors'] = []
                        out['errors'].append({'qid': None, 'msg': e.message})
        return out
            