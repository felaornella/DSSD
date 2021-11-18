from datetime import timedelta
from os import  environ
from flask import Flask
from flask_session import Session
from config import config
from app import db
#from dotenv import load_dotenv
from app.db_sqlalchemy import db_sqlalchemy
from flask_bootstrap import Bootstrap
from flask_cors import CORS

from app.resources import sociedad
from app.resources import qr

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

    # archivos
    UPLOAD_FOLDER = '/static/uploads'
    ALLOWED_EXTENSIONS = {'pdf'}
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
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
    
    app.add_url_rule("/solicitud_estampillado", "estampillar", sociedad.estampillar,methods=["GET"])

    app.add_url_rule("/", "home", sociedad.home,methods=["GET"])
    app.add_url_rule("/login", "login_apoderado", sociedad.login_general_page,methods=["GET"])
    app.add_url_rule("/login", "login_apoderado_post", sociedad.login_general,methods=["POST"])
    app.add_url_rule("/register", "register_apoderado", sociedad.register_general_page,methods=["GET"])
    app.add_url_rule("/register", "register_apoderado_post", sociedad.register_general,methods=["POST"])
    app.add_url_rule("/logout", "logout_apoderado", sociedad.logout_general,methods=["GET"])
    app.add_url_rule("/gestion/login", "login_page", sociedad.loginPage,methods=["GET"])
    app.add_url_rule("/gestion/logout", "logout", sociedad.logout,methods=["GET"])
    app.add_url_rule("/gestion/login", "login", sociedad.login,methods=["POST"])
    app.add_url_rule("/nueva", "nueva_sa", sociedad.nuevaPag,methods=["GET"])
    app.add_url_rule("/nueva", "nueva_sa_agregar", sociedad.nueva,methods=["POST"])
    app.add_url_rule("/menu_mesa_de_entrada", "menu_mesa_de_entrada", sociedad.menu_mesaEntrada,methods=["GET"])
    app.add_url_rule("/menu_area_de_legales", "menu_area_de_legales", sociedad.menu_legales,methods=["GET"])
    app.add_url_rule("/evaluar_solicitudes", "evaluar_solicitudes", sociedad.evaluar_solicitudes,methods=["GET"])
    app.add_url_rule("/rechazar_solicitud", "rechazar_solicitud", sociedad.rechazar_solicitud,methods=["POST"])
    app.add_url_rule("/aceptar_solicitud", "aceptar_solicitud", sociedad.aceptar_solicitud,methods=["POST"])
    app.add_url_rule("/sociedad/<hash>", "vista_sociedad", sociedad.vista_sociedad,methods=["GET"])
    
    app.add_url_rule("/generar_qr/<id>", "generar_qr", qr.generar_qr,methods=["GET"])
    app.add_url_rule("/qr/<hash>", "obtener_qr", qr.obtener_qr,methods=["GET"])
    app.add_url_rule("/estatutos/<id>", "obtener_estatuto", sociedad.obtener_estatuo,methods=["GET"])
    app.add_url_rule("/generar-carpeta-virtual/<id>", "generar_carpeta_virtual", sociedad.generar_carpeta_virtual,methods=["GET"])
    app.add_url_rule("/sociedad/pdf/<id>", "obtener_pdf_sociedad", sociedad.obtener_pdf_sociedad,methods=["GET"])
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
    
