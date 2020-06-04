import os
import unittest
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from project import server, db

server.config.from_object(os.environ['APP_SETTINGS'])

migrate = Migrate(server, db)
manager = Manager(server)

manager.add_command('db', MigrateCommand)


@manager.command
def test():
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()