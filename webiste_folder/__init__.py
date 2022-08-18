import flask_monitoringdashboard as dashboard
#from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask
# from flask.ext.images import resized_img_src
import os

def create_app(test_config=None):
   app = Flask(__name__, instance_relative_config=True)

   app.config.from_mapping(
       SECRET_KEY='dev',
       DATABASE=os.path.join(app.instance_path, 'users.sqlite'),
       DEBUG_TB_PROFILER_ENABLED = False,
   )

   #debug tool
   # toolbar = DebugToolbarExtension(app)
   # dashboard.bind(app)
   if test_config is None:
      app.config.from_pyfile('config.py',silent=True)
   else:
      app.config.from_mapping(test_config)
      
   try:
      os.makedirs(app.instance_path)
   except OSError:
      pass
   
   from . import db
   db.init_app(app)
      
   from . import auth
   app.register_blueprint(auth.bp)
   
   from . import site_routes
   #push app context to access in site_routes
   app.register_blueprint(site_routes.bp)
   with app.app_context():
      site_routes.make_cache_config()
      
   return app

