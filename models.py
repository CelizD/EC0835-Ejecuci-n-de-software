
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from db import Base

# TABLA DE USUARIOS 
# Defino el modelo Usuario, encargado de representar la tabla de usuarios en la base de datos.
class Usuario(Base):
    __tablename__ = "usuarios"  # Establezco el nombre de la tabla en la base de datos.
    
    id = Column(Integer, primary_key=True, index=True)  # Defino el identificador principal de cada usuario.
    nombre = Column(String, index=True)  # Almaceno el nombre del usuario.
    # Establezco el correo electrónico como un campo único para evitar registros duplicados.
    email = Column(String, unique=True, index=True)
    # Almaceno la contraseña utilizada para autenticar al usuario en el sistema.
    # Establezco un valor predeterminado para mantener la compatibilidad con registros anteriores.
    password = Column(String, default="1234")
    # Utilizo este campo para implementar la eliminación lógica de los usuarios.
    # Cuando está activo, el registro permanece disponible; cuando está inactivo, se considera eliminado.
    activo = Column(Boolean, default=True)

# TABLA DE TAREAS 
# Defino el modelo Tarea, encargado de almacenar la información de las tareas registradas.
class Tarea(Base):
    __tablename__ = "tareas"  # Establezco el nombre de la tabla correspondiente.

    id = Column(Integer, primary_key=True, index=True)  # Defino el identificador principal de cada tarea.
    titulo = Column(String, index=True)  # Almaceno el título de la tarea.
    descripcion = Column(String)  # Guardo la descripción y los detalles de cada tarea.
    prioridad = Column(Integer)  # Almaceno el nivel de prioridad mediante un valor entero.
    # Establezco la relación entre las tareas y los usuarios mediante una llave foránea.
    # Este campo permite identificar al usuario al que pertenece cada tarea.
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    # Implemento la eliminación lógica para conservar los registros de tareas.
    # Este campo permite identificar si una tarea continúa activa o ha sido desactivada.
    activo = Column(Boolean, default=True)
