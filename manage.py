import sys
import importlib
import os
import time
from work_muxixyz_app import create_app,db
from work_muxixyz_app.models import Team,Group,User,Project,Message,Statu,File,Comment
from flask_script import Manager,Shell,Command
from flask_migrate import Migrate,MigrateCommand

importlib.reload(sys)
#export PYTHONIOENCODING="UTF-8"

app=create_app(os.getenv('FLASK_CONFIG') or 'default')
manager=Manager(app)
migrate=Migrate(app,db)

manager.add_command('db',MigrateCommand)

def make_shell_context():
    return dict(app=app)

manager.add_command("shell",Shell(make_context=make_shell_context))

@manager.command
def test_management():

    import unittest
    tests=unittest.TestLoader().discover('test_management')
    unittest.TextTestRunner(verbosity=2).run(tests)

@manager.command
def test_project():

    import unittest
    tests=unittest.TestLoader().discover('test_project')
    unittest.TextTestRunner(verbosity=2).run(tests)

@manager.command
def createdb():
    db.create_all()

if __name__=='__main__':
    manager.run()
    app.run(debug=True)