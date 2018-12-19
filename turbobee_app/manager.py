from flask_script import Manager, Server
from adsmutils import ADSFlask
from views import bp
from models import Base, Pages
from app import SampleADSFlask, create_app

# app = SampleADSFlask('sample')
# app.url_map.strict_slashes = False    
# app.register_blueprint(bp)

a = create_app(**{
       'SQLALCHEMY_DATABASE_URI': 'sqlite:///turbobee_cache',
       'SQLALCHEMY_ECHO': False,
       'SQLALCHEMY_TRACK_MODIFICATIONS': False,
       'TESTING': True,
       'PROPAGATE_EXCEPTIONS': True,
       'TRAP_BAD_REQUEST_ERRORS': True
    })
Base.metadata.bind = a.db.session.get_bind()
Base.metadata.create_all()

manager = Manager(a)

@manager.shell
def make_shell_context():
    return dict(app=a, Pages=Pages)

if __name__=='__main__':
    manager.run()
