from app.db_sqlalchemy import db_sqlalchemy
from datetime import datetime
from app.models.socio import Socio


db = db_sqlalchemy
metadata= db.MetaData()

class Sociedad(db.Model):
    __tablename__ = 'sociedad'
    id = db.Column(db.Integer, primary_key=True)
    
    nombre = db.Column(db.String(255),nullable=True)
    fechaCreacion = db.Column(db.DateTime())
    domicilioLegal = db.Column(db.String(255),nullable=True)
    domicilioReal = db.Column(db.String(255),nullable=True)
    correoApoderado = db.Column(db.String(255),nullable=True)
    paises = db.Column(db.Text(),nullable=True)

    association_table = db.Table('sociedad_tiene_socios', metadata,
                                 db.Column('sociedad_id', db.Integer, db.ForeignKey(id)),
                                 db.Column('socio_id', db.Integer, db.ForeignKey(id)))
    
    socios = db.relationship("Socio", secondary=association_table,
                                            primaryjoin=id==association_table.c.sociedad_id,
                                            secondaryjoin=id==association_table.c.socio_id)
                                            

    
    def __init__(self, nombre, fechaCreacion, domicilioLegal, domicilioReal, correoApoderado, paises):
        self.nombre = nombre
        self.fechaCreacion = fechaCreacion
        self.domicilioLegal = domicilioLegal
        self.domicilioReal = domicilioReal
        self.correoApoderado = correoApoderado
        self.paises = paises

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

    def buscarTurno_FinalPorID(id):
        turno = Sociedad.query.filter_by(id=id).first()
        return turno