from app.db_sqlalchemy import db_sqlalchemy
from datetime import datetime


db = db_sqlalchemy
metadata= db.MetaData()

class Socio(db.Model):
    __tablename__ = 'socio'
    id = db.Column(db.Integer, primary_key=True)
    
    nombre = db.Column(db.String(255),nullable=True)
    apellido = db.Column(db.String(255),nullable=True)
    porcentaje = db.Column(db.Integer)
    apoderado = db.Column(db.Boolean)

    
    def __init__(self, nombre, apellido, porcentaje,apoderado):
        self.nombre = nombre
        self.apellido = apellido
        self.porcentaje = porcentaje
        self.apoderado = apoderado

    @staticmethod
    def all():
        return Socio.query.all()

    def save(self):
        db.session.add(self)
        db.session.commit()
        return True
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return True

    def __repr__(self):
        return '<Socio Object>'

    # --- Desarrollo de Activar/Desactivar Turno_Final ---

    def buscarTurno_FinalPorID(id):
        turno = Socio.query.filter_by(id=id).first()
        return turno
    # def buscarSociosDeSociedad(id):
        # turno = Socio.query.filter_by(id=id)
        # return turno