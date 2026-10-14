# models.py

# Hola, yo soy principiante. Este archivo lo hice para definir las tablas de la base de datos.
# No entiendo todo de SQLAlchemy, pero aquí voy aprendiendo.
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from db import Base

# ----- TABLA DE USUARIOS -----
# Esta clase representa la tabla de usuarios. Yo la llamé Usuario y hereda de Base.
class Usuario(Base):
    __tablename__ = "usuarios"  # Aquí le digo a la base de datos cómo se llama la tabla.
    
    id = Column(Integer, primary_key=True, index=True)  # El id es la llave principal, me dijeron que es importante.
    nombre = Column(String, index=True)  # Aquí guardo el nombre del usuario.
    # El email es único, no se pueden repetir correos. Lo puse unique=True porque no quiero dos iguales.
    email = Column(String, unique=True, index=True)
    # NUEVO: Este campo me sirve para el "soft delete". 
    # Si activo = True, el usuario se muestra. Si activo = False, está "eliminado".
    # Yo no borro de verdad, solo lo marco como inactivo. Eso me lo explicaron y me pareció buena idea.
    activo = Column(Boolean, default=True)

# ----- TABLA DE TAREAS -----
# Esta otra clase es para las tareas. También hereda de Base.
class Tarea(Base):
    __tablename__ = "tareas"  # El nombre de la tabla en la base de datos.

    id = Column(Integer, primary_key=True, index=True)  # Llave principal de la tarea.
    titulo = Column(String, index=True)  # El título de la tarea.
    descripcion = Column(String)  # Aquí va la descripción, puede ser más larga.
    prioridad = Column(Integer)  # La prioridad la guardo como número. No sé si 1 es más importante, pero así lo hice.
    # Esta es la llave foránea que relaciona la tarea con un usuario. 
    # Me costó entender esto, pero creo que así la tarea sabe de quién es.
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    # NUEVO: También le pongo el campo activo a las tareas. 
    # Así puedo "eliminarlas" sin borrarlas de verdad.
    activo = Column(Boolean, default=True)