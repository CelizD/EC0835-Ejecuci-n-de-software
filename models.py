# models.py
# En este archivo defino las tablas de la base de datos como clases de Python.
# Importo las cosas que voy a necesitar de SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from db import Base

# ----- TABLA DE USUARIOS -----
class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    # El email es único, no se pueden repetir correos
    email = Column(String, unique=True, index=True)
    # NUEVO: Este campo me sirve para el "soft delete". 
    # Si activo = True, el usuario se muestra. Si activo = False, está "eliminado".
    activo = Column(Boolean, default=True)

# ----- TABLA DE TAREAS -----
class Tarea(Base):
    __tablename__ = "tareas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    descripcion = Column(String)
    prioridad = Column(Integer)
    # Esta es la llave foránea que relaciona la tarea con un usuario
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    # NUEVO: También le pongo el campo activo a las tareas
    activo = Column(Boolean, default=True)