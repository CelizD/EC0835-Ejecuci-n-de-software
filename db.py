# db.py
# En este archivo configuro todo lo de la base de datos: la conexión y las sesiones.
# Aquí uso SQLAlchemy, que es la librería que me deja hablar con SQLite sin escribir SQL puro.
import os     # Lo necesito para armar rutas de archivos
import sys    # Lo necesito para saber si el programa corre como .exe o desde Python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ----- TRUCO PARA EL .EXE -----
# Esto lo puse porque cuando convertí el programa a .exe con PyInstaller, 
# la base de datos se creaba en una carpeta temporal y se borraba al cerrar.
# Con esto, la base de datos siempre se crea junto al programa.

# getattr(sys, 'frozen', False) me dice si el programa está "congelado" (o sea, si es un .exe)
if getattr(sys, 'frozen', False):
    # Si ya es .exe, uso la carpeta donde está el ejecutable
    ruta_base = os.path.dirname(sys.executable)
else:
    # Si estoy en VS Code, uso la carpeta donde está este archivo .py
    ruta_base = os.path.dirname(os.path.abspath(__file__))

# Armo la ruta completa donde va a vivir la base de datos (se llamará "sistema.db")
ruta_db = os.path.join(ruta_base, "sistema.db")

# SQLAlchemy necesita la ruta con este formato raro de "sqlite:///..."
SQLALCHEMY_DATABASE_URL = f"sqlite:///{ruta_db}"

# ----- EL ENGINE -----
# El engine es el que hace la magia de conectarse a la base de datos.
# El connect_args={"check_same_thread": False} lo puse porque Tkinter se trababa 
# si no lo ponía. Es un truco que encontré en internet.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# ----- LA FÁBRICA DE SESIONES -----
# SessionLocal es como una "fábrica" que me da una sesión nueva cada vez que la pido.
# Cada sesión es como una conversación con la base de datos.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base es la clase padre de la que van a heredar mis modelos (Usuario y Tarea).
# Básicamente le dice a SQLAlchemy que mis clases van a ser tablas.
Base = declarative_base()

# ----- LA FUNCIÓN QUE ME DA UNA SESIÓN -----
# Esta función la hago para poder pedir una sesión desde otros archivos.
def get_db():
    db = SessionLocal()   # Creo una sesión nueva
    try:
        return db         # La regreso para que la usen
    finally:
        pass  # Aquí antes cerraba la sesión, pero la cerré manualmente desde main.py
              # porque si la cerraba aquí, ya no podía usarla después.