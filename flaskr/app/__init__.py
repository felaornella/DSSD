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

from app.resources import sociedad,estadisticas,qr,estampillado,logins_users


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
    
    

    app.add_url_rule("/", "home", sociedad.home,methods=["GET"])


    app.add_url_rule("/login", "login_apoderado", logins_users.login_general_page,methods=["GET"])
    app.add_url_rule("/login", "login_apoderado_post", logins_users.login_general,methods=["POST"])
    app.add_url_rule("/register", "register_apoderado", logins_users.register_general_page,methods=["GET"])
    app.add_url_rule("/register", "register_apoderado_post", logins_users.register_general,methods=["POST"])
    app.add_url_rule("/logout", "logout_apoderado", logins_users.logout_general,methods=["GET"])

    app.add_url_rule("/gestion/login", "login_page", logins_users.loginPage,methods=["GET"])
    app.add_url_rule("/gestion/login", "login", logins_users.login,methods=["POST"])
    app.add_url_rule("/gestion/logout", "logout", logins_users.logout,methods=["GET"])

    app.add_url_rule("/menu_apoderado", "menu_apoderado", sociedad.menu_apoderado,methods=["GET"])
    app.add_url_rule("/menu_mesa_de_entrada", "menu_mesa_de_entrada", sociedad.menu_mesaEntrada,methods=["GET"])
    app.add_url_rule("/menu_area_de_legales", "menu_area_de_legales", sociedad.menu_legales,methods=["GET"])
    app.add_url_rule("/menu_gerencia", "menu_gerencia", sociedad.menu_gerencia,methods=["GET"])

    app.add_url_rule("/nueva", "nueva_sa", sociedad.nuevaPag,methods=["GET"])
    app.add_url_rule("/nueva", "nueva_sa_agregar", sociedad.nueva,methods=["POST"])
    app.add_url_rule("/editar/<hash>", "edicion_sa", sociedad.editarPag ,methods=["GET"])
    app.add_url_rule("/editar/<hash>", "editar_sa", sociedad.guardarEdicion,methods=["POST"])
    app.add_url_rule("/evaluar_solicitudes", "evaluar_solicitudes", sociedad.evaluar_solicitudes,methods=["GET"])
    app.add_url_rule("/evaluar_estatutos", "evaluar_estatutos", sociedad.evaluar_estatutos,methods=["GET"])
    app.add_url_rule("/rechazar_solicitud", "rechazar_solicitud", sociedad.rechazar_solicitud,methods=["POST"])
    app.add_url_rule("/aceptar_solicitud", "aceptar_solicitud", sociedad.aceptar_solicitud,methods=["POST"])
    app.add_url_rule("/rechazar_solicitud_estatuto", "rechazar_solicitud_estatuto", sociedad.rechazar_estatuto,methods=["POST"])
    app.add_url_rule("/aceptar_solicitud_estatuto", "aceptar_solicitud_estatuto", sociedad.aceptar_estatuto,methods=["POST"])
    app.add_url_rule("/sociedad", "vista_sociedad", sociedad.vista_sociedad,methods=["GET"])

    app.add_url_rule("/estatutos/<id>", "obtener_estatuto", sociedad.obtener_estatuo,methods=["GET"])
    app.add_url_rule("/generar-carpeta-virtual/<id>", "generar_carpeta_virtual", sociedad.generar_carpeta_virtual,methods=["GET"])
    app.add_url_rule("/sociedad/pdf/<id>", "obtener_pdf_sociedad", sociedad.obtener_pdf_sociedad,methods=["GET"])

    app.add_url_rule("/solicitud_estampillado", "estampillar", estampillado.estampillar,methods=["GET"])

    app.add_url_rule("/generar_qr/<id>", "generar_qr", qr.generar_qr,methods=["GET"])
    app.add_url_rule("/qr/<id>", "obtener_qr", qr.obtener_qr,methods=["GET"])

    app.add_url_rule("/generar_carpetas_fisicas", "generar_carpetas_fisicas", sociedad.generar_carpetas_fisicas,methods=["GET"])
    app.add_url_rule("/generar_carpeta_fisica", "generar_carpeta_fisica", sociedad.generar_carpeta_fisica,methods=["POST"])
    

    app.add_url_rule("/gerencia/estadisticas", "estadisticas", estadisticas.get_estadisticas_paises,methods=["GET"])
    app.add_url_rule("/gerencia/metricas", "metricas", estadisticas.get_metricas,methods=["GET"])

    return app

    
