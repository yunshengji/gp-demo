import mongoengine
from flask_script import Manager
from flask_apidoc import ApiDoc

from demo import app, settings
from demo.api import v1  # noqa: F401

app.config['DEBUG'] = None
mongoengine.connect(settings.DB_NAME,
                    host=settings.DB_HOST,
                    port=settings.DB_PORT)

ApiDoc(app=app,
       url_path='/api/docs',
       folder_path='.',
       dynamic_url=False)

manager = Manager(app)

if __name__ == '__main__':
    manager.run()
