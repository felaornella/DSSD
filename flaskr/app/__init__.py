from datetime import datetime, timedelta
from os import path, environ
from types import MethodType
from flask import Flask, render_template, g, session, redirect, url_for, jsonify
from flask.helpers import send_file
from flask.wrappers import Response
from flask_session import Session
from werkzeug.wrappers import ResponseStreamMixin
from config import config
from app import db
#from dotenv import load_dotenv
from app.helpers import handler
from app.helpers import auth as helper_auth
from app.db_sqlalchemy import db_sqlalchemy
from flask import request
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
from flask_cors import CORS,cross_origin
from app.resources import sociedad
import app.helpers.bonita as bonita 

#va development
def create_app(environment="development"):
    #load_dotenv()

    # Configuración inicial de la app
    app = Flask(__name__)
    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'
    
    # Carga de la configuración
    env = environ.get("FLASK_ENV", environment)
    app.config.from_object(config[env])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = b'6hc/_gsh,./;2ZZx3c6_s,1//'
    
    # Server Side session
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=90)
    Session(app)
    Bootstrap(app)

    # Configure db
    db.init_app(app)

    # Configure sqlAlchemy
    conf = app.config
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://" + \
        conf["DB_USER"]+":"+conf["DB_PASS"]+"@" + \
        conf["DB_HOST"]+"/"+conf["DB_NAME"] + "?charset=utf8mb4"
    db_sqlalchemy.init_app(app)
    db_sqlalchemy.app=app
    db_sqlalchemy.create_all()
    # Configure secure_filename
    UPLOAD_FOLDER = 'static/uploads'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    app.add_url_rule("/login", "login_page", sociedad.loginPage,methods=["GET"])
    app.add_url_rule("/login", "login", sociedad.login,methods=["POST"])
    app.add_url_rule("/nueva", "nueva_sa", sociedad.nuevaPag,methods=["GET"])
    app.add_url_rule("/nueva", "nueva_sa_agregar", sociedad.nueva,methods=["POST"])
    return app

'''
    # Funciones que se exportan al contexto de Jinja2
    app.jinja_env.globals.update(is_authenticated=helper_auth.authenticated)
    
    @app.errorhandler(InternalServer)
    def handle_object_not_found_error(e):
        return jsonify({'message': str(e)}), 500

    @app.errorhandler(BadRequest)
    def handle_object_not_found_error(e):
        return jsonify({'message': str(e)}), 400

    # Handlers
    app.register_error_handler(404, handler.not_found_error)
    app.register_error_handler(401, handler.unauthorized_error)
    # Implementar lo mismo para el error 500 y 401
   

'''
    
