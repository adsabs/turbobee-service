#!/usr/bin/python
# -*- coding: utf-8 -*-

from adsmutils import ADSFlask, get_date
from views import bp
from flask import Response

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
        ctype = page_obj.ctype or 'application/octet-stream'
        return Response(page_obj.content, content_type=ctype)

	"""
    def update_row(self, **kwargs):
		with self.session_scope() as session:
			x = session.query(model.Row).filter_by(qid=....).first()
			y = model.Row(qid=23)
			session.add(y)
			session.commit()
		print y
	"""
