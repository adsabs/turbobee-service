from flask_script import Manager, Server
from turbobee_app.models import Pages, Records
from turbobee_app import app as application

app = application.create_app(**{
       'SQLALCHEMY_ECHO': False,
       'SQLALCHEMY_TRACK_MODIFICATIONS': False,
       'TESTING': True,
       'PROPAGATE_EXCEPTIONS': True,
       'TRAP_BAD_REQUEST_ERRORS': True
    })
manager = Manager(app)

@manager.shell
def make_shell_context():
    return dict(app=app, Pages=Pages, Records=Records)

if __name__=='__main__':
    manager.run()
