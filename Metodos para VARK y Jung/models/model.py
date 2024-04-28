from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Patrón Singleton para la conexión a la base de datos
class Database:
    __instance = None

    @staticmethod
    def get_instance():
        if Database.__instance is None:
            Database()
        return Database.__instance

    def __init__(self):
        if Database.__instance is not None:
            raise Exception("This class is a Singleton!")
        else:
            Database.__instance = self
            # Conexión a la base de datos MySQL usando PyMySQL
            self.engine = create_engine('mysql+pymysql://root:123456@localhost/a12')
            self.Base = declarative_base()
            self.Session = sessionmaker(bind=self.engine)
            self.session = self.Session()

    def get_session(self):
        return self.session

Base = declarative_base()

# Definición de las tablas
class Puesto(Base):
    __tablename__ = 'puestos'
    idpuestos = Column(Integer, primary_key=True, autoincrement=True)
    puesto = Column(String(100), nullable=False)

class Perfil(Base):
    __tablename__ = 'perfil'
    id_perfil = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    apellidoPaterno = Column(String(100), nullable=False)
    apellidoMaterno = Column(String(100), nullable=False)
    telefono = Column(String(100), nullable=False)
    correo_electronico = Column(String(100), nullable=False)
    id_puesto = Column(Integer, ForeignKey('puestos.idpuestos'))
    puesto = relationship("Puesto")
    resultado_vark = relationship("ResultadoVark", uselist=False)
    respuestas_vark = relationship("RespuestaVark")

class Pregunta(Base):
    __tablename__ = 'preguntas'
    id_pregunta = Column(Integer, primary_key=True, autoincrement=True)
    enunciado = Column(String(255), nullable=False)
    opciones = relationship("OpcionRespuesta", back_populates="pregunta")

class OpcionRespuesta(Base):
    __tablename__ = 'opciones_respuesta'
    id_opcion = Column(Integer, primary_key=True, autoincrement=True)
    id_pregunta = Column(Integer, ForeignKey('preguntas.id_pregunta'))
    opcion = Column(CHAR(1), nullable=False)
    respuesta_texto = Column(String(255), nullable=False)
    pregunta = relationship("Pregunta", back_populates="opciones")

class RespuestaVark(Base):
    __tablename__ = 'respuestas_vark'
    id_respuesta = Column(Integer, primary_key=True, autoincrement=True)
    id_persona = Column(Integer, ForeignKey('perfil.id_perfil'))
    id_pregunta = Column(Integer, ForeignKey('preguntas.id_pregunta'))
    respuesta = Column(CHAR(1), nullable=False)
    perfil = relationship("Perfil")
    pregunta = relationship("Pregunta")

class ResultadoVark(Base):
    __tablename__ = 'resultado_vark'
    id_resultado = Column(Integer, primary_key=True, autoincrement=True)
    id_persona = Column(Integer, ForeignKey('perfil.id_perfil'))
    V = Column(Integer, nullable=False)
    A = Column(Integer, nullable=False)
    R = Column(Integer, nullable=False)
    K = Column(Integer, nullable=False)
    perfil = relationship("Perfil")

class Seccion(Base):
    __tablename__ = 'secciones'
    id_seccion = Column(Integer, primary_key=True, autoincrement=True)
    nombre_seccion = Column(String(255), nullable=False)

class PreguntasJung(Base):
    __tablename__ = 'preguntas_jung'
    id_pregunta = Column(Integer, primary_key=True, autoincrement=True)
    pregunta = Column(String(255), nullable=False)
    id_seccion = Column(Integer, ForeignKey('secciones.id_seccion'))
    seccion = relationship("Seccion")

class PuntosTotalesSeccion(Base):
    __tablename__ = 'puntos_totales_seccion'
    id_puntos_totales_seccion = Column(Integer, primary_key=True, autoincrement=True)
    id_perfil = Column(Integer, ForeignKey('perfil.id_perfil'))
    id_seccion = Column(Integer, ForeignKey('secciones.id_seccion'))
    puntos_totales = Column(Integer, nullable=False)
    perfil = relationship("Perfil")
    seccion = relationship("Seccion")

class Respuesta(Base):
    __tablename__ = 'respuestas'
    id_respuestas = Column(Integer, primary_key=True, autoincrement=True)
    id_perfil = Column(Integer, ForeignKey('perfil.id_perfil'))
    id_pregunta = Column(Integer, ForeignKey('preguntas_jung.id_pregunta'))
    respuesta = Column(Integer, nullable=False)
    perfil = relationship("Perfil")
    pregunta_jung = relationship("PreguntasJung")

class ComparacionSecciones(Base):
    __tablename__ = 'comparacion_secciones'
    id_comparacion = Column(Integer, primary_key=True, autoincrement=True)
    id_perfil = Column(Integer, ForeignKey('perfil.id_perfil'))
    seccion_mayor = Column(String(105), nullable=False)
    puntos_seccion_mayor = Column(Integer, nullable=False)
    perfil = relationship("Perfil")

class CategoriaPerfil(Base):
    __tablename__ = 'categoria_perfil'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_perfil = Column(Integer, ForeignKey('perfil.id_perfil'))
    categoria = Column(String(105), nullable=False)
    perfil = relationship("Perfil")
