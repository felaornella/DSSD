from app.db_sqlalchemy import db_sqlalchemy
from datetime import datetime


db = db_sqlalchemy
metadata= db.MetaData()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    
    nombre = db.Column(db.String(45),nullable=True)
    apellido = db.Column(db.String(45),nullable=True)
    email = db.Column(db.String(255),nullable=True)
    password = db.Column(db.String(255),nullable=True)
    dni = db.Column(db.String(45),nullable=True)

    
    def __init__(self, nombre, apellido, email,password,dni):
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.password = password
        self.dni = dni


    @staticmethod
    def all():
        return Usuario.query.all()

    def save(self):
        db.session.add(self)
        db.session.commit()
        return True

    def __repr__(self):
        return '<Usuario Object>'

    # --- Desarrollo de Activar/Desactivar Turno_Final ---

    def buscarTurno_FinalPorID(id):
        turno = Usuario.query.filter_by(id=id).first()
        return turno

    def autenticar(email, psw):
        usu = Usuario.query.filter_by(email=email, password=psw).first()
        if usu is None:
            return None
        if usu is not None:
            return usu
        else:
            return None

    def crearNuevo(email, pwd, nombre, apellido, dni):
        busqueda = Usuario.query.filter_by(email=email).all()
        if len(busqueda) == 0:
            usu = Usuario(nombre,apellido,email,pwd,dni)
            usu.save()
            return usu
        else:
            return None