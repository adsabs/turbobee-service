#!/usr/bin/python
# -*- coding: utf-8 -*-

from adsmutils import ADSFlask, get_date
from views import bp

def create_app(**config):
    """
    Create the application and return it to the user
    :return: flask.Flask application
    """

    app = SampleADSFlask('sample', local_config=config)
    app.url_map.strict_slashes = False    
    app.register_blueprint(bp)
    return app


class SampleADSFlask(ADSFlask):
    
    def __init__(self, *args, **kwargs):
        ADSFlask.__init__(self, *args, **kwargs)
        
        # HTTP client is provided by requests module; it handles connection pooling
        # here we just set some headers we always want to use while sending a request
        self.client.headers.update({'Authorization': 'Bearer {}'.format(self.config.get("API_TOKEN", ''))})
        
    def get_date(self, date=None):
        """
        :return: UTC date
        """

        self.logger.info('Example of logging within the app.')
        return get_date(date).isoformat()

	"""
    def update_row(self, **kwargs):
		with self.session_scope() as session:
			x = session.query(model.Row).filter_by(qid=....).first()
			y = model.Row(qid=23)
			session.add(y)
			session.commit()
		print y
	"""
