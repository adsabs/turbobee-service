from flask_script import Manager, Server
from adsmutils import ADSFlask
from turbobee_app.views import bp
from turbobee_app.models import Pages, Records
from turbobee_app.app import SampleADSFlask

app = SampleADSFlask('sample')
app.url_map.strict_slashes = False    
app.register_blueprint(bp)

manager = Manager(app)

@manager.shell
def make_shell_context():
    return dict(app=app, Pages=Pages, Records=Records)

if __name__=='__main__':
    manager.run()
