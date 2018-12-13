from flask_script import Manager, Server
from adsmutils import ADSFlask
from views import bp
from app import SampleADSFlask

app = SampleADSFlask('sample')
app.url_map.strict_slashes = False    
app.register_blueprint(bp)

manager = Manager(app)

@manager.shell
def make_shell_context():
    return dict(app=app)

if __name__=='__main__':
    manager.run()
