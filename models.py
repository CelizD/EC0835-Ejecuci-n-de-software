# models.py
# En este archivo defino las tablas de la base de datos como clases de Python.
# Cada clase se convierte en una tabla, y cada atributo en una columna.
# Importo las cosas que voy a necesitar de SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey
# Importo la clase Base que hice en db.py, de ahí van a heredar mis modelos
from db import Base

# ----- TABLA DE USUARIOS -----
# Esta clase representa la tabla "usuarios" en la base de datos.
# Hereda de Base para que SQLAlchemy sepa que es una tabla.
class Usuario(Base):
    # Así se va a llamar la tabla en SQLite. Por convención se pone en plural.
    __tablename__ = "usuarios"
    
    # El ID es la llave primaria. primary_key=True significa que identifica a cada usuario.
    # index=True lo pongo para que las búsquedas por ID sean más rápidas.
    id = Column(Integer, primary_key=True, index=True)
    
    # El nombre del usuario. También le puse index para búsquedas rápidas.
    nombre = Column(String, index=True)
    
    # El email. Le puse unique=True para que no se puedan repetir correos.
    # Eso fue lo que causó el error de "UNIQUE constraint failed" que ya arreglamos.
    email = Column(String, unique=True, index=True)

# ----- TABLA DE TAREAS -----
# Esta clase representa la tabla "tareas" en la base de datos.
# También hereda de Base.
class Tarea(Base):
    __tablename__ = "tareas"

    # El ID de la tarea, también es llave primaria.
    id = Column(Integer, primary_key=True, index=True)
    
    # El título de la tarea (ejemplo: "Hacer la tarea de programación")
    titulo = Column(String, index=True)
    
    # La descripción de la tarea, para poner más detalles.
    descripcion = Column(String)
    
    # La prioridad. La puse como número entero (1 = alta, 2 = media, 3 = baja, etc.)
    prioridad = Column(Integer)
    
    # Esta es la parte más importante: usuario_id es una llave foránea.
    # ForeignKey("usuarios.id") significa que este número tiene que coincidir 
    # con el ID de algún usuario que ya exista. Así relaciono tareas con usuarios.
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))