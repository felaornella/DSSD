from app.db_sqlalchemy import db_sqlalchemy
from datetime import datetime
from app.models.socio import Socio


db = db_sqlalchemy


association_table = db.Table('sociedad_tiene_socios', 
                                 db.Column('sociedad_id', db.Integer, db.ForeignKey('sociedad.id'), primary_key=True),
                                 db.Column('socio_id', db.Integer, db.ForeignKey('socio.id'), primary_key=True))
class Sociedad(db.Model):
    __tablename__ = 'sociedad'
    id = db.Column(db.Integer, primary_key=True)
    
    nombre = db.Column(db.String(255),nullable=True)
    fechaCreacion = db.Column(db.DateTime())
    domicilioLegal = db.Column(db.String(255),nullable=True)
    domicilioReal = db.Column(db.String(255),nullable=True)
    correoApoderado = db.Column(db.String(255),nullable=True)
    paises = db.Column(db.Text(),nullable=True)

    socios = db.relationship("Socio", secondary=association_table,lazy='subquery', backref=db.backref('sociedad', lazy=True))
    caseId=  db.Column(db.Integer(),nullable=True) 
    estado =  db.Column(db.String(255),nullable=True)                                   

    
    def __init__(self, nombre, fechaCreacion, domicilioLegal, domicilioReal, correoApoderado, paises,estado):
        self.nombre = nombre
        self.fechaCreacion = fechaCreacion
        self.domicilioLegal = domicilioLegal
        self.domicilioReal = domicilioReal
        self.correoApoderado = correoApoderado
        self.paises = paises
        self.estado = estado

    @staticmethod
    def all():
        return Sociedad.query.all()

    def save(self):
        db.session.add(self)
        db.session.commit()
        return True

    def __repr__(self):
        return '<Sociedad Object>'

    # --- Desarrollo de Activar/Desactivar Turno_Final ---

    def buscarSociedadPorId(id):
        turno = Sociedad.query.filter_by(id=id).first()
        return turno